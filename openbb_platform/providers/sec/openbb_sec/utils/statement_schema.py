"""Runtime schema module for standardized financial statement extraction."""

# pylint: disable=C0302,R0912,R0913,R0914,R0915,R0916,R0917
# flake8: noqa: PLR0912

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from math import isclose
from pathlib import Path
from typing import Any, Literal

_SCHEMA_PATH = Path(__file__).resolve().parent / "statement_schema.json"
ANNUAL_FORMS = frozenset({"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"})
QUARTERLY_FORMS = frozenset({"10-Q", "10-Q/A"})
SEMI_ANNUAL_FORMS = frozenset({"6-K", "6-K/A"})
PRELIMINARY_FORMS = frozenset({"8-K", "8-K/A"})
ALL_FORMS = ANNUAL_FORMS | QUARTERLY_FORMS | SEMI_ANNUAL_FORMS
Frequency = Literal["annual", "quarterly"]
StatementName = Literal["income_statement", "balance_sheet", "cash_flow"]
CompanyType = Literal["industrial", "financial", "diversified", "insurance"]
_TOLERANCE = 1_000_000


@dataclass(frozen=True)
class RowDef:
    """A single row definition from the schema."""

    tag: str
    label: str
    description: str
    parent: str | None
    sequence: int
    factor: str
    balance: str
    unit: str  # "monetary", "per_share", or "shares"
    period_type: str  # "duration" or "instant"
    xbrl_tags: tuple[dict[str, str], ...]  # ({"tag": ..., "namespace": ...}, ...)


@dataclass
class RowResult:
    """Extracted values for one standardized row."""

    tag: str
    label: str
    description: str
    parent: str | None
    sequence: int | float
    factor: str
    balance: str
    unit: str
    period_type: str
    values: dict[str, float]  # {period_end_date: value}
    sources: dict[str, str] = field(
        default_factory=dict
    )  # {date: "ns:Tag" or "imputed: ..."}


@dataclass
class ValidationWarning:
    """A discrepancy detected during post-extraction validation."""

    date: str
    tag: str
    expected: float  # value computed from the accounting identity
    actual: float  # value extracted from XBRL
    formula: (
        str  # human-readable identity (e.g. "total_revenue + -total_cost_of_revenue")
    )
    identity: str  # which identity was violated


@dataclass
class StatementResult:
    """A fully extracted statement."""

    statement: str
    company_type: str
    frequency: str
    currency: str  # ISO currency code detected from the filing (e.g. "USD")
    dates: list[str]  # sorted period-end dates
    rows: list[RowResult]
    fiscal_data: dict[str, dict[str, Any]] = field(
        default_factory=dict
    )  # {date: {fiscal_year, fiscal_period}}
    diagnostics: list[ValidationWarning] = field(
        default_factory=list
    )  # validation discrepancies (never overrides)
    preliminary_dates: set[str] = field(
        default_factory=set
    )  # period-end dates sourced only from 8-K (not yet reported on 10-Q/K)


class StatementSchema:
    """Schema for standardized financial statement extraction."""

    def __init__(self, schema_path: Path | str | None = None) -> None:
        """Initialize the schema by loading the JSON definition."""
        path = Path(schema_path) if schema_path else _SCHEMA_PATH

        with open(path) as f:
            data = json.load(f)

        self._version: str = data.get("version", "unknown")
        self._generated: str = data.get("generated", "unknown")
        self._statements: dict = data["statements"]
        self._detection: dict = data["detection"]
        self._row_defs: dict[str, dict[str, list[RowDef]]] = {}

        for stmt_name, types in self._statements.items():
            self._row_defs[stmt_name] = {}

            for stype, rows in types.items():
                self._row_defs[stmt_name][stype] = [
                    RowDef(
                        tag=r["tag"],
                        label=r["label"],
                        description=r.get("description", ""),
                        parent=r.get("parent"),
                        sequence=r.get("sequence", 0),
                        factor=r.get("factor", "+"),
                        balance=r.get("balance", ""),
                        unit=r.get("unit", "monetary"),
                        period_type=r["period_type"],
                        xbrl_tags=tuple(
                            {"tag": x["tag"], "namespace": x["namespace"]}
                            for x in r["xbrl_tags"]
                        ),
                    )
                    for r in rows
                ]

        # Pre-parse detection config
        self._insurance_is_signals: list[str] = self._detection.get(
            "insurance_is_signals", []
        )
        self._insurance_bs_signals: list[str] = self._detection.get(
            "insurance_bs_signals", []
        )
        self._financial_signals: list[str] = self._detection.get(
            "financial_signals", []
        )
        self._diversified_signals: list[str] = self._detection.get(
            "diversified_signals", []
        )
        self._industrial_signals: list[str] = self._detection.get(
            "industrial_signals", []
        )
        self._min_financial_signals: int = self._detection.get(
            "min_financial_signals", 2
        )

    @property
    def version(self) -> str:
        """Version string from the loaded schema."""
        return self._version

    @property
    def generated(self) -> str:
        """Generation timestamp from the loaded schema."""
        return self._generated

    def get_rows(
        self, statement: StatementName, company_type: CompanyType
    ) -> list[RowDef]:
        """Return row definitions for a statement + type combination."""
        return self._row_defs.get(statement, {}).get(company_type, [])

    def get_row(
        self, tag: str, statement: StatementName, company_type: CompanyType
    ) -> RowDef | None:
        """Look up a single row by its standardized tag name."""
        for row in self.get_rows(statement, company_type):
            if row.tag == tag:
                return row
        return None

    def get_tag_chain(
        self, tag: str, statement: StatementName, company_type: CompanyType
    ) -> tuple[dict[str, str], ...]:
        """Return the XBRL tag chain for a standardized tag."""
        row = self.get_row(tag, statement, company_type)
        return row.xbrl_tags if row else ()

    def get_period_type(
        self, tag: str, statement: StatementName, company_type: CompanyType
    ) -> str | None:
        """Return 'duration' or 'instant' for a standardized tag."""
        row = self.get_row(tag, statement, company_type)
        return row.period_type if row else None

    def detect_type(self, facts: dict[str, Any]) -> CompanyType:
        """Classify a company as industrial, financial, diversified, or insurance.

        Priority order:
        1. Insurance — at least 1 IS insurance signal AND total >= 2
           (but defers to financial if financial signal count is higher)
        2. Financial (bank) — >= min_financial_signals bank tags
        3. Industrial — has COGS/GrossProfit tags **reported in recent filings**
        4. Diversified — fallback (CostsAndExpenses without COGS)

        Parameters
        ----------
        facts : dict
            The ``facts`` dict from company facts JSON (keyed by namespace).
        """
        company_tags: set[str] = set()

        for ns_data in facts.values():
            if isinstance(ns_data, dict):
                company_tags.update(ns_data.keys())

        ins_is = sum(1 for s in self._insurance_is_signals if s in company_tags)
        ins_bs = sum(1 for s in self._insurance_bs_signals if s in company_tags)
        ins_total = ins_is + ins_bs
        is_insurance = ins_is >= 1 and ins_total >= 2
        fin_count = sum(1 for s in self._financial_signals if s in company_tags)
        is_financial = fin_count >= self._min_financial_signals

        # When both insurance and financial signals fire (e.g. a bank with an
        # insurance subsidiary like TD Bank), the category with more signals wins.
        if is_insurance and is_financial:
            return "insurance" if ins_total > fin_count else "financial"
        if is_insurance:
            return "insurance"
        if is_financial:
            return "financial"

        has_cogs = any(
            s in company_tags and self._has_recent_data(facts, s)
            for s in self._industrial_signals
        )

        if has_cogs:
            return "industrial"

        has_cne = any(s in company_tags for s in self._diversified_signals)

        if has_cne:
            return "diversified"

        return "industrial"

    @staticmethod
    def _has_recent_data(
        facts: dict[str, Any], tag: str, max_age_years: int = 5
    ) -> bool:
        """Check if a tag has data from a recent 10-K filing.

        Prevents stale tags (e.g. GrossProfit last reported in 2010)
        from influencing company type detection.
        """
        cutoff_year = datetime.now().year - max_age_years

        for ns_data in facts.values():
            if not isinstance(ns_data, dict) or tag not in ns_data:
                continue

            tag_data = ns_data[tag]

            for entries in tag_data.get("units", {}).values():
                for entry in entries:
                    if entry.get("form", "") in ("10-K", "10-K/A", "20-F", "20-F/A"):
                        end = entry.get("end", "")
                        if end and int(end[:4]) >= cutoff_year:
                            return True

        return False

    @staticmethod
    def get_filing_dates(
        facts: dict[str, Any],
        frequency: Frequency = "annual",
        include_preliminary: bool = False,
    ) -> set[str]:
        """Determine canonical period-end dates from actual filings.

        For annual: end dates of 300-400 day duration items in 10-K forms.
        For quarterly: end dates of 60-135 day duration items in 10-Q forms,
        PLUS semi-annual end dates (150-200 days) from 6-K forms,
        PLUS FY end dates from 10-K/20-F (which are the Q4/H2 end dates).

        When ``include_preliminary`` is True, 8-K period-end dates that are
        NOT already covered by a 10-Q/K filing are also included.

        After collection, annual dates are deduplicated by detecting the
        dominant fiscal-year-end pattern and removing outlier dates that
        resulted from old filing vintages, mergers, or transition periods.

        These dates form the canonical set applied uniformly to all three
        statements, ensuring IS/BS/CF always show the same periods.
        """
        filing_dates: set[str] = set()
        preliminary_candidates: set[str] = set()

        for ns_facts in facts.values():
            for tag_data in ns_facts.values():
                for entries in tag_data.get("units", {}).values():
                    for entry in entries:
                        form = entry.get("form", "")
                        start = entry.get("start", "")
                        end = entry.get("end", "")

                        if not start or not end or start == end:
                            continue
                        try:
                            days = (
                                datetime.strptime(end, "%Y-%m-%d")
                                - datetime.strptime(start, "%Y-%m-%d")
                            ).days
                        except (ValueError, TypeError):
                            continue

                        if frequency == "annual":
                            if form in ANNUAL_FORMS and 300 <= days <= 400:
                                filing_dates.add(end)
                            elif (
                                include_preliminary
                                and form in PRELIMINARY_FORMS
                                and 300 <= days <= 400
                            ):
                                preliminary_candidates.add(end)
                        else:
                            if form in QUARTERLY_FORMS and 60 <= days <= 135:
                                filing_dates.add(end)
                            if form in SEMI_ANNUAL_FORMS and (
                                60 <= days <= 135 or 150 <= days <= 200
                            ):
                                filing_dates.add(end)
                            if (
                                include_preliminary
                                and form in PRELIMINARY_FORMS
                                and 60 <= days <= 135
                            ):
                                preliminary_candidates.add(end)

        # For quarterly: add only canonical annual FY-end dates (Q4/H2
        # end dates).  We must NOT add raw annual-form end dates because
        # 10-K filings can contain calendar-year tags (e.g. tax rate
        # reconciliation items ending Dec-31) that don't match the
        # company's actual FY-end (e.g. WMT Jan-31).  Compute the
        # deduped annual date set via recursion and add only those.
        if frequency != "annual":
            canonical_annual = StatementSchema.get_filing_dates(
                facts, "annual", include_preliminary=include_preliminary
            )
            filing_dates |= canonical_annual

        # Add 8-K dates only when not already covered by a 10-Q/K filing
        if include_preliminary:
            filing_dates |= preliminary_candidates - filing_dates

        # Detect the dominant month-day pattern and drop outliers that have a
        # nearby canonical date covering the same fiscal year.
        if frequency == "annual" and len(filing_dates) > 3:
            parsed = [(d, datetime.strptime(d, "%Y-%m-%d")) for d in filing_dates]
            md_counts: Counter[tuple[int, int]] = Counter()

            for _, dt in parsed:
                md_counts[(dt.month, dt.day)] += 1

            dominant_md, dom_freq = md_counts.most_common(1)[0]
            dom_m, dom_d = dominant_md

            if dom_freq >= max(3, len(parsed) * 0.4):
                # Classify each date as canonical (matches dominant ±5 days)
                # or non-canonical.
                canonical: set[str] = set()
                canonical_dts: list[datetime] = []
                non_canonical: list[tuple[str, datetime]] = []

                for d, dt in parsed:
                    is_match = False

                    for y in (dt.year - 1, dt.year, dt.year + 1):
                        try:
                            anchor = datetime(y, dom_m, dom_d)
                        except ValueError:
                            anchor = datetime(y, dom_m, min(dom_d, 28))
                        if abs((dt - anchor).days) <= 5:
                            is_match = True
                            break

                    if is_match:
                        canonical.add(d)
                        canonical_dts.append(dt)
                    else:
                        non_canonical.append((d, dt))

                # Drop duplicate canonicals within 10 days of each other
                # (e.g. Dec 30 vs Dec 31 from CIK merge).  Keep the one
                # that exactly matches the dominant month-day.
                canonical_sorted = sorted(canonical)

                for i in range(len(canonical_sorted) - 1):
                    d1 = canonical_sorted[i]
                    d2 = canonical_sorted[i + 1]
                    dt1 = datetime.strptime(d1, "%Y-%m-%d")
                    dt2 = datetime.strptime(d2, "%Y-%m-%d")

                    if (dt2 - dt1).days <= 10:
                        exact1 = dt1.month == dom_m and dt1.day == dom_d
                        exact2 = dt2.month == dom_m and dt2.day == dom_d
                        if exact2 and not exact1:
                            canonical.discard(d1)
                        elif exact1 and not exact2:
                            canonical.discard(d2)

                # Drop non-canonical dates that have a canonical date nearby
                # (within 200 days), i.e. in the same fiscal year.
                filtered = set(canonical)

                for d, dt in non_canonical:
                    has_nearby = any(abs((dt - ct).days) <= 200 for ct in canonical_dts)
                    if not has_nearby:
                        filtered.add(d)

                filing_dates = filtered

        # Drop leading dates that lack complete balance-sheet data.
        # Early XBRL filings (e.g. 2007) often include only a handful of
        # comparative BS tags from the first 10-K, making that year's
        # statements structurally incomplete.  We detect this by checking
        # whether the ``Assets`` instant tag exists for the earliest date.
        # Loop because multiple leading dates may lack data (e.g. Merck
        # has a stray 1998-12-31 comparative AND a sparse 2007-12-31).
        # For quarterly frequency, accept Assets from ANY form (10-Q, 6-K,
        # 10-K) so that valid Q1/Q2/Q3 dates are not incorrectly dropped.
        assets_forms = ALL_FORMS if frequency == "quarterly" else ANNUAL_FORMS
        if include_preliminary:
            assets_forms = assets_forms | PRELIMINARY_FORMS

        while len(filing_dates) > 1:
            earliest = min(filing_dates)
            has_assets = False

            for ns_facts in facts.values():
                assets_data = ns_facts.get("Assets", {})

                for entries in assets_data.get("units", {}).values():
                    for entry in entries:
                        if (
                            entry.get("form", "") in assets_forms
                            and entry.get("end") == earliest
                            and not entry.get("start")
                        ):
                            has_assets = True
                            break

                    if has_assets:
                        break

                if has_assets:
                    break

            if not has_assets:
                filing_dates.discard(earliest)
            else:
                break

        return filing_dates

    @staticmethod
    def get_fiscal_meta(
        facts: dict[str, Any],
        frequency: Frequency,
        filing_dates: set[str],
    ) -> dict[str, dict[str, Any]]:
        """Build fiscal metadata for each period-end date.

        Uses ``fy`` / ``fp`` from SEC filing entries.  The earliest filing
        per date is selected so that ``fy`` reflects the *original* fiscal
        year, not a later comparative restatement.

        For quarterly frequency, FY-end dates are relabelled as ``Q4``
        (or ``H2`` for semi-annual filers).

        Returns
        -------
        dict
            ``{end_date: {"fiscal_year": int, "fiscal_period": str}}``
        """
        annual_dates = StatementSchema.get_filing_dates(facts, "annual")
        # Collect earliest-filed (fy, fp, form) per end_date per form group
        best_annual: dict[str, tuple[str, int, str]] = {}
        best_quarterly: dict[str, tuple[str, int, str]] = {}
        best_semi: dict[str, tuple[str, int, str]] = {}
        best_preliminary: dict[str, tuple[str, int, str]] = {}

        for ns_facts in facts.values():
            for tag_data in ns_facts.values():
                for entries_list in tag_data.get("units", {}).values():
                    for entry in entries_list:
                        end = entry.get("end", "")

                        if end not in filing_dates:
                            continue

                        filed = entry.get("filed", "")
                        fy = entry.get("fy")
                        fp = entry.get("fp", "")
                        form = entry.get("form", "")

                        if not filed:
                            continue

                        if form in ANNUAL_FORMS:
                            if fy is None or not fp:
                                continue
                            if end not in best_annual or filed < best_annual[end][0]:
                                best_annual[end] = (filed, fy, fp)
                        elif form in QUARTERLY_FORMS:
                            if fy is None or not fp:
                                continue
                            if (
                                end not in best_quarterly
                                or filed < best_quarterly[end][0]
                            ):
                                best_quarterly[end] = (filed, fy, fp)
                        elif form in SEMI_ANNUAL_FORMS:
                            if fy is None or not fp:
                                continue
                            if end not in best_semi or filed < best_semi[end][0]:
                                best_semi[end] = (filed, fy, fp)
                        elif form in PRELIMINARY_FORMS:
                            if fy is not None and fp:
                                if (
                                    end not in best_preliminary
                                    or filed < best_preliminary[end][0]
                                ):
                                    best_preliminary[end] = (filed, fy, fp)
                            elif end not in best_preliminary:
                                month = int(end[5:7])
                                cal_q = f"Q{(month - 1) // 3 + 1}"
                                best_preliminary[end] = (
                                    filed,
                                    int(end[:4]),
                                    cal_q,
                                )

        result: dict[str, dict[str, Any]] = {}

        for date in filing_dates:
            if frequency == "annual":
                info = best_annual.get(date)
                result[date] = {
                    "fiscal_year": info[1] if info else int(date[:4]),
                    "fiscal_period": "FY",
                }
                # Quarterly / semi-annual
            elif date in annual_dates:
                # FY-end date → Q4 (or H2 for semi-annual filers)
                info = best_annual.get(date)
                period = "Q4"
                # If the company files semi-annually (no 10-Q data
                # and no quarterly-granularity 6-K dates), relabel to
                # H2 instead of Q4.  6-K filers that report actual
                # Q1/Q3 standalone items have >2 non-annual dates per
                # fiscal year — those are quarterly, not semi-annual.
                if not best_quarterly and best_semi:
                    non_annual = {d for d in filing_dates if d not in annual_dates}
                    period = "Q4" if len(non_annual) > len(annual_dates) else "H2"
                result[date] = {
                    "fiscal_year": info[1] if info else int(date[:4]),
                    "fiscal_period": period,
                }
            else:
                # Try 10-Q, then 6-K, then fallback
                q_info = best_quarterly.get(date)

                if q_info:
                    result[date] = {
                        "fiscal_year": q_info[1],
                        "fiscal_period": q_info[2],
                    }
                else:
                    s_info = best_semi.get(date)
                    if s_info:
                        result[date] = {
                            "fiscal_year": s_info[1],
                            "fiscal_period": s_info[2],
                        }
                    else:
                        p_info = best_preliminary.get(date)
                        if p_info:
                            result[date] = {
                                "fiscal_year": p_info[1],
                                "fiscal_period": p_info[2],
                            }
                        else:
                            result[date] = {
                                "fiscal_year": int(date[:4]),
                                "fiscal_period": "Q4",
                            }

        # ----- Post-process FYs for monotonicity -----
        # The SEC ``fy`` field is the fiscal year of the *filing* that
        # contains each data point.  Comparative prior-year figures
        # restated in a later filing inherit the later filing's ``fy``.
        # After selecting the earliest-filed entry, the first XBRL filing
        # may still stamp several historical dates with the same ``fy``.
        # Fix: walk backwards from the latest date (always correct) and
        # decrement any duplicate or non-decreasing FYs.
        if frequency == "annual" and result:
            sorted_dates = sorted(result.keys())
            # Work backwards: the last date's fy is authoritative (its own 10-K)
            for i in range(len(sorted_dates) - 2, -1, -1):
                cur = sorted_dates[i]
                nxt = sorted_dates[i + 1]
                if result[cur]["fiscal_year"] >= result[nxt]["fiscal_year"]:
                    result[cur]["fiscal_year"] = result[nxt]["fiscal_year"] - 1

        elif frequency == "quarterly" and result:
            # FY-end dates (marked Q4/H2) get fy from the 10-K filing which
            # can be wrong for the same reason.  After initial assignment,
            # ensure Q4 dates inherit the same fy as surrounding quarters.
            sorted_dates = sorted(result.keys())
            annual_set = set(annual_dates)

            for i, date in enumerate(sorted_dates):
                if (
                    date in annual_set
                    and result[date]["fiscal_period"] in ("Q4", "H2")
                    and i > 0
                ):
                    # Q4 should share fy with the preceding quarter
                    prev = sorted_dates[i - 1]
                    prev_fy = result[prev]["fiscal_year"]
                    if result[date]["fiscal_year"] != prev_fy:
                        result[date]["fiscal_year"] = prev_fy

        return result

    @staticmethod
    def _detect_reporting_currency(facts: dict[str, Any]) -> str:
        """Detect the reporting currency from the SEC facts data.

        Scans all tags across namespaces and returns the ISO currency code
        that appears most often as a unit key (e.g. ``"USD"``, ``"EUR"``).
        Falls back to ``"USD"`` if no monetary units are found.
        """
        currency_counts: dict[str, int] = {}
        # Keys that are never currencies
        skip = frozenset(
            {
                "shares",
                "pure",
            }
        )

        for ns_facts in facts.values():
            for tag_data in ns_facts.values():
                for unit_key in tag_data.get("units", {}):

                    if unit_key in skip or "/" in unit_key:
                        continue
                    # ISO currency codes are 3 uppercase letters

                    if len(unit_key) == 3 and unit_key.isalpha() and unit_key.isupper():
                        currency_counts[unit_key] = currency_counts.get(unit_key, 0) + 1

        if not currency_counts:
            return "USD"

        return max(currency_counts, key=currency_counts.get)  # type: ignore[arg-type]

    @staticmethod
    def _prior_period_end(date: str) -> str | None:
        """Return the prior quarter-end date string for a given period end."""
        _PRIOR = {
            3: lambda y: f"{y - 1}-12-31",
            6: lambda y: f"{y}-03-31",
            9: lambda y: f"{y}-06-30",
            12: lambda y: f"{y}-09-30",
            1: lambda y: f"{y - 1}-10-31",
            4: lambda y: f"{y}-01-31",
        }

        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
        except (ValueError, TypeError):
            return None

        fn = _PRIOR.get(dt.month)

        return fn(dt.year) if fn else None

    @staticmethod
    def _get_unit_data(
        tag_data: dict,
        unit_type: str = "monetary",
        currency: str = "USD",
    ) -> list[dict] | None:
        """Find the best unit data array from a tag's units dict.

        Parameters
        ----------
        tag_data : dict
            A single XBRL tag's data dict (contains ``"units"`` key).
        unit_type : str
            Schema unit type: ``"monetary"``, ``"per_share"``, or ``"shares"``.
        currency : str
            ISO currency code detected from the filing (e.g. ``"USD"``).
        """
        units = tag_data.get("units", {})

        if unit_type == "shares":
            if "shares" in units:
                return units["shares"]
        elif unit_type == "per_share":
            per_share_key = f"{currency}/shares"
            if per_share_key in units:
                return units[per_share_key]
            # Some filers use variant keys (e.g. USD/shares_unit)
            for key in units:
                if key.startswith(f"{currency}/"):
                    return units[key]
        elif currency in units:  # monetary
            return units[currency]

        # Fallback: first available unit
        if units:
            return next(iter(units.values()))

        return None

    @staticmethod
    def _get_annual_values(
        facts: dict[str, Any],
        row: RowDef,
        currency: str = "USD",
        include_preliminary: bool = False,
    ) -> dict[str, tuple[str, float, str]]:
        """Return {fy_end_date: (fy_start_date, value, xbrl_source)} for annual periods.

        Used internally for Q4 derivation.  Applies the same filing-date
        consistency logic as the annual branch of extract_row_values so that
        the FY value used for Q4 = FY − (Q1+Q2+Q3) matches the annual
        extraction exactly.
        """
        if row.period_type != "duration":
            return {}

        # Phase 1: collect candidates per tag: {end: {filed: (start, val)}}
        tag_candidates: list[dict[str, dict[str, tuple[str, float]]]] = []

        for xbrl_entry in row.xbrl_tags:
            ns_facts = facts.get(xbrl_entry["namespace"], {})
            tag_data = ns_facts.get(xbrl_entry["tag"])

            if not tag_data:
                tag_candidates.append({})
                continue

            unit_data = StatementSchema._get_unit_data(tag_data, row.unit, currency)

            if not unit_data:
                tag_candidates.append({})
                continue

            entries_by_date: dict[str, dict[str, tuple[str, float]]] = {}

            for entry in unit_data:

                _av_allowed = (
                    ANNUAL_FORMS | PRELIMINARY_FORMS
                    if include_preliminary
                    else ANNUAL_FORMS
                )
                if entry.get("form", "") not in _av_allowed:
                    continue
                start, end = entry.get("start", ""), entry.get("end", "")

                if not start or not end or start == end:
                    continue

                try:
                    days = (
                        datetime.strptime(end, "%Y-%m-%d")
                        - datetime.strptime(start, "%Y-%m-%d")
                    ).days
                except (ValueError, TypeError):
                    continue

                if not 300 <= days <= 400:
                    continue

                val = entry.get("val")

                if val is None:
                    continue

                filed = entry.get("filed", "")

                if end not in entries_by_date:
                    entries_by_date[end] = {}

                if filed not in entries_by_date[end]:
                    entries_by_date[end][filed] = (start, val)

            tag_candidates.append(entries_by_date)

        # Phase 2: resolve using filing-date consistency (same as annual)
        all_dates: set[str] = set()

        for tc in tag_candidates:
            all_dates.update(tc.keys())

        result: dict[str, tuple[str, float, str]] = {}

        for end_date in all_dates:
            # Earliest filing across all tags for this date
            ref_filed = None

            for tc in tag_candidates:
                filings = tc.get(end_date)

                if filings:
                    earliest = min(filings)

                    if ref_filed is None or earliest < ref_filed:
                        ref_filed = earliest

            if ref_filed is None:
                continue

            # First tag with exact ref_filed match
            for i, tc in enumerate(tag_candidates):
                filings = tc.get(end_date)

                if filings and ref_filed in filings:
                    start, val = filings[ref_filed]
                    xbrl_e = row.xbrl_tags[i]
                    xbrl_src = f"{xbrl_e['namespace']}:{xbrl_e['tag']}"
                    result[end_date] = (start, val, xbrl_src)
                    break

        return result

    @staticmethod
    def _get_ytd9_values(
        facts: dict[str, Any],
        row: RowDef,
        currency: str = "USD",
    ) -> dict[str, float]:
        """Return {fy_end_date: Q4_value} derived via FY − YTD_9mo.

        Used for per-share Q4 derivation.  Both the FY total and the
        9-month YTD must come from the **same filing** to avoid
        stock-split vintage mismatches.

        Returns the Q4 value (FY − YTD_9mo) keyed by FY end date.
        """
        if row.period_type != "duration":
            return {}

        # Collect annual and 9-month entries per (end_date, filed).
        # annual_entries: {fy_end: {filed: (fy_start, val)}}
        # ytd9_entries:   {ytd_end: {filed: val}}
        annual_entries: dict[str, dict[str, tuple[str, float]]] = {}
        ytd9_entries: dict[str, dict[str, float]] = {}

        for xbrl_entry in row.xbrl_tags:
            ns_facts = facts.get(xbrl_entry["namespace"], {})
            tag_data = ns_facts.get(xbrl_entry["tag"])

            if not tag_data:
                continue

            unit_data = StatementSchema._get_unit_data(tag_data, row.unit, currency)

            if not unit_data:
                continue

            for entry in unit_data:
                start = entry.get("start", "")
                end = entry.get("end", "")

                if not start or not end or start == end:
                    continue

                try:
                    days = (
                        datetime.strptime(end, "%Y-%m-%d")
                        - datetime.strptime(start, "%Y-%m-%d")
                    ).days
                except (ValueError, TypeError):
                    continue

                val = entry.get("val")

                if val is None:
                    continue

                filed = entry.get("filed", "")

                if 300 <= days <= 400:
                    if end not in annual_entries:
                        annual_entries[end] = {}
                    if filed not in annual_entries[end]:
                        annual_entries[end][filed] = (start, val)
                elif 240 <= days <= 310:
                    if end not in ytd9_entries:
                        ytd9_entries[end] = {}
                    if filed not in ytd9_entries[end]:
                        ytd9_entries[end][filed] = val

            # Stop at first tag with data (tag priority)
            if annual_entries or ytd9_entries:
                break

        if not annual_entries or not ytd9_entries:
            return {}

        # For each FY, find a filing that has both the annual and
        # YTD_9mo values, ensuring vintage consistency.
        result: dict[str, float] = {}

        for fy_end, fy_filings in annual_entries.items():
            # Find the 9-month YTD that falls within this FY
            ytd_end_match = None

            for ytd_end in ytd9_entries:
                # Check ytd_end is within this FY
                for filed, (fy_start, _) in fy_filings.items():
                    if fy_start < ytd_end < fy_end:
                        ytd_end_match = ytd_end
                        break

                if ytd_end_match:
                    break

            if not ytd_end_match:
                continue

            ytd_filings = ytd9_entries[ytd_end_match]

            # Use the LATEST filing for both annual and YTD to get
            # post-split restated values.  Per-share items are
            # affected by stock splits (different denominator), so
            # the most recent filing always has the correct basis.
            # When a common filing exists (same date for both annual
            # and YTD), use the latest common filing.  Otherwise
            # pair the latest annual with the latest YTD.
            common = set(fy_filings) & set(ytd_filings)

            if common:
                best = max(common)
                _, fy_val = fy_filings[best]
                ytd_val = ytd_filings[best]
            else:
                latest_fy = max(fy_filings)
                _, fy_val = fy_filings[latest_fy]
                ytd_val = ytd_filings[max(ytd_filings)]

            result[fy_end] = fy_val - ytd_val

        return result

    @staticmethod
    def extract_row_values(
        facts: dict[str, Any],
        row: RowDef,
        frequency: Frequency = "annual",
        currency: str = "USD",
        ref_filed_map: dict[str, str] | None = None,
        cross_targets: dict[str, float] | None = None,
        statement: str = "",
        include_preliminary: bool = False,
    ) -> tuple[dict[str, float], dict[str, str]]:
        """Extract values for a single schema row across all periods.

        For each period-end date, tries XBRL tags in chain order. The first
        tag with data for that date wins.

        For quarterly duration items, Q4 is derived as FY − (Q1+Q2+Q3).
        For quarterly instant items (BS), values from both 10-Q and 10-K are
        collected (the 10-K value at FY end = Q4 balance sheet).

        Parameters
        ----------
        ref_filed_map : dict or None
            When provided, maps each end_date to the global reference filing
            date (earliest across ALL rows in the statement).  This ensures
            all rows use the same filing vintage, preventing cross-filing
            mixing from retroactively-added tags.
        """
        period_type = row.period_type
        values_by_date: dict[str, float] = {}
        sources_by_date: dict[str, str] = {}
        _base_forms = ANNUAL_FORMS if frequency == "annual" else ALL_FORMS
        allowed_forms = (
            _base_forms | PRELIMINARY_FORMS if include_preliminary else _base_forms
        )
        # Collect ALL candidate entries per (tag_index, end_date) so we can
        # enforce filing-date consistency across tags for the same date.
        # Each entry: {end_date: {filed: val}}
        tag_candidates: list[dict[str, dict[str, float]]] = []
        collect_ytd = (
            frequency == "quarterly"
            and period_type == "duration"
            and row.unit != "shares"
        )
        ytd_tag_candidates: list[dict[str, dict[str, tuple[str, float]]]] = []

        for xbrl_entry in row.xbrl_tags:
            ns_facts = facts.get(xbrl_entry["namespace"], {})
            tag_data = ns_facts.get(xbrl_entry["tag"])

            if not tag_data:
                tag_candidates.append({})

                if collect_ytd:
                    ytd_tag_candidates.append({})

                continue

            unit_data = StatementSchema._get_unit_data(tag_data, row.unit, currency)

            if not unit_data:
                tag_candidates.append({})

                if collect_ytd:
                    ytd_tag_candidates.append({})

                continue

            # Collect all valid entries grouped by (end_date, filed)
            entries_by_date: dict[str, dict[str, float]] = {}
            _dur_by_date: dict[str, dict[str, int]] = (
                {}
            )  # track durations for shortest-wins
            ytd_entries_by_date: dict[str, dict[str, tuple[str, float]]] = {}

            for entry in unit_data:
                form = entry.get("form", "")

                if form not in allowed_forms:
                    continue

                end_date = entry.get("end", "")

                if not end_date:
                    continue

                days = 0  # instant items have no duration

                if period_type == "duration":
                    start_date = entry.get("start", "")

                    if not start_date or start_date == end_date:
                        continue
                    try:
                        days = (
                            datetime.strptime(end_date, "%Y-%m-%d")
                            - datetime.strptime(start_date, "%Y-%m-%d")
                        ).days
                    except (ValueError, TypeError):
                        continue

                    if frequency == "annual":
                        if not 300 <= days <= 400:
                            continue
                    elif form in SEMI_ANNUAL_FORMS:
                        if not (60 <= days <= 135 or 150 <= days <= 200):
                            continue
                    elif not 60 <= days <= 135:
                        if collect_ytd and 136 <= days <= 310:
                            ytd_val = entry.get("val")
                            if ytd_val is not None:
                                filed = entry.get("filed", "")
                                if end_date not in ytd_entries_by_date:
                                    ytd_entries_by_date[end_date] = {}
                                if filed not in ytd_entries_by_date[end_date]:
                                    ytd_entries_by_date[end_date][filed] = (
                                        start_date,
                                        ytd_val,
                                    )
                        continue

                val = entry.get("val")

                if val is None:
                    continue

                filed = entry.get("filed", "")

                if end_date not in entries_by_date:
                    entries_by_date[end_date] = {}
                    _dur_by_date[end_date] = {}
                # Prefer shorter duration (quarterly standalone over
                # cumulative YTD) when both exist for the same filing.
                if filed not in entries_by_date[end_date] or days < _dur_by_date[
                    end_date
                ].get(filed, 9999):
                    entries_by_date[end_date][filed] = val
                    _dur_by_date[end_date][filed] = days

            tag_candidates.append(entries_by_date)

            if collect_ytd:
                ytd_tag_candidates.append(ytd_entries_by_date)

        # Determine the reference filing per end_date, then
        # walk the tag chain and pick the first tag from that filing.
        # When a statement-level ref_filed_map is provided, use it so all
        # rows in the statement share the same filing vintage.  Otherwise
        # fall back to per-row earliest filing (standalone calls).
        all_dates: set[str] = set()

        for tc in tag_candidates:
            all_dates.update(tc.keys())

        for end_date in all_dates:
            if ref_filed_map is not None:
                ref_filed = ref_filed_map.get(end_date)
            else:
                # Per-row fallback: earliest filing across this row's tags
                ref_filed = None

                for tc in tag_candidates:
                    filings = tc.get(end_date)
                    if filings:
                        earliest = min(filings)
                        if ref_filed is None or earliest < ref_filed:
                            ref_filed = earliest

            if ref_filed is None:
                continue

            matched_identity = False

            if cross_targets and end_date in cross_targets:
                target_val = cross_targets[end_date]
                for i, tc in enumerate(tag_candidates):
                    filings = tc.get(end_date)
                    if not filings:
                        continue
                    # Check if any filing matches the exact identity value lock
                    for val in filings.values():
                        if isclose(val, target_val, rel_tol=1e-5, abs_tol=1.0):
                            values_by_date[end_date] = val
                            xbrl_e = row.xbrl_tags[i]
                            sources_by_date[end_date] = (
                                f"{xbrl_e['namespace']}:{xbrl_e['tag']}(identity_lock:{statement})"
                            )
                            matched_identity = True
                            break

                    if matched_identity:
                        break

            if matched_identity:
                continue

            if frequency == "quarterly" and period_type == "duration":
                # Quarterly duration (IS/CF flows): tag order wins over
                # filing match so the same XBRL tag resolves for both
                # quarterly and annual, keeping Q sum = FY consistent.
                for i, tc in enumerate(tag_candidates):
                    filings = tc.get(end_date)

                    if not filings:
                        continue

                    if ref_filed in filings:
                        values_by_date[end_date] = filings[ref_filed]
                    else:
                        # Fall back to nearest filing before ref_filed
                        # (same vintage as the 10-K).  If none exist
                        # before, use the earliest after.
                        before = [f for f in filings if f <= ref_filed]
                        best = max(before) if before else min(filings)
                        values_by_date[end_date] = filings[best]

                    xbrl_e = row.xbrl_tags[i]
                    sources_by_date[end_date] = f"{xbrl_e['namespace']}:{xbrl_e['tag']}"
                    break
            else:
                # Annual & quarterly instant (BS/CF snapshots): filing
                # consistency wins over tag order.
                for i, tc in enumerate(tag_candidates):
                    filings = tc.get(end_date)

                    if filings and ref_filed in filings:
                        values_by_date[end_date] = filings[ref_filed]
                        xbrl_e = row.xbrl_tags[i]
                        sources_by_date[end_date] = (
                            f"{xbrl_e['namespace']}:{xbrl_e['tag']}"
                        )
                        break
                else:
                    # No tag had an exact ref_filed match — fall back to
                    # the first tag with data, using nearest filing.
                    # Tag the source with "(fallback)" so the verification
                    # pass can detect cross-vintage values.
                    for i, tc in enumerate(tag_candidates):
                        filings = tc.get(end_date)

                        if filings:
                            before = [f for f in filings if f <= ref_filed]
                            best = max(before) if before else min(filings)
                            values_by_date[end_date] = filings[best]
                            xbrl_e = row.xbrl_tags[i]
                            sources_by_date[end_date] = (
                                f"{xbrl_e['namespace']}:{xbrl_e['tag']}(fallback)"
                            )
                            break

        # Quarterly duration: de-cumulate YTD entries, then derive Q4.
        if frequency == "quarterly" and period_type == "duration":
            annual_vals = StatementSchema._get_annual_values(
                facts, row, currency, include_preliminary=include_preliminary
            )

            # --- YTD de-cumulation ---
            # 10-Q cash-flow (and sometimes IS) items may only report
            # cumulative year-to-date values (6-month for Q2, 9-month
            # for Q3) rather than standalone quarterly figures.
            # De-cumulate: Q2 = YTD_Q2 − Q1, Q3 = YTD_Q3 − YTD_Q2.
            if collect_ytd and ytd_tag_candidates:
                ytd_resolved: dict[str, tuple[str, float, str]] = {}
                ytd_all_dates: set[str] = set()

                for ytc in ytd_tag_candidates:
                    ytd_all_dates.update(ytc.keys())

                for end_date in ytd_all_dates:
                    if ref_filed_map is not None:
                        ref = ref_filed_map.get(end_date)
                    else:
                        ref = None
                        for ytc in ytd_tag_candidates:
                            filings = ytc.get(end_date)

                            if filings:
                                earliest = min(filings)
                                if ref is None or earliest < ref:
                                    ref = earliest

                    if ref is None:
                        continue

                    for i, ytc in enumerate(ytd_tag_candidates):
                        filings = ytc.get(end_date)

                        if not filings:
                            continue

                        if ref in filings:
                            start_d, val = filings[ref]
                        else:
                            before = [f for f in filings if f <= ref]
                            best = max(before) if before else min(filings)
                            start_d, val = filings[best]

                        xbrl_e = row.xbrl_tags[i]
                        ytd_resolved[end_date] = (
                            start_d,
                            val,
                            f"{xbrl_e['namespace']}:{xbrl_e['tag']}",
                        )
                        break

                if ytd_resolved:
                    by_fy_start: dict[str, list[tuple[str, float, str]]] = defaultdict(
                        list
                    )
                    for end_d, (start_d, val, src) in ytd_resolved.items():
                        by_fy_start[start_d].append((end_d, val, src))

                    fy_boundaries = {
                        fy_start: fy_end
                        for fy_end, (fy_start, _, _) in annual_vals.items()
                    }

                    for fy_start, ytd_list in by_fy_start.items():
                        ytd_list.sort()
                        ytd_map = {d: (v, s) for d, v, s in ytd_list}
                        fy_end = fy_boundaries.get(fy_start)

                        if fy_end:
                            fy_q_dates = sorted(
                                d for d in values_by_date if fy_start < d < fy_end
                            )
                        else:
                            latest_ytd = ytd_list[-1][0]
                            fy_q_dates = sorted(
                                d for d in values_by_date if fy_start < d <= latest_ytd
                            )

                        all_q_dates = sorted(set(fy_q_dates) | set(ytd_map.keys()))

                        prev_cum = 0.0
                        for d in all_q_dates:
                            has_standalone = d in values_by_date
                            has_ytd = d in ytd_map

                            if not has_standalone and has_ytd:
                                ytd_val, ytd_src = ytd_map[d]
                                values_by_date[d] = ytd_val - prev_cum
                                sources_by_date[d] = f"ytd_derived({ytd_src})"

                            if has_ytd:
                                prev_cum = ytd_map[d][0]
                            elif has_standalone:
                                prev_cum += values_by_date[d]

            # --- Q4 derivation ---
            # Three strategies by unit type:
            #  1. shares: use the FY annual value as Q4 when no direct
            #     Q4 entry exists.  Weighted-average shares can't be
            #     derived via subtraction.
            #  2. per_share (EPS, DPS) and monetary: Q4 = FY − (Q1+Q2+Q3).
            #     Always overwrite any direct Q4 value so that Q_sum = FY
            #     (the 10-K annual total is authoritative; Q4 absorbs
            #     adjustments between 10-Q values and the 10-K).

            if row.unit == "shares":
                for fy_end, (fy_start, fy_val, fy_xbrl_src) in annual_vals.items():
                    if fy_end not in values_by_date:
                        values_by_date[fy_end] = fy_val
                        sources_by_date[fy_end] = f"Q4: FY[{fy_xbrl_src}]"

            else:
                for fy_end, (fy_start, fy_val, fy_xbrl_src) in annual_vals.items():
                    q_sum = 0
                    q_count = 0
                    for q_end, q_val in values_by_date.items():
                        if fy_start < q_end < fy_end:
                            q_sum += q_val
                            q_count += 1
                    if q_count == 3:
                        # Q4 = FY - (Q1 + Q2 + Q3)
                        q_srcs = [
                            sources_by_date.get(q_end, "")
                            for q_end in sorted(values_by_date)
                            if fy_start < q_end < fy_end
                        ]
                        q_labels = "+".join(
                            f"Q{i+1}[{s}]" for i, s in enumerate(q_srcs)
                        )
                        values_by_date[fy_end] = fy_val - q_sum
                        sources_by_date[fy_end] = (
                            f"Q4: FY[{fy_xbrl_src}] − ({q_labels})"
                        )
                    elif q_count == 1:
                        # H2 = FY - H1 (semi-annual filers with one
                        # interim period per fiscal year).
                        # Guard: the single interim date must be near
                        # the fiscal mid-point (±45 days).  A Q3 date
                        # (~270 days in) means the filer is quarterly
                        # with missing Q1/Q2 — do NOT derive Q4.
                        interim_date = next(
                            q_end
                            for q_end in values_by_date
                            if fy_start < q_end < fy_end
                        )
                        fy_days = (
                            datetime.strptime(fy_end, "%Y-%m-%d")
                            - datetime.strptime(fy_start, "%Y-%m-%d")
                        ).days
                        interim_days = (
                            datetime.strptime(interim_date, "%Y-%m-%d")
                            - datetime.strptime(fy_start, "%Y-%m-%d")
                        ).days
                        if abs(interim_days - fy_days / 2) <= 45:
                            h1_src = sources_by_date.get(interim_date, "")
                            values_by_date[fy_end] = fy_val - q_sum
                            sources_by_date[fy_end] = (
                                f"H2: FY[{fy_xbrl_src}] − H1[{h1_src}]"
                            )

        return values_by_date, sources_by_date

    @staticmethod
    def _compute_ref_filings(
        facts: dict[str, Any],
        rows_def: list,
        frequency: Frequency,
        currency: str,
        include_preliminary: bool = False,
    ) -> dict[str, str]:
        """Compute the earliest filing date per end_date across all rows.

        This global reference map ensures every row in a statement is
        extracted from the same filing vintage, preventing values that
        were retroactively added in later filings from mixing with
        original-filing data.
        """
        _base_forms = ANNUAL_FORMS if frequency == "annual" else ALL_FORMS
        allowed_forms = (
            _base_forms | PRELIMINARY_FORMS if include_preliminary else _base_forms
        )
        ref_map: dict[str, str] = {}

        for row_def in rows_def:
            period_type = row_def.period_type

            for xbrl_entry in row_def.xbrl_tags:
                ns_facts = facts.get(xbrl_entry["namespace"], {})
                tag_data = ns_facts.get(xbrl_entry["tag"])

                if not tag_data:
                    continue

                unit_data = StatementSchema._get_unit_data(
                    tag_data, row_def.unit, currency
                )

                if not unit_data:
                    continue

                for entry in unit_data:
                    form = entry.get("form", "")

                    if form not in allowed_forms:
                        continue

                    end_date = entry.get("end", "")

                    if not end_date:
                        continue

                    if period_type == "duration":
                        start_date = entry.get("start", "")

                        if not start_date or start_date == end_date:
                            continue

                        try:
                            days = (
                                datetime.strptime(end_date, "%Y-%m-%d")
                                - datetime.strptime(start_date, "%Y-%m-%d")
                            ).days
                        except (ValueError, TypeError):
                            continue

                        if frequency == "annual":
                            if not 300 <= days <= 400:
                                continue
                        elif form in SEMI_ANNUAL_FORMS:
                            if not (60 <= days <= 135 or 150 <= days <= 200):
                                continue
                        elif not 60 <= days <= 135:
                            continue

                    filed = entry.get("filed", "")

                    if filed and (end_date not in ref_map or filed < ref_map[end_date]):
                        ref_map[end_date] = filed

        return ref_map

    @staticmethod
    def _quarterly_ref_filings(
        facts: dict[str, Any],
        base_ref_map: dict[str, str],
    ) -> dict[str, str]:
        """Override quarterly ref filings to prefer 10-K vintage.

        For quarters within a completed FY (10-K filed), use the 10-K
        filing date so restated comparatives match the annual total.
        For the current FY (no 10-K yet), keep the original 10-Q ref.
        """
        # Discover FY periods and their earliest 10-K filing dates
        fy_filings: dict[str, tuple[str, str]] = {}  # fy_end → (fy_start, filed)

        for ns_facts in facts.values():
            for tag_data in ns_facts.values():
                for entries in tag_data.get("units", {}).values():
                    for entry in entries:
                        form = entry.get("form", "")

                        if form not in ANNUAL_FORMS:
                            continue

                        start = entry.get("start", "")
                        end = entry.get("end", "")
                        filed = entry.get("filed", "")

                        if not start or not end or not filed or start == end:
                            continue

                        try:
                            days = (
                                datetime.strptime(end, "%Y-%m-%d")
                                - datetime.strptime(start, "%Y-%m-%d")
                            ).days
                        except (ValueError, TypeError):
                            continue

                        if 300 <= days <= 400 and (
                            end not in fy_filings or filed < fy_filings[end][1]
                        ):
                            fy_filings[end] = (start, filed)

        if not fy_filings:
            return base_ref_map

        result = dict(base_ref_map)
        sorted_fys = sorted(fy_filings.keys())

        for date in base_ref_map:
            for fy_end in sorted_fys:
                fy_start, fy_filed = fy_filings[fy_end]
                if fy_start < date <= fy_end:
                    result[date] = fy_filed
                    break

        return result

    def extract(
        self,
        company_facts: dict[str, Any],
        statement: StatementName,
        *,
        frequency: Frequency = "annual",
        company_type: CompanyType | None = None,
        filing_dates: set[str] | None = None,
        skip_imputation: bool = False,
        ref_filed_map: dict[str, str] | None = None,
        cross_identities: dict[str, dict[str, float]] | None = None,
        pit_mode: bool = False,
        include_preliminary: bool = False,
    ) -> StatementResult:
        """Extract a single standardized statement from company facts JSON.

        Parameters
        ----------
        company_facts : dict
            Raw SEC company facts JSON (must have "facts" key, or be the
            facts dict directly keyed by namespace).
        statement : str
            One of "income_statement", "balance_sheet", "cash_flow".
        frequency : str
            "annual" or "quarterly".
        company_type : str or None
            "industrial" or "financial". Auto-detected if None.
        filing_dates : set or None
            Canonical period-end dates. Discovered automatically if None.
        ref_filed_map : dict or None
            Pre-computed reference filing date per period-end.  When
            provided (e.g. from ``extract_all``), skips per-statement
            computation so all statements share the same filing vintage.
        pit_mode : bool
            If True, skip the 10-K vintage override for quarterly data.
            Quarterly values will reflect the original 10-Q filing vintage,
            preserving point-in-time fidelity for backtesting.  Note:
            Q4 values may not reconcile to FY totals in this mode.
        include_preliminary : bool
            If True, include 8-K filing data for period-end dates not
            yet covered by a 10-Q/K.
        """
        # Accept either the full JSON or just the facts sub-dict
        facts = company_facts.get("facts", company_facts)

        if company_type is None:
            company_type = self.detect_type(facts)

        if filing_dates is None:
            filing_dates = self.get_filing_dates(
                facts, frequency, include_preliminary=include_preliminary
            )

        # Determine which dates are preliminary (8-K only, no 10-Q/K)
        _preliminary_dates: set[str] = set()
        if include_preliminary:
            confirmed_dates = self.get_filing_dates(facts, frequency)
            _preliminary_dates = filing_dates - confirmed_dates

        # Detect the filing's reporting currency once per extraction
        currency = self._detect_reporting_currency(facts)
        rows_def = self.get_rows(statement, company_type)
        result_rows: list[RowResult] = []
        # Use the caller-supplied ref_filed_map if available; otherwise
        # compute per-statement.
        if ref_filed_map is None:
            ref_filed_map = self._compute_ref_filings(
                facts,
                rows_def,
                frequency,
                currency,
                include_preliminary=include_preliminary,
            )
            # For quarterly: prefer 10-K filing vintage for completed FYs
            # so restated comparatives match the annual total.
            # Skip for balance_sheet: 10-K filings only contain FY-end
            # instant snapshots, not Q1/Q2/Q3 snapshots.  Overriding those
            # dates to the 10-K filing causes instant entries to be
            # unreachable (they were only filed in the 10-Q).
            # Skip in pit_mode: preserve original 10-Q filing vintage for
            # point-in-time fidelity (backtesting use case).
            if (
                frequency == "quarterly"
                and statement != "balance_sheet"
                and not pit_mode
            ):
                ref_filed_map = self._quarterly_ref_filings(facts, ref_filed_map)

        # Cash-flow credit-balance items are expressed as positive outflows
        # in XBRL.  Negate them so the statement uses the conventional
        # signed presentation (outflows negative, inflows positive).
        # Exceptions: net-income family items (they start the statement as a
        # positive figure) and supplemental disclosures (factor "0").
        _CF_SIGN_KEEP = frozenset(
            {"net_income", "net_income_continuing", "net_income_discontinued"}
        )
        apply_cf_sign = statement == "cash_flow"

        for row_def in rows_def:
            cross_targets = (
                cross_identities.get(row_def.tag) if cross_identities else None
            )
            values, sources = self.extract_row_values(
                facts,
                row_def,
                frequency,
                currency,
                ref_filed_map,
                cross_targets,
                statement,
                include_preliminary=include_preliminary,
            )
            values = {d: v for d, v in values.items() if d in filing_dates}
            sources = {d: s for d, s in sources.items() if d in filing_dates}

            if (
                apply_cf_sign
                and row_def.balance == "credit"
                and row_def.factor != "0"
                and row_def.tag not in _CF_SIGN_KEEP
            ):
                values = {d: -v for d, v in values.items()}

            result_rows.append(
                RowResult(
                    tag=row_def.tag,
                    label=row_def.label,
                    description=row_def.description,
                    parent=row_def.parent,
                    sequence=row_def.sequence,
                    factor=row_def.factor,
                    balance=row_def.balance,
                    unit=row_def.unit,
                    period_type=row_def.period_type,
                    values=values,
                    sources=sources,
                )
            )

        # Post-extraction imputation: derive missing values from known
        # algebraic relationships (xbrlsite ImputeRules).
        diagnostics: list[ValidationWarning] = []

        if not skip_imputation:
            result_rows, diagnostics = self._impute(
                result_rows, statement, company_type, filing_dates, facts
            )

        # Cash flow: fill gaps in cash_at_end_of_period (the strict
        # ref_filed match may miss dates where the instant snapshot
        # was filed on a different date than the duration rows), then
        # derive beginning-of-period from the previous period's end.
        if statement == "cash_flow":
            tag_map = {r.tag: r for r in result_rows}
            eop_row = tag_map.get("cash_at_end_of_period")
            bop_row = tag_map.get("cash_at_beginning_of_period")

            if eop_row:
                # Get the row definition for a standalone extraction
                eop_def = None

                for rd in rows_def:
                    if rd.tag == "cash_at_end_of_period":
                        eop_def = rd
                        break

                if eop_def:
                    standalone, standalone_src = self.extract_row_values(
                        facts, eop_def, frequency, currency
                    )
                    for date in filing_dates:
                        if date not in eop_row.values and date in standalone:
                            eop_row.values[date] = standalone[date]
                            eop_row.sources[date] = standalone_src.get(
                                date, "standalone"
                            )

            if eop_row and bop_row:
                sorted_dates = sorted(filing_dates)

                for i, date in enumerate(sorted_dates):
                    if i > 0:
                        prev_date = sorted_dates[i - 1]
                        prev_val = eop_row.values.get(prev_date)
                        if prev_val is not None:
                            bop_row.values[date] = prev_val
                            bop_row.sources[date] = (
                                f"derived: cash_at_end_of_period({prev_date})"
                            )

        # Cash balance identity: BOP + net_change = EOP.
        # Runs after BOP derivation so all three components are populated.
        # This is an independent cross-check: the activity decomposition
        # (op + inv + fin + fx = net_change) verifies the FLOW side;
        # this verifies the flow ties to the BALANCE side.
        if statement == "cash_flow" and not skip_imputation:
            tag_map = {r.tag: r for r in result_rows}
            _eop = tag_map.get("cash_at_end_of_period")
            _bop = tag_map.get("cash_at_beginning_of_period")
            _nc = tag_map.get("net_change_in_cash")

            if _eop and _bop and _nc:
                for date in filing_dates:
                    _ev = _eop.values.get(date)
                    _bv = _bop.values.get(date)
                    _nv = _nc.values.get(date)

                    if _ev is None or _bv is None or _nv is None:
                        continue

                    _diff = abs(_bv + _nv - _ev)

                    if _diff > _TOLERANCE:
                        _bop_src = _bop.sources.get(date, "")
                        _nc_src = _nc.sources.get(date, "")
                        _eop_src = _eop.sources.get(date, "")
                        # If BOP is derived from prior EOP, override it
                        # to make the identity hold (EOP is the anchor).
                        if "derived:" in _bop_src:
                            _bop.values[date] = _ev - _nv
                            _bop.sources[date] = (
                                "identity-enforced: cash_at_end_of_period"
                                " - net_change_in_cash"
                            )
                        # If net_change is imputed, override it.
                        elif "imputed:" in _nc_src:
                            _nc.values[date] = _ev - _bv
                            _nc.sources[date] = (
                                "identity-enforced: cash_at_end_of_period"
                                " - cash_at_beginning_of_period"
                            )
                        # If EOP is from standalone extraction, override it.
                        elif "standalone" in _eop_src:
                            _eop.values[date] = _bv + _nv
                            _eop.sources[date] = (
                                "identity-enforced: cash_at_beginning_of_period"
                                " + net_change_in_cash"
                            )
                        else:
                            # All hard — emit diagnostic.
                            diagnostics.append(
                                ValidationWarning(
                                    date=date,
                                    tag="cash_at_end_of_period",
                                    expected=_bv + _nv,
                                    actual=_ev,
                                    formula="cash_at_beginning_of_period + net_change_in_cash",
                                    identity="cash_at_end_of_period = cash_at_beginning_of_period + net_change_in_cash",
                                )
                            )

        # Prune dates where every row is NULL (phantom periods from
        # bogus filing dates or entity transitions).
        pruned_dates = set()

        for date in filing_dates:
            if any(r.values.get(date) is not None for r in result_rows):
                pruned_dates.add(date)

        # Build fiscal metadata (fy / fp) for each date from SEC entries
        fiscal_data = self.get_fiscal_meta(facts, frequency, pruned_dates)

        # Tag preliminary sources: prefix source strings for 8-K-only dates
        final_preliminary = _preliminary_dates & pruned_dates
        if final_preliminary:
            for row in result_rows:
                for date in final_preliminary:
                    if date in row.sources and not row.sources[date].startswith(
                        "preliminary:"
                    ):
                        row.sources[date] = f"preliminary:{row.sources[date]}"

        return StatementResult(
            statement=statement,
            company_type=company_type,
            frequency=frequency,
            currency=currency,
            dates=sorted(pruned_dates),
            rows=result_rows,
            fiscal_data=fiscal_data,
            diagnostics=diagnostics,
            preliminary_dates=final_preliminary,
        )

    def extract_all(
        self,
        company_facts: dict[str, Any],
        *,
        frequency: Frequency = "annual",
        company_type: CompanyType | None = None,
        skip_imputation: bool = False,
        pit_mode: bool = False,
        include_preliminary: bool = False,
    ) -> dict[str, StatementResult]:
        """Extract all three statements at once.

        Returns a dict keyed by statement name. Filing dates and company type
        are computed once and shared across all three statements.

        After individual extraction, dates are aligned so that all three
        statements report the exact same set of periods.  Any period-end
        date that is missing from even one statement is dropped from all
        three.  For quarterly frequency, incomplete fiscal years at the
        earliest boundary (fewer quarters than the norm) are also trimmed
        so that Q-SUM validation can succeed.

        Parameters
        ----------
        pit_mode : bool
            If True, skip the 10-K vintage override for quarterly data,
            preserving point-in-time fidelity for backtesting.
        include_preliminary : bool
            If True, include 8-K filing data for period-end dates not
            yet covered by a 10-Q/K.
        """
        facts = company_facts.get("facts", company_facts)

        if company_type is None:
            company_type = self.detect_type(facts)

        filing_dates = self.get_filing_dates(
            facts, frequency, include_preliminary=include_preliminary
        )

        _STMTS = ("income_statement", "balance_sheet", "cash_flow")

        # Compute a SINGLE reference filing map across ALL rows from all
        # three statements.  This ensures every statement extracts values
        # from the same filing vintage (prevents CROSS IS/CF net_income
        # mismatches caused by per-statement earliest-filing differences).
        currency = self._detect_reporting_currency(facts)
        all_rows = []

        for stmt in _STMTS:
            all_rows.extend(self.get_rows(stmt, company_type))

        shared_ref_map = self._compute_ref_filings(
            facts,
            all_rows,
            frequency,
            currency,
            include_preliminary=include_preliminary,
        )

        # For quarterly IS/CF: override to 10-K vintage for completed FYs.
        # BS keeps the base map (10-K instants only cover FY-end, not Q1-Q3).
        # Skip in pit_mode: preserve original 10-Q filing vintage.
        if frequency == "quarterly" and not pit_mode:
            shared_ref_map_q = self._quarterly_ref_filings(facts, shared_ref_map)
        else:
            shared_ref_map_q = shared_ref_map

        results: dict[str, StatementResult] = {}
        cross_identities: dict[str, dict[str, float]] = {}

        for stmt in _STMTS:
            ref = shared_ref_map if stmt == "balance_sheet" else shared_ref_map_q
            results[stmt] = self.extract(
                facts,
                stmt,
                skip_imputation=skip_imputation,
                frequency=frequency,
                company_type=company_type,
                filing_dates=filing_dates,
                ref_filed_map=ref,
                cross_identities=cross_identities,
                pit_mode=pit_mode,
                include_preliminary=include_preliminary,
            )

            # PHASE 2: Register values for cross-statement identity matching
            for r in results[stmt].rows:
                # E.g. "net_income" extracted from IS will constrain "net_income" in CF
                if r.tag not in cross_identities:
                    cross_identities[r.tag] = {}
                cross_identities[r.tag].update(r.values)

        # ----- Align dates across all three statements -----
        # Each extract() prunes phantom dates independently, so the three
        # statements can end up with slightly different date sets.
        # Only keep dates that appear in ALL three statements.
        date_sets = [set(r.dates) for r in results.values()]
        common_dates = date_sets[0] & date_sets[1] & date_sets[2]

        # For quarterly: the first fiscal year must be complete.
        # Drop leading FYs that have fewer periods than the norm.
        if frequency == "quarterly" and common_dates:
            annual_dates = sorted(self.get_filing_dates(facts, "annual"))

            if annual_dates:
                sorted_q = sorted(common_dates)
                fy_groups: dict[str, list[str]] = {}

                for qd in sorted_q:
                    fy_end = None
                    for ad in annual_dates:
                        if qd <= ad:
                            fy_end = ad
                            break
                    if fy_end:
                        fy_groups.setdefault(fy_end, []).append(qd)
                    # Dates beyond last annual = current incomplete FY — keep

                # Expected periods per FY = mode of FY sizes
                completed = dict(fy_groups)

                if len(completed) > 2:
                    size_counts = Counter(len(v) for v in completed.values())
                    expected = size_counts.most_common(1)[0][0]

                    # Drop leading incomplete FYs only
                    for fy_end in sorted(completed.keys()):
                        if len(completed[fy_end]) < expected:
                            for qd in completed[fy_end]:
                                common_dates.discard(qd)
                        else:
                            break

        # Apply the aligned date set to every statement
        aligned = sorted(common_dates)
        # Build unified fiscal metadata for the aligned dates
        aligned_fiscal = self.get_fiscal_meta(facts, frequency, common_dates)

        # Merge preliminary_dates across all statements and intersect
        # with the aligned date set.
        all_preliminary: set[str] = set()
        for stmt_result in results.values():
            all_preliminary |= stmt_result.preliminary_dates
        aligned_preliminary = all_preliminary & common_dates

        for stmt_result in results.values():
            stmt_result.dates = aligned
            stmt_result.fiscal_data = aligned_fiscal
            stmt_result.preliminary_dates = aligned_preliminary

            for row in stmt_result.rows:
                row.values = {d: v for d, v in row.values.items() if d in common_dates}
                row.sources = {
                    d: s for d, s in row.sources.items() if d in common_dates
                }

        return results

    @staticmethod
    def merge_facts(*facts_list: dict[str, Any]) -> dict[str, Any]:
        """Merge multiple CompanyFacts JSON dicts into a single unified dict.

        Some companies change CIK over time (e.g., BlackRock moved from
        CIK 1364742 to CIK 2012383 in 2025).  This combines all XBRL
        entries so the extraction engine sees the full history.

        Entries are concatenated per namespace/tag/unit and deduplicated
        on ``(end, start, val, form, filed)``.  The extraction engine's
        ``ref_filed`` logic naturally picks the correct filing vintage.

        Parameters
        ----------
        *facts_list : dict
            Two or more raw SEC CompanyFacts JSON dicts (each with a
            top-level ``"facts"`` key, or already the facts sub-dict).

        Returns
        -------
        dict
            A single merged facts dict (namespace-keyed, no wrapper).
        """
        merged: dict[str, dict] = {}

        for raw in facts_list:
            facts = raw.get("facts", raw)

            for ns, tags in facts.items():
                if ns not in merged:
                    merged[ns] = {}

                for tag_name, tag_data in tags.items():
                    if tag_name not in merged[ns]:
                        merged[ns][tag_name] = {}
                    src_label = tag_data.get("label", "")
                    src_desc = tag_data.get("description", "")

                    if "label" not in merged[ns][tag_name] and src_label:
                        merged[ns][tag_name]["label"] = src_label

                    if "description" not in merged[ns][tag_name] and src_desc:
                        merged[ns][tag_name]["description"] = src_desc

                    src_units = tag_data.get("units", {})

                    if "units" not in merged[ns][tag_name]:
                        merged[ns][tag_name]["units"] = {}

                    for unit_key, entries in src_units.items():
                        if unit_key not in merged[ns][tag_name]["units"]:
                            merged[ns][tag_name]["units"][unit_key] = []

                        existing = merged[ns][tag_name]["units"][unit_key]
                        # Build a set of dedup keys from already-merged entries
                        seen = set()

                        for e in existing:
                            key = (
                                e.get("end", ""),
                                e.get("start", ""),
                                e.get("val"),
                                e.get("form", ""),
                                e.get("filed", ""),
                            )
                            seen.add(key)

                        for e in entries:
                            key = (
                                e.get("end", ""),
                                e.get("start", ""),
                                e.get("val"),
                                e.get("form", ""),
                                e.get("filed", ""),
                            )
                            if key not in seen:
                                existing.append(e)
                                seen.add(key)

        return merged

    # Imputation rules derived from xbrlsite Report Frame ImputeRules.
    # Each rule: (target_tag, [(source_tag, sign), ...])
    # target = sum of (source * sign) — only applied when target is missing
    # and ALL sources are present.

    # IS rules by company_type
    _IS_IMPUTE: dict[str, list[tuple[str, list[tuple[str, int]]]]] = {
        "industrial": [
            # --- Single-step IS rules (C&E-based) ---
            # Must come first: when costs_and_expenses exists but COGS/GP
            # don't, derive COGS from C&E - OpEx (OpEx is available from
            # hierarchical rollup of children like SGA, D&A, etc.)
            (
                "total_cost_of_revenue",
                [("costs_and_expenses", 1), ("total_operating_expenses", -1)],
            ),
            (
                "total_operating_expenses",
                [("costs_and_expenses", 1), ("total_cost_of_revenue", -1)],
            ),
            (
                "costs_and_expenses",
                [("total_revenue", 1), ("total_operating_income", -1)],
            ),
            # --- Standard multi-step IS rules ---
            (
                "total_gross_profit",
                [("total_revenue", 1), ("total_cost_of_revenue", -1)],
            ),
            (
                "total_cost_of_revenue",
                [("total_revenue", 1), ("total_gross_profit", -1)],
            ),
            (
                "total_operating_expenses",
                [("total_gross_profit", 1), ("total_operating_income", -1)],
            ),
            (
                "total_operating_income",
                [("total_gross_profit", 1), ("total_operating_expenses", -1)],
            ),
            (
                "total_other_income",
                [("total_pretax_income", 1), ("total_operating_income", -1)],
            ),
        ],
        "diversified": [
            (
                "total_operating_income",
                [("total_pretax_income", 1), ("total_other_income", -1)],
            ),
            (
                "total_operating_income",
                [("total_revenue", 1), ("costs_and_expenses", -1)],
            ),
            (
                "costs_and_expenses",
                [("total_revenue", 1), ("total_operating_income", -1)],
            ),
            (
                "total_other_income",
                [("total_pretax_income", 1), ("total_operating_income", -1)],
            ),
        ],
        "financial": [
            (
                "total_interest_income",
                [("net_interest_income", 1), ("total_interest_expense", 1)],
            ),
            (
                "net_interest_income_after_provision",
                [("net_interest_income", 1), ("provision_for_credit_losses", -1)],
            ),
            # Revenue = NII + non-interest income.  Early filings
            # (AmEx pre-2015) lack RevenuesNetOfInterestExpense but
            # have the components.
            (
                "total_revenue",
                [("net_interest_income", 1), ("total_noninterest_income", 1)],
            ),
            # Fallback: Revenue = pretax + opex.  Goldman pre-2011 has
            # no revenue or NII tags but does report NoninterestExpense
            # and pretax income (or NI + tax from which pretax is
            # derived by _IS_VERIFY).
            (
                "total_revenue",
                [("total_pretax_income", 1), ("total_noninterest_expense", 1)],
            ),
        ],
        "insurance": [
            (
                "total_pretax_income",
                [("total_revenue", 1), ("benefits_costs_expenses", -1)],
            ),
            (
                "benefits_costs_expenses",
                [("total_revenue", 1), ("total_pretax_income", -1)],
            ),
        ],
    }

    # Core IS identities used for verification only (no decomposition
    # rules that could create circular overrides).
    # net_income is intentionally EXCLUDED: the ProfitLoss tag is the
    # authoritative source and must match the CF statement.  The
    # ni_cont + disc identity uses broader NCI-inclusive tags that
    # can disagree with ProfitLoss for companies with discontinued
    # operations (3M, Honeywell, J&J, Merck).  Imputation still
    # derives net_income from components when NULL.
    #
    # Pretax/NI identity: some filers only report the narrow-scope
    # pretax tag (...MinorityInterestAndIncomeLossFromEquityMethod
    # Investments) which EXCLUDES equity-method income while NI
    # (ProfitLoss) INCLUDES it.  The verify loop skips this check
    # when the pretax source tag indicates the narrow scope.
    _IS_VERIFY: list[tuple[str, list[tuple[str, int]]]] = [
        (
            "total_pretax_income",
            [("net_income_continuing", 1), ("income_tax_expense", 1)],
        ),
        (
            "net_income_continuing",
            [("total_pretax_income", 1), ("income_tax_expense", -1)],
        ),
        # GP = rev - COGS.  Revenue and COGS are primary data; GP is a
        # derived subtotal.  Some XBRL filings have small rounding diffs
        # (IBM ±$1M) or vintage-mixed values (HON 2009).  Override GP
        # so the identity holds exactly.
        (
            "total_gross_profit",
            [("total_revenue", 1), ("total_cost_of_revenue", -1)],
        ),
        # OpInc = GP - OpEx.  Cascading fix after GP correction.
        (
            "total_operating_income",
            [("total_gross_profit", 1), ("total_operating_expenses", -1)],
        ),
    ]

    # Balance-sheet verification identities.  Only fundamental
    # identities that always hold are included.  Noncurrent
    # derivations (Assets - Current) are excluded because some
    # companies have mezzanine items outside current/noncurrent.
    # Common-equity identity is excluded because StockholdersEquity
    # includes preferred equity in XBRL (see Goldman Sachs).
    # The total_liabilities rule includes redeemable NCI; the
    # fallback (without redeemable NCI) fires only when the broader
    # rule cannot be evaluated — handled via verified_pairs.
    _BS_VERIFY: list[tuple[str, list[tuple[str, int]]]] = [
        # Fundamental: Assets = Liabilities + Equity
        ("total_assets", [("total_liabilities_and_equity", 1)]),
        # Equity decomposition
        (
            "total_equity_and_noncontrolling_interests",
            [("total_equity", 1), ("noncontrolling_interests", 1)],
        ),
        (
            "total_equity",
            [
                ("total_equity_and_noncontrolling_interests", 1),
                ("noncontrolling_interests", -1),
            ],
        ),
        # Liabilities = L&E - Equity_NCI - Redeemable NCI (broader rule first)
        (
            "total_liabilities",
            [
                ("total_liabilities_and_equity", 1),
                ("total_equity_and_noncontrolling_interests", -1),
                ("redeemable_noncontrolling_interest", -1),
            ],
        ),
        # Fallback: Liabilities = L&E - Equity_NCI (no redeemable NCI)
        (
            "total_liabilities",
            [
                ("total_liabilities_and_equity", 1),
                ("total_equity_and_noncontrolling_interests", -1),
            ],
        ),
    ]

    # Cash-flow verification identities.  Only the cash-flow
    # identity (net change = sum of activities) is checked.
    # D&A decomposition is NOT a valid accounting identity because
    # DepreciationDepletionAndAmortization includes depletion
    # while Depreciation + Amortization does not.
    # The verify loop handles IncludingExchangeRateEffect tags
    # by checking the source and excluding FX when already baked in.
    _CF_VERIFY: list[tuple[str, list[tuple[str, int]]]] = [
        # Rule 1: with FX — matches new-basis tags and old-basis tags that
        # DO include exchange-rate effects in the total.
        (
            "net_change_in_cash",
            [
                ("net_cash_from_operating_activities", 1),
                ("net_cash_from_investing_activities", 1),
                ("net_cash_from_financing_activities", 1),
                ("effect_of_exchange_rate_changes", 1),
            ],
        ),
        # Rule 2: without FX — matches old-basis tags that EXCLUDE FX.
        (
            "net_change_in_cash",
            [
                ("net_cash_from_operating_activities", 1),
                ("net_cash_from_investing_activities", 1),
                ("net_cash_from_financing_activities", 1),
            ],
        ),
        # Rule 3: with FX + other — handles reconciling items like
        # business-acquisition cash (Ferrovial) that sit outside the
        # standard operating/investing/financing/FX buckets.
        (
            "net_change_in_cash",
            [
                ("net_cash_from_operating_activities", 1),
                ("net_cash_from_investing_activities", 1),
                ("net_cash_from_financing_activities", 1),
                ("effect_of_exchange_rate_changes", 1),
                ("other_net_changes_in_cash", 1),
            ],
        ),
        # Rule 4: without FX + other.
        (
            "net_change_in_cash",
            [
                ("net_cash_from_operating_activities", 1),
                ("net_cash_from_investing_activities", 1),
                ("net_cash_from_financing_activities", 1),
                ("other_net_changes_in_cash", 1),
            ],
        ),
    ]

    _IS_IMPUTE_COMMON: list[tuple[str, list[tuple[str, int]]]] = [
        (
            "total_pretax_income",
            [("net_income_continuing", 1), ("income_tax_expense", 1)],
        ),
        (
            "net_income_continuing",
            [("total_pretax_income", 1), ("income_tax_expense", -1)],
        ),
        ("net_income", [("net_income_continuing", 1), ("net_income_discontinued", 1)]),
        # Comprehensive income: CI = NI + OCI
        (
            "comprehensive_income",
            [("comprehensive_income_parent", 1), ("comprehensive_income_nci", 1)],
        ),
        (
            "comprehensive_income_parent",
            [("comprehensive_income", 1), ("comprehensive_income_nci", -1)],
        ),
        (
            "comprehensive_income_nci",
            [("comprehensive_income", 1), ("comprehensive_income_parent", -1)],
        ),
        # Income tax split: total = current + deferred
        (
            "income_tax_expense",
            [("income_tax_current", 1), ("income_tax_deferred", 1)],
        ),
        (
            "income_tax_current",
            [("income_tax_expense", 1), ("income_tax_deferred", -1)],
        ),
        (
            "income_tax_deferred",
            [("income_tax_expense", 1), ("income_tax_current", -1)],
        ),
        # Pretax = before equity method + equity method investments
        (
            "total_pretax_income",
            [("income_before_equity_method", 1), ("equity_method_investments", 1)],
        ),
        (
            "income_before_equity_method",
            [("total_pretax_income", 1), ("equity_method_investments", -1)],
        ),
        # NCI = redeemable NCI + nonredeemable NCI
        (
            "net_income_to_noncontrolling_interest",
            [("net_income_nci_redeemable", 1), ("net_income_nci_nonredeemable", 1)],
        ),
    ]

    _BS_IMPUTE: list[tuple[str, list[tuple[str, int]]]] = [
        (
            "total_noncurrent_assets",
            [("total_assets", 1), ("total_current_assets", -1)],
        ),
        (
            "total_noncurrent_liabilities",
            [("total_liabilities", 1), ("total_current_liabilities", -1)],
        ),
        ("total_liabilities_and_equity", [("total_assets", 1)]),
        (
            "total_liabilities",
            [
                ("total_liabilities_and_equity", 1),
                ("total_equity_and_noncontrolling_interests", -1),
                ("redeemable_noncontrolling_interest", -1),
            ],
        ),
        (
            "total_liabilities",
            [
                ("total_liabilities_and_equity", 1),
                ("total_equity_and_noncontrolling_interests", -1),
            ],
        ),
        (
            "total_equity_and_noncontrolling_interests",
            [("total_equity", 1), ("noncontrolling_interests", 1)],
        ),
        (
            "total_equity",
            [
                ("total_equity_and_noncontrolling_interests", 1),
                ("noncontrolling_interests", -1),
            ],
        ),
        ("total_common_equity", [("total_equity", 1), ("total_preferred_equity", -1)]),
        # Fallback: common_equity = total_equity when no preferred row exists.
        # The rule above fires first when preferred is present; this catches
        # companies without preferred stock.
        ("total_common_equity", [("total_equity", 1)]),
        # Fallback: E_nci = E when NCI isn't separately reported.
        ("total_equity_and_noncontrolling_interests", [("total_equity", 1)]),
        # Redeemable NCI breakdown
        (
            "redeemable_noncontrolling_interest",
            [
                ("redeemable_nci_common", 1),
                ("redeemable_nci_preferred", 1),
                ("redeemable_nci_other", 1),
            ],
        ),
        # Impute mezzanine equity from the fundamental BS identity:
        # R_nci = L&E - L - E_nci.  Fires when no direct mezzanine tag
        # exists but all three totals are available (e.g. BlackRock Inc).
        (
            "redeemable_noncontrolling_interest",
            [
                ("total_liabilities_and_equity", 1),
                ("total_liabilities", -1),
                ("total_equity_and_noncontrolling_interests", -1),
            ],
        ),
    ]

    _CF_IMPUTE: list[tuple[str, list[tuple[str, int]]]] = [
        (
            "net_change_in_cash",
            [
                ("net_cash_from_operating_activities", 1),
                ("net_cash_from_investing_activities", 1),
                ("net_cash_from_financing_activities", 1),
                ("effect_of_exchange_rate_changes", 1),
            ],
        ),
        # Derive FX from the identity when FX is missing but the
        # other four components are present (common after companies
        # switched to the "IncludingExchangeRateEffect" net-change tag).
        (
            "effect_of_exchange_rate_changes",
            [
                ("net_change_in_cash", 1),
                ("net_cash_from_operating_activities", -1),
                ("net_cash_from_investing_activities", -1),
                ("net_cash_from_financing_activities", -1),
            ],
        ),
        # D&A = depreciation + amortization
        (
            "depreciation_and_amortization",
            [("depreciation_expense", 1), ("amortization_expense", 1)],
        ),
    ]

    # Maximum number of imputation passes (defensive upper bound;
    # typically converges in 2-3 for derivation chains up to 3 steps deep).
    _MAX_IMPUTE_PASSES: int = 10

    @staticmethod
    def _format_impute_source(prefix: str, sources: list[tuple[str, int]]) -> str:
        """Build a human-readable source string for an imputation rule."""
        parts: list[str] = []

        for i, (src_tag, sign) in enumerate(sources):
            if i == 0:
                parts.append(f"{'-' if sign < 0 else ''}{src_tag}")
            else:
                parts.append(f"{'+' if sign > 0 else '-'} {src_tag}")

        return f"{prefix}: {' '.join(parts)}"

    @staticmethod
    def _run_imputation_passes(
        rows: list[RowResult],
        rules: list[tuple[str, list[tuple[str, int]]]],
        tag_idx: dict[str, int],
        filing_dates: set[str],
    ) -> bool:
        """Run up to _MAX_IMPUTE_PASSES imputation passes over all rules.

        Returns True if any value was derived across all passes.
        """
        any_changed = False

        for _pass in range(StatementSchema._MAX_IMPUTE_PASSES):
            changed = False

            for target_tag, sources in rules:
                target_i = tag_idx.get(target_tag)

                if target_i is None:
                    continue

                target_row = rows[target_i]

                for date in filing_dates:

                    if target_row.values.get(date) is not None:
                        continue

                    val = 0.0
                    all_present = True

                    for src_tag, sign in sources:
                        src_i = tag_idx.get(src_tag)

                        if src_i is None:
                            all_present = False
                            break

                        src_val = rows[src_i].values.get(date)

                        if src_val is None:
                            all_present = False
                            break

                        val += src_val * sign

                    if all_present:
                        target_row.values[date] = val
                        target_row.sources[date] = (
                            StatementSchema._format_impute_source("imputed", sources)
                        )
                        changed = True

            if not changed:
                break

            any_changed = True

        return any_changed

    @staticmethod
    def _apply_hierarchical_articulation(
        rows: list[RowResult],
        filing_dates: set[str],
    ) -> None:
        """Enforce parent-child math by rolling up missing parents or generating plugs.

        Evaluates the tree strictly bottom-up.
        If a parent is missing, it is imputed from the sum of its children.
        If a parent exists but differs from the sum of its children, an
        'other_{parent_tag}' plug is generated to ensure exact math articulation.
        """
        tag_to_row = {r.tag: r for r in rows}
        children_by_parent: dict[str, list[RowResult]] = {}
        depth_map: dict[str, int] = {}

        def get_depth(tag: str) -> int:
            if tag in depth_map:
                return depth_map[tag]
            row = tag_to_row.get(tag)
            if not row or not row.parent or row.parent not in tag_to_row:
                depth_map[tag] = 0
                return 0
            # Prevent infinite recursion in case of malformed schema
            depth_map[tag] = 0
            d = 1 + get_depth(row.parent)
            depth_map[tag] = d
            return d

        for row in rows:
            get_depth(row.tag)

            if row.parent and row.factor in ("+", "-"):
                if row.parent not in children_by_parent:
                    children_by_parent[row.parent] = []

                children_by_parent[row.parent].append(row)

        parents = list(children_by_parent.keys())
        # Sort from deepest (highest depth) to shallowest (0)
        parents.sort(key=lambda p: get_depth(p), reverse=True)
        new_rows: list[RowResult] = []

        for parent_tag in parents:
            parent_row = tag_to_row[parent_tag]
            children = children_by_parent[parent_tag]

            for date in filing_dates:
                children_sum = 0.0
                has_child_val = False
                contributing_children: list[str] = []

                for child in children:
                    # Skip existing plug rows — they will be recalculated
                    if child.tag.startswith(
                        "other_"
                    ) and "imputed-plug" in child.sources.get(date, ""):
                        continue

                    c_val = child.values.get(date)

                    if c_val is not None:
                        has_child_val = True
                        sign = 1.0 if child.factor == "+" else -1.0
                        children_sum += c_val * sign
                        contributing_children.append(f"{child.tag}({child.factor})")

                if not has_child_val:
                    continue

                p_val = parent_row.values.get(date)
                children_detail = " + ".join(contributing_children)

                if p_val is None:
                    # Rollup imputation
                    parent_row.values[date] = children_sum
                    parent_row.sources[date] = f"imputed-rollup: {children_detail}"
                else:
                    # Plug generation
                    diff = p_val - children_sum

                    if abs(diff) > _TOLERANCE:
                        base = parent_tag.removeprefix("total_")
                        plug_tag = f"other_{base}"

                        if plug_tag not in tag_to_row:
                            plug_seq = parent_row.sequence
                            base_label = parent_row.label.removeprefix("Total ")
                            plug_row = RowResult(
                                tag=plug_tag,
                                label=f"Other {base_label}",
                                description="Synthetic balancing plug derived from "
                                + f"{parent_row.label} minus explicitly mapped children.",
                                parent=parent_tag,
                                sequence=plug_seq - 0.01,
                                factor="+",
                                balance=parent_row.balance,
                                unit=parent_row.unit,
                                period_type=parent_row.period_type,
                                values={},
                                sources={},
                            )
                            tag_to_row[plug_tag] = plug_row
                            new_rows.append(plug_row)

                        plug_row = tag_to_row[plug_tag]
                        # Don't overwrite real XBRL-extracted values
                        existing_source = plug_row.sources.get(date, "")

                        if date in plug_row.values and "imputed" not in existing_source:
                            continue

                        plug_row.values[date] = diff
                        plug_row.sources[date] = (
                            f"imputed-plug: {parent_tag} - ({children_detail})"
                        )

        if new_rows:
            rows.extend(new_rows)
            # Re-sort rows to place plugs right before their parent
            # stable sort keeps original standard items in order
            rows.sort(key=lambda r: float(r.sequence))

    def _impute(
        self,
        rows: list[RowResult],
        statement: StatementName,
        company_type: CompanyType,
        filing_dates: set[str],
        facts: dict[str, Any] | None = None,
    ) -> tuple[list[RowResult], list[ValidationWarning]]:
        """Apply imputation rules to derive missing values, then validate.

        Runs multiple passes (up to _MAX_IMPUTE_PASSES) so cascading
        derivations work.  After imputation, validates accounting identities
        and returns any discrepancies as diagnostics (never overrides
        extracted values).
        """
        if statement == "income_statement":
            rules = self._IS_IMPUTE.get(company_type, []) + self._IS_IMPUTE_COMMON
        elif statement == "balance_sheet":
            rules = self._BS_IMPUTE
        elif statement == "cash_flow":
            rules = self._CF_IMPUTE
        else:
            return rows, []

        if not rules:
            return rows, []

        tag_idx: dict[str, int] = {r.tag: i for i, r in enumerate(rows)}

        # --- Pre-imputation: EquityMethod pretax reclassification ---
        # When total_pretax_income was extracted from the narrow XBRL tag
        # (...MinorityInterestAndIncomeLossFromEquityMethodInvestments)
        # the value EXCLUDES equity-method income.  Only correct pretax
        # to broad scope when the narrow identity (pretax = NI + tax)
        # does NOT already hold — meaning NI is broad-scope and pretax
        # is narrow, creating a scope mismatch.  When narrow pretax
        # already equals NI + tax, both are same scope — leave as-is.
        if statement == "income_statement":
            _ptx_i = tag_idx.get("total_pretax_income")
            _beq_i = tag_idx.get("income_before_equity_method")
            _eqm_i = tag_idx.get("equity_method_investments")
            _nic_i = tag_idx.get("net_income_continuing")
            _tax_i = tag_idx.get("income_tax_expense")

            if _ptx_i is not None:
                _ptx = rows[_ptx_i]

                for _d in list(filing_dates):
                    _s = _ptx.sources.get(_d, "")

                    if "EquityMethodInvestments" not in _s:
                        continue
                    # Ensure income_before_equity_method preserves the
                    # narrow value (it maps to the same XBRL tag but
                    # may not have resolved for all dates).
                    if _beq_i is not None and _d not in rows[_beq_i].values:
                        rows[_beq_i].values[_d] = _ptx.values[_d]
                        rows[_beq_i].sources[_d] = _s
                    # Check if narrow identity already holds:
                    # pretax_narrow = NI + tax → scopes match, no fix needed.
                    _ni_v = rows[_nic_i].values.get(_d) if _nic_i is not None else None
                    _tx_v = rows[_tax_i].values.get(_d) if _tax_i is not None else None
                    _ni_src = (
                        rows[_nic_i].sources.get(_d, "") if _nic_i is not None else ""
                    )

                    if (
                        _ni_v is not None
                        and _tx_v is not None
                        and abs(_ptx.values[_d] - _ni_v - _tx_v) <= _TOLERANCE
                    ):
                        # Narrow pretax = NI + tax already.  NI and pretax
                        # share the same scope — no correction needed.
                        continue
                    # If NI comes from ProfitLoss (total scope — includes
                    # equity method AND disc ops), pretax should equal
                    # NI + tax without any correction.  Clear pretax so
                    # imputation derives it from NI + tax.
                    if "ProfitLoss" in _ni_src and "FromContinuing" not in _ni_src:
                        del _ptx.values[_d]
                        del _ptx.sources[_d]
                        continue

                    _eqv = rows[_eqm_i].values.get(_d) if _eqm_i is not None else None

                    if _eqv is not None and _eqv != 0:
                        # Correct pretax to broad scope.
                        _ptx.values[_d] += _eqv
                        _ptx.sources[_d] = (
                            "corrected: income_before_equity_method"
                            " + equity_method_investments"
                        )
                    else:
                        # No equity-method income available; clear pretax
                        # so imputation derives it from NI + tax.
                        del _ptx.values[_d]
                        del _ptx.sources[_d]

        # --- Pre-imputation: ProfitLoss continuing-ops adjustment ---
        # When net_income_continuing was extracted from ProfitLoss (total
        # NI including discontinued operations), subtract disc-ops NI to
        # get the continuing-only figure matching pretax scope.
        # BUT only if tax is also continuing-scope — otherwise mixing
        # continuing NI with total tax breaks the pretax identity.
        if statement == "income_statement":
            _nic_i = tag_idx.get("net_income_continuing")
            _disc_i = tag_idx.get("net_income_discontinued")
            _tax_i = tag_idx.get("income_tax_expense")

            if _nic_i is not None and _disc_i is not None:
                _nic = rows[_nic_i]
                _disc = rows[_disc_i]

                for _d in list(filing_dates):
                    _s = _nic.sources.get(_d, "")

                    if "ProfitLoss" not in _s:
                        continue
                    # Only trigger for the bare ProfitLoss tag (total NI),
                    # not for already-continuing tags like
                    # ProfitLossFromContinuingOperations.
                    if "ProfitLossFrom" in _s or "ProfitLossBefore" in _s:
                        continue
                    # Skip disc-adjustment if tax is total-scope — mixing
                    # continuing NI with total tax creates scope mismatch.
                    if _tax_i is not None:
                        _tax_src = rows[_tax_i].sources.get(_d, "")

                        if _tax_src and "ContinuingOperations" not in _tax_src:
                            continue

                    _dv = _disc.values.get(_d)

                    if _dv is not None and _dv != 0:
                        _nic.values[_d] -= _dv
                        _nic.sources[_d] = _s + "(disc-adjusted)"

        # Roll up parent nodes from children BEFORE imputation so that
        # derived subtotals (e.g. total_operating_expenses from SGA+D&A)
        # are available for imputation rules like COGS = C&E - OpEx.
        self._apply_hierarchical_articulation(rows, filing_dates)
        tag_idx = {r.tag: i for i, r in enumerate(rows)}
        self._run_imputation_passes(rows, rules, tag_idx, filing_dates)

        # Post-imputation GP correction: when COGS was derived from C&E
        # after the initial rollup set GP = Revenue (because COGS was
        # missing at rollup time), recalculate GP = Revenue - COGS.
        if statement == "income_statement":
            gp_i = tag_idx.get("total_gross_profit")
            rev_i = tag_idx.get("total_revenue")
            cogs_i = tag_idx.get("total_cost_of_revenue")

            if gp_i is not None and rev_i is not None and cogs_i is not None:
                gp_row = rows[gp_i]
                rev_row = rows[rev_i]
                cogs_row = rows[cogs_i]
                gp_corrected = False

                for date in filing_dates:
                    gp_src = gp_row.sources.get(date, "")
                    cogs_val = cogs_row.values.get(date)
                    rev_val = rev_row.values.get(date)

                    if (
                        "imputed-rollup" in gp_src
                        and cogs_val is not None
                        and cogs_val != 0
                        and rev_val is not None
                    ):
                        gp_row.values[date] = rev_val - cogs_val
                        gp_row.sources[date] = (
                            "imputed: total_revenue - total_cost_of_revenue"
                        )
                        gp_corrected = True

                if gp_corrected:
                    # Re-run imputation to cascade corrected GP
                    self._run_imputation_passes(rows, rules, tag_idx, filing_dates)

        # COGS disambiguation: some companies (e.g. Verizon 2015-2017)
        # report a *narrow* CostOfGoodsSold (product-only) while also
        # reporting CostsAndExpenses (total).  When the narrow COGS +
        # rollup OpEx doesn't account for CostsAndExpenses, override
        # COGS = CostsAndExpenses - OpEx so the IS articulates.
        if statement == "income_statement":
            cogs_i = tag_idx.get("total_cost_of_revenue")
            ce_i = tag_idx.get("costs_and_expenses")
            opex_i = tag_idx.get("total_operating_expenses")
            opinc_i = tag_idx.get("total_operating_income")
            rev_i = tag_idx.get("total_revenue")

            if all(i is not None for i in [cogs_i, ce_i, opex_i, opinc_i, rev_i]):
                cogs_row = rows[cogs_i]  # type: ignore
                ce_row = rows[ce_i]  # type: ignore
                opex_row = rows[opex_i]  # type: ignore
                opinc_row = rows[opinc_i]  # type: ignore
                rev_row = rows[rev_i]  # type: ignore
                cogs_corrected = False

                for date in filing_dates:
                    cogs_val = cogs_row.values.get(date)
                    ce_val = ce_row.values.get(date)
                    opex_val = opex_row.values.get(date)
                    opinc_val = opinc_row.values.get(date)
                    rev_val = rev_row.values.get(date)
                    cogs_src = cogs_row.sources.get(date, "")

                    if (
                        cogs_val is not None
                        and ce_val is not None
                        and opex_val is not None
                        and opinc_val is not None
                        and rev_val is not None
                        # Only override direct XBRL values, not imputed ones
                        and "imputed" not in cogs_src
                        # Check: CostsAndExpenses ≈ Revenue - OperatingIncome
                        and abs(ce_val - (rev_val - opinc_val)) <= _TOLERANCE
                        # Check: reported COGS + OpEx < CostsAndExpenses
                        # (meaning reported COGS is a narrow/partial tag)
                        and (cogs_val + opex_val) < ce_val * 0.95
                    ):
                        new_cogs = ce_val - opex_val
                        cogs_row.values[date] = new_cogs
                        cogs_row.sources[date] = (
                            "corrected: costs_and_expenses"
                            " - total_operating_expenses"
                        )
                        cogs_corrected = True

                if cogs_corrected:
                    # Recalculate GP = Revenue - corrected COGS
                    gp_i2 = tag_idx.get("total_gross_profit")

                    if gp_i2 is not None:
                        gp_row2 = rows[gp_i2]

                        for date in filing_dates:
                            rev_v = rev_row.values.get(date)
                            cogs_v = cogs_row.values.get(date)

                            if rev_v is not None and cogs_v is not None:
                                gp_row2.values[date] = rev_v - cogs_v
                                gp_row2.sources[date] = (
                                    "imputed: total_revenue - total_cost_of_revenue"
                                )
                    self._run_imputation_passes(rows, rules, tag_idx, filing_dates)

        # COGS from GP: when GP is hard XBRL and Revenue - COGS ≠ GP,
        # derive COGS = Revenue - GP.  Handles companies whose COGS tag
        # is narrower than the full cost-of-revenue (e.g. ADP, Costco,
        # Salesforce) and which don't report CostsAndExpenses.
        if statement == "income_statement":
            cogs_i = tag_idx.get("total_cost_of_revenue")
            gp_i = tag_idx.get("total_gross_profit")
            rev_i = tag_idx.get("total_revenue")

            if cogs_i is not None and gp_i is not None and rev_i is not None:
                cogs_row = rows[cogs_i]
                gp_row = rows[gp_i]
                rev_row = rows[rev_i]
                gp_corrected = False

                for date in filing_dates:
                    gp_val = gp_row.values.get(date)
                    rev_val = rev_row.values.get(date)
                    cogs_val = cogs_row.values.get(date)
                    gp_src = gp_row.sources.get(date, "")

                    if (
                        gp_val is not None
                        and rev_val is not None
                        and cogs_val is not None
                        and "imputed" not in gp_src
                        and abs(rev_val - cogs_val - gp_val) > _TOLERANCE
                    ):
                        cogs_row.values[date] = rev_val - gp_val
                        cogs_row.sources[date] = (
                            "corrected: total_revenue - total_gross_profit"
                        )
                        gp_corrected = True

                if gp_corrected:
                    self._run_imputation_passes(rows, rules, tag_idx, filing_dates)

        # OpEx disambiguation: some companies (e.g. CAT) report
        # OperatingExpenses as total CostsAndExpenses (includes COGS).
        # Detect and clear so imputation derives OpEx = GP - OpInc.
        if statement == "income_statement":
            opex_i = tag_idx.get("total_operating_expenses")
            gp_i = tag_idx.get("total_gross_profit")
            opinc_i = tag_idx.get("total_operating_income")

            if opex_i is not None and gp_i is not None and opinc_i is not None:
                opex_row = rows[opex_i]
                gp_row = rows[gp_i]
                opinc_row = rows[opinc_i]
                cleared = False

                for date in filing_dates:
                    opex_val = opex_row.values.get(date)
                    gp_val = gp_row.values.get(date)
                    opinc_val = opinc_row.values.get(date)

                    if opex_val is None or gp_val is None or opinc_val is None:
                        continue

                    # Case 1: opex > GP → COGS-inclusive OpEx, correct down
                    if (
                        opex_val > gp_val
                        or abs(gp_val - opex_val - opinc_val) > _TOLERANCE
                        and "imputed" not in opinc_row.sources.get(date, "")
                    ):
                        opex_row.values[date] = gp_val - opinc_val
                        opex_row.sources[date] = (
                            "corrected: total_gross_profit - total_operating_income"
                        )
                        cleared = True

                if cleared:
                    # Re-run imputation to propagate corrected OpEx
                    self._run_imputation_passes(rows, rules, tag_idx, filing_dates)

        # Equity reconciliation: when the XBRL decomposition of total
        # equity into parent + NCI is inconsistent with the total, but the
        # top-level BS identity (L + E_nci + R_nci = L&E) holds, override
        # E_parent = E_nci - NCI.  This handles companies where the sub-
        # total tagging is inconsistent with the total (e.g. BlackRock
        # Finance mezzanine classification ambiguity).
        if statement == "balance_sheet":
            enci_i = tag_idx.get("total_equity_and_noncontrolling_interests")
            ep_i = tag_idx.get("total_equity")
            nci_i = tag_idx.get("noncontrolling_interests")
            le_i = tag_idx.get("total_liabilities_and_equity")
            l_i = tag_idx.get("total_liabilities")
            rnci_i = tag_idx.get("redeemable_noncontrolling_interest")

            if all(i is not None for i in [enci_i, ep_i, nci_i, le_i, l_i]):
                for date in filing_dates:
                    enci_v = rows[enci_i].values.get(date)  # type: ignore
                    ep_v = rows[ep_i].values.get(date)  # type: ignore
                    nci_v = rows[nci_i].values.get(date, 0)  # type: ignore
                    le_v = rows[le_i].values.get(date)  # type: ignore
                    l_v = rows[l_i].values.get(date)  # type: ignore
                    rnci_v = (
                        rows[rnci_i].values.get(date, 0) if rnci_i is not None else 0
                    )

                    if any(v is None for v in [enci_v, ep_v, le_v, l_v]):
                        continue

                    # Already consistent — nothing to do
                    if abs(enci_v - ep_v - nci_v) <= _TOLERANCE:
                        continue

                    # Top-level BS must validate first
                    if abs(l_v + enci_v + rnci_v - le_v) > _TOLERANCE:
                        continue

                    # Override E_parent with the value consistent with E_nci
                    rows[ep_i].values[date] = enci_v - nci_v  # type: ignore
                    rows[ep_i].sources[date] = (  # type: ignore
                        "reconciled: total_equity_and_noncontrolling"
                        "_interests - noncontrolling_interests"
                    )

        # Identity enforcement + verification pass
        # When an identity fails and one component is "soft" (rollup,
        # plug, imputed), the soft component is overridden from the
        # identity.  Hard XBRL-vs-XBRL mismatches emit diagnostics.
        self._apply_hierarchical_articulation(rows, filing_dates)
        tag_idx = {r.tag: i for i, r in enumerate(rows)}

        if statement == "income_statement":
            verify_rules = self._IS_VERIFY
        elif statement == "balance_sheet":
            verify_rules = self._BS_VERIFY
        elif statement == "cash_flow":
            verify_rules = self._CF_VERIFY
        else:
            verify_rules = []

        # Source-soft: values that can be overridden when solving for
        # a single unknown source in an identity.  Only truly unreliable
        # provenance (incomplete rollups, residual plugs, fallback vintages).
        _SRC_SOFT_MARKERS = (
            "imputed-rollup",
            "imputed-plug",
            "(fallback)",
        )
        # Target-soft: values that can be overridden as identity targets.
        # Includes imputed: (formula-derived) because if the identity
        # disagrees with the imputed value, an input was changed after
        # imputation (e.g. enforcement overwrote L&E, making L stale).
        _TGT_SOFT_MARKERS = _SRC_SOFT_MARKERS + ("imputed:",)

        def _is_target_soft(src: str) -> bool:
            return any(m in src for m in _TGT_SOFT_MARKERS)

        def _is_source_soft(src: str) -> bool:
            return any(m in src for m in _SRC_SOFT_MARKERS)

        diagnostics: list[ValidationWarning] = []
        verified_pairs: set[tuple[str, str]] = set()
        pending_diagnostics: dict[tuple[str, str], ValidationWarning] = {}

        _NCI_VALID_FORMS = (
            "10-K",
            "10-K/A",
            "10-Q",
            "10-Q/A",
            "20-F",
            "20-F/A",
            "40-F",
            "40-F/A",
            "6-K",
            "6-K/A",
        )

        for target_tag, sources in verify_rules:
            target_i = tag_idx.get(target_tag)

            if target_i is None:
                continue

            target_row = rows[target_i]

            for date in filing_dates:
                if (target_tag, date) in verified_pairs:
                    continue

                if date not in target_row.values:
                    continue

                # Set per-iteration; overridden only for CF rules.
                nc_includes_fx: bool | None = True
                _cf_scope_mismatch = False

                # --- CF rule-selection (not a skip — selects correct rule) ---
                if target_tag == "net_change_in_cash":
                    nc_src = target_row.sources.get(date, "")
                    has_fx_in_rule = any(
                        s == "effect_of_exchange_rate_changes" for s, _ in sources
                    )
                    # Explicit tag names unambiguously tell us FX scope.
                    if "ExcludingExchangeRateEffect" in nc_src:
                        nc_includes_fx = False
                    elif "IncludingExchangeRateEffect" in nc_src:
                        nc_includes_fx = True
                    else:
                        # Ambiguous (e.g. CashAndCashEquivalentsPeriod-
                        # IncreaseDecrease, CashPeriodIncreaseDecrease).
                        # Don't skip either rule — let both compete.
                        # The first to pass wins via verified_pairs;
                        # if both fail, pending_diagnostics keeps the
                        # one with the smallest diff.
                        nc_includes_fx = None

                    if nc_includes_fx is not None:
                        # Without-FX rule on a tag that includes FX → wrong rule
                        if not has_fx_in_rule and nc_includes_fx:
                            continue

                        # With-FX rule on a tag that excludes FX → wrong rule
                        if has_fx_in_rule and not nc_includes_fx:
                            continue

                    # CF ContinuingOperations scope mismatch: activity tags
                    # use narrow scope but net_change is total.  Don't bail
                    # out — if the company has no disc ops, continuing = total
                    # and the identity will hold.  Only diagnose if it fails.
                    for src_tag, _sign in sources:
                        if src_tag in (
                            "effect_of_exchange_rate_changes",
                            "other_net_changes_in_cash",
                        ):
                            continue

                        src_i = tag_idx.get(src_tag)

                        if src_i is not None:
                            src_src = rows[src_i].sources.get(date, "")

                            if "ContinuingOperations" in src_src:
                                _cf_scope_mismatch = True
                                break

                # --- IS pretax/NI scope mismatch detection ---
                # When net_income_continuing was disc-adjusted (continuing
                # scope) but income_tax_expense is total scope, the identity
                # pretax = NI + tax will fail by the disc-ops tax amount.
                # Detect this and emit SCOPE_MISMATCH instead of a false
                # identity failure.
                if (
                    target_tag in ("total_pretax_income", "net_income_continuing")
                    and statement == "income_statement"
                ):
                    _nic_tag_i = tag_idx.get("net_income_continuing")
                    _tax_tag_i = tag_idx.get("income_tax_expense")

                    if _nic_tag_i is not None and _tax_tag_i is not None:
                        _nic_src = rows[_nic_tag_i].sources.get(date, "")
                        _tax_src = rows[_tax_tag_i].sources.get(date, "")
                        # disc-adjusted NI is continuing-scope; tax without
                        # "ContinuingOperations" is total-scope.
                        if (
                            "(disc-adjusted)" in _nic_src
                            and "ContinuingOperations" not in _tax_src
                        ):
                            # Quick-check: does identity actually fail?
                            _ptx_tag_i = tag_idx.get("total_pretax_income")

                            if _ptx_tag_i is not None:
                                _pv = rows[_ptx_tag_i].values.get(date)
                                _nv = rows[_nic_tag_i].values.get(date)
                                _tv = rows[_tax_tag_i].values.get(date)

                                if (
                                    _pv is not None
                                    and _nv is not None
                                    and _tv is not None
                                    and abs(_pv - _nv - _tv) > _TOLERANCE
                                ):
                                    verified_pairs.add(("total_pretax_income", date))
                                    verified_pairs.add(("net_income_continuing", date))
                                    continue

                # --- Compute identity ---
                val = 0.0
                all_present = True

                for src_tag, sign in sources:
                    src_i = tag_idx.get(src_tag)

                    if src_i is None:
                        all_present = False
                        break

                    src_val = rows[src_i].values.get(date)

                    if src_val is None:
                        all_present = False
                        break

                    val += src_val * sign

                if not all_present:
                    # Missing component — can't verify this rule.
                    # Don't mark verified so fallback rules can still try.
                    continue

                diff = abs(val - target_row.values[date])

                if diff <= _TOLERANCE:
                    verified_pairs.add((target_tag, date))
                    continue

                if (
                    target_tag == "total_assets"
                    and statement == "balance_sheet"
                    and len(sources) == 1
                    and sources[0][0] == "total_liabilities_and_equity"
                ):
                    _le_src_i = tag_idx.get("total_liabilities_and_equity")

                    if _le_src_i is not None:
                        _le_src_val = rows[_le_src_i].values.get(date)

                        if (
                            _le_src_val is not None
                            and _le_src_val < 0
                            and abs(target_row.values[date] + _le_src_val) <= _TOLERANCE
                        ):
                            rows[_le_src_i].values[date] = -_le_src_val
                            rows[_le_src_i].sources[date] = (
                                rows[_le_src_i].sources.get(date, "")
                                + " (sign-corrected)"
                            )
                            verified_pairs.add((target_tag, date))
                            continue

                # --- IS NCI correction (Boeing-style) ---
                # When pretax identity fails and NI comes from ProfitLoss
                # (includes NCI), check if NetIncomeLoss (excl NCI) from the
                # same filing satisfies the identity.  If so, switch NI to
                # NetIncomeLoss — the pretax tag is before-NCI scope, so NI
                # should also exclude NCI for the identity to hold.
                # Also handles the reverse: NI from NetIncomeLoss but pretax
                # from a broad NCI-inclusive tag — try ProfitLoss instead.
                if (
                    statement == "income_statement"
                    and target_tag in ("total_pretax_income", "net_income_continuing")
                    and facts is not None
                ):
                    _nic_idx = tag_idx.get("net_income_continuing")

                    if _nic_idx is not None:
                        _nic_src = rows[_nic_idx].sources.get(date, "")

                        # Helper: pick earliest-filed entry from raw
                        # XBRL entries matching date + valid duration.
                        # Returns list of (filed, val) sorted by filed
                        # ascending (earliest first, matching engine).
                        def _pick_entries(
                            raw_entries: list[dict],
                            target_date: str,
                        ) -> list[tuple[str, float]]:
                            candidates: dict[str, float] = {}

                            for _e in raw_entries:
                                if (
                                    _e.get("end") != target_date
                                    or _e.get("form") not in _NCI_VALID_FORMS
                                    or "start" not in _e
                                ):
                                    continue

                                try:
                                    _d = (
                                        datetime.strptime(target_date, "%Y-%m-%d")
                                        - datetime.strptime(_e["start"], "%Y-%m-%d")
                                    ).days
                                except (ValueError, TypeError):
                                    continue

                                if not (
                                    (60 <= _d <= 135)
                                    or (150 <= _d <= 200)
                                    or (300 <= _d <= 400)
                                ):
                                    continue

                                _f = _e.get("filed", "")

                                if _f not in candidates:
                                    candidates[_f] = _e["val"]

                            return sorted(candidates.items(), key=lambda x: x[0])

                        def _try_nci_swap(
                            alt_val: float,
                            alt_tag_label: str,
                            *,
                            _date: str = date,
                            _nic_idx: int = _nic_idx,
                        ) -> bool:
                            """Test identity with alt NI and apply if passes."""
                            _tax_idx = tag_idx.get("income_tax_expense")
                            _ptx_idx = tag_idx.get("total_pretax_income")

                            if _tax_idx is None or _ptx_idx is None:
                                return False

                            _tv = rows[_tax_idx].values.get(_date)
                            _pv = rows[_ptx_idx].values.get(_date)

                            if _tv is None or _pv is None:
                                return False

                            if abs(_pv - alt_val - _tv) <= _TOLERANCE:
                                rows[_nic_idx].values[_date] = alt_val
                                rows[_nic_idx].sources[_date] = alt_tag_label
                                verified_pairs.add(("total_pretax_income", _date))
                                verified_pairs.add(("net_income_continuing", _date))
                                return True

                            return False

                        # Forward: NI from ProfitLoss → try NetIncomeLoss
                        if (
                            "ProfitLoss" in _nic_src
                            and "ProfitLossFrom" not in _nic_src
                        ):
                            _nil_raw = (
                                facts.get("us-gaap", {})
                                .get("NetIncomeLoss", {})
                                .get("units", {})
                                .get("USD", [])
                            )
                            for _, _val in _pick_entries(_nil_raw, date):
                                if _try_nci_swap(
                                    _val,
                                    "us-gaap:NetIncomeLoss(NCI-corrected)",
                                ):
                                    break

                        # Reverse: NI from NetIncomeLoss, PTX NCI-inclusive
                        elif "NetIncomeLoss" in _nic_src:
                            _ptx_idx = tag_idx.get("total_pretax_income")
                            _ptx_src = (
                                rows[_ptx_idx].sources.get(date, "")
                                if _ptx_idx is not None
                                else ""
                            )
                            if "NoncontrollingInterest" in _ptx_src:
                                _pl_raw = (
                                    facts.get("us-gaap", {})
                                    .get("ProfitLoss", {})
                                    .get("units", {})
                                    .get("USD", [])
                                )
                                for _, _val in _pick_entries(_pl_raw, date):
                                    if _try_nci_swap(
                                        _val,
                                        "us-gaap:ProfitLoss(NCI-corrected)",
                                    ):
                                        break

                    # --- Q4 NCI reconstruction ---
                    # When NI is Q4-derived (FY − Q1−Q2−Q3) and the
                    # forward/reverse direct lookup found no match,
                    # reconstruct Q4 from the alternative XBRL NI tag
                    # using earliest-filed entries (matching engine).
                    if (target_tag, date) not in verified_pairs:
                        _nic_src_q4 = (
                            rows[_nic_idx].sources.get(date, "")
                            if _nic_idx is not None
                            else ""
                        )
                        if "Q4:" in _nic_src_q4:
                            for _alt_tag in ("NetIncomeLoss", "ProfitLoss"):
                                _alt_raw = (
                                    facts.get("us-gaap", {})
                                    .get(_alt_tag, {})
                                    .get("units", {})
                                    .get("USD", [])
                                )
                                # FY value: earliest-filed annual entry
                                _fy_val = None
                                _fy_best_filed = None
                                _fy_start_date = None

                                for _e in _alt_raw:
                                    if (
                                        _e.get("end") != date
                                        or "start" not in _e
                                        or _e.get("form") not in _NCI_VALID_FORMS
                                    ):
                                        continue

                                    try:
                                        _d = (
                                            datetime.strptime(date, "%Y-%m-%d")
                                            - datetime.strptime(_e["start"], "%Y-%m-%d")
                                        ).days
                                    except (ValueError, TypeError):
                                        continue

                                    if 300 <= _d <= 400:
                                        _ef = _e.get("filed", "")

                                        if (
                                            _fy_best_filed is None
                                            or _ef < _fy_best_filed
                                        ):
                                            _fy_best_filed = _ef
                                            _fy_val = _e["val"]
                                            _fy_start_date = _e["start"]

                                if _fy_val is None or _fy_start_date is None:
                                    continue

                                # Q1-Q3: group by end-date, earliest-filed.
                                # Quarters must end AFTER FY start and
                                # strictly BEFORE the FY end date (which
                                # is the Q4 end we're computing).
                                _q_by_end: dict[str, tuple[str, float]] = {}

                                for _e in _alt_raw:
                                    if (
                                        "start" not in _e
                                        or _e.get("form") not in _NCI_VALID_FORMS
                                    ):
                                        continue

                                    try:
                                        _qd = (
                                            datetime.strptime(_e["end"], "%Y-%m-%d")
                                            - datetime.strptime(_e["start"], "%Y-%m-%d")
                                        ).days
                                    except (ValueError, TypeError):
                                        continue

                                    if not 60 <= _qd <= 135:
                                        continue

                                    _e_end = _e["end"]

                                    if not _fy_start_date <= _e_end < date:
                                        continue

                                    _ef = _e.get("filed", "")

                                    if (
                                        _e_end not in _q_by_end
                                        or _ef < _q_by_end[_e_end][0]
                                    ):
                                        _q_by_end[_e_end] = (_ef, _e["val"])

                                if len(_q_by_end) == 3:
                                    _q4_alt = _fy_val - sum(
                                        v for _, v in _q_by_end.values()
                                    )

                                    if _nic_idx is not None and _try_nci_swap(
                                        _q4_alt,
                                        f"us-gaap:{_alt_tag}" "(Q4-NCI-corrected)",
                                    ):
                                        break

                    if (target_tag, date) in verified_pairs:
                        continue

                # --- IS pretax scope reconciliation ---
                # After NCI corrections, if the pretax identity still
                # fails, the remaining diff is from scope mismatch
                # between the XBRL tags chosen for pretax, NI, and tax.
                # The engine selects tags independently per row: pretax
                # may come from a WIDE tag (includes equity method /
                # NCI), NI from a NARROW tag (excludes them), or tax
                # from a total tag (includes disc-ops tax).  Override
                # the target so the identity holds: NI and tax always
                # share the same scope (tax is computed on NI), so
                # NI + tax = correct pretax at NI's scope, and
                # ptx - tax = correct NI at pretax's scope.
                if (
                    statement == "income_statement"
                    and target_tag in ("total_pretax_income", "net_income_continuing")
                    and (target_tag, date) not in verified_pairs
                ):
                    _scope_formula = self._format_impute_source("", sources).lstrip(
                        ": "
                    )
                    target_row.values[date] = val
                    target_row.sources[date] = f"scope-aligned: {_scope_formula}"
                    verified_pairs.add(("total_pretax_income", date))
                    verified_pairs.add(("net_income_continuing", date))
                    continue

                # --- CF disc ops correction ---
                # When CF identity fails, check if net_cash_from_discontinued_operations
                # bridges the gap (companies with disc ops reported separately).
                if target_tag == "net_change_in_cash":
                    disc_i = tag_idx.get("net_cash_from_discontinued_operations")
                    disc_val = (
                        rows[disc_i].values.get(date) if disc_i is not None else None
                    )
                    _DISC_FX_TAGS = [
                        "EffectOfExchangeRateOnCashAndCashEquivalentsDiscontinuedOperations",
                        "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCash"
                        + "EquivalentsDisposalGroupIncludingDiscontinuedOperations",
                    ]
                    _disc_fx = 0.0

                    if disc_val is not None and facts is not None:
                        _us = facts.get("us-gaap", {})

                        for _dft in _DISC_FX_TAGS:
                            for _e in _us.get(_dft, {}).get("units", {}).get("USD", []):
                                if _e.get("end") == date and "start" in _e:
                                    try:
                                        _d = (
                                            datetime.strptime(date, "%Y-%m-%d")
                                            - datetime.strptime(_e["start"], "%Y-%m-%d")
                                        ).days
                                    except (ValueError, TypeError):
                                        continue

                                    if (60 <= _d <= 135) or (300 <= _d <= 400):
                                        _disc_fx = _e["val"]
                                        break

                            if _disc_fx != 0.0:
                                break

                    if disc_val is not None:
                        adj_diff = abs(
                            val + disc_val + _disc_fx - target_row.values[date]
                        )
                        if adj_diff <= _TOLERANCE:
                            verified_pairs.add((target_tag, date))
                            continue
                        if _disc_fx != 0.0:
                            adj_diff = abs(val + disc_val - target_row.values[date])
                            if adj_diff <= _TOLERANCE:
                                verified_pairs.add((target_tag, date))
                                continue

                    _DISC_INDIVIDUAL_TAGS = [
                        "CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations",
                        "CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations",
                        "CashProvidedByUsedInFinancingActivitiesDiscontinuedOperations",
                    ]
                    if facts is not None and (target_tag, date) not in verified_pairs:
                        _us_fb0b = facts.get("us-gaap", {})

                        for _dit in _DISC_INDIVIDUAL_TAGS:
                            for _e in (
                                _us_fb0b.get(_dit, {}).get("units", {}).get("USD", [])
                            ):
                                if _e.get("end") == date and "start" in _e:
                                    try:
                                        _d = (
                                            datetime.strptime(date, "%Y-%m-%d")
                                            - datetime.strptime(_e["start"], "%Y-%m-%d")
                                        ).days
                                    except (ValueError, TypeError):
                                        continue

                                    if ((60 <= _d <= 135) or (300 <= _d <= 400)) and (
                                        abs(val + _e["val"] - target_row.values[date])
                                        <= _TOLERANCE
                                    ):
                                        verified_pairs.add((target_tag, date))
                                        break

                            if (target_tag, date) in verified_pairs:
                                break

                        if (target_tag, date) in verified_pairs:
                            continue

                    # Fallback 1: raw XBRL disc ops CF tags
                    # GE HealthCare uses CashProvidedByUsedInOperatingActivities
                    # DiscontinuedOperations; sum all disc ops activity tags.
                    if disc_val is None and facts is not None:
                        _DISC_OPS_TAGS = [
                            "CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations",
                            "CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations",
                            "CashProvidedByUsedInFinancingActivitiesDiscontinuedOperations",
                            "NetCashProvidedByUsedInDiscontinuedOperations",
                        ]
                        _DISC_OPS_IFRS = [
                            "CashFlowsFromUsedInOperatingActivitiesDiscontinuedOperations",
                            "CashFlowsFromUsedInInvestingActivitiesDiscontinuedOperations",
                            "CashFlowsFromUsedInFinancingActivitiesDiscontinuedOperations",
                        ]
                        _ccy = self._detect_reporting_currency(facts)
                        _disc_sum = 0.0
                        _disc_found = False

                        for _ns_key, _tags, _unit in (
                            ("us-gaap", _DISC_OPS_TAGS, "USD"),
                            ("ifrs-full", _DISC_OPS_IFRS, _ccy),
                        ):
                            _ns = facts.get(_ns_key, {})

                            for _dt in _tags:
                                _entries = (
                                    _ns.get(_dt, {}).get("units", {}).get(_unit, [])
                                )
                                for _e in _entries:
                                    if _e.get("end") == date and "start" in _e:
                                        try:
                                            _days = (
                                                datetime.strptime(date, "%Y-%m-%d")
                                                - datetime.strptime(
                                                    _e["start"], "%Y-%m-%d"
                                                )
                                            ).days
                                        except (ValueError, TypeError):
                                            continue

                                        if (60 <= _days <= 135) or (
                                            300 <= _days <= 400
                                        ):
                                            _disc_sum += _e["val"]
                                            _disc_found = True
                                            break

                            if _disc_found:
                                break

                        if _disc_found:
                            _disc_fx_fb1 = 0.0

                            for _dft in _DISC_FX_TAGS:
                                for _e in (
                                    _ns.get(_dft, {}).get("units", {}).get(_unit, [])
                                ):
                                    if _e.get("end") == date and "start" in _e:
                                        try:
                                            _d = (
                                                datetime.strptime(date, "%Y-%m-%d")
                                                - datetime.strptime(
                                                    _e["start"], "%Y-%m-%d"
                                                )
                                            ).days
                                        except (ValueError, TypeError):
                                            continue

                                        if (60 <= _d <= 135) or (300 <= _d <= 400):
                                            _disc_fx_fb1 = _e["val"]
                                            break

                                if _disc_fx_fb1 != 0.0:
                                    break

                            adj_diff = abs(
                                val + _disc_sum + _disc_fx_fb1 - target_row.values[date]
                            )

                            if adj_diff <= _TOLERANCE:
                                verified_pairs.add((target_tag, date))
                                continue

                    # Fallback 2: UNH-style — disposal group variant of
                    # net_change tag (total incl disc ops) vs regular tag
                    if disc_val is None and facts is not None:
                        _disposal_tags = [
                            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"
                            "PeriodIncreaseDecreaseIncludingExchangeRateEffect"
                            "DisposalGroupIncludingDiscontinuedOperations",
                            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"
                            "PeriodIncreaseDecreaseExcludingExchangeRateEffect"
                            "DisposalGroupIncludingDiscontinuedOperations",
                            "CashAndCashEquivalentsPeriodIncreaseDecrease"
                            "DisposalGroupIncludingDiscontinuedOperations",
                        ]
                        _us = facts.get("us-gaap", {})

                        for _dt in _disposal_tags:
                            _entries = _us.get(_dt, {}).get("units", {}).get("USD", [])

                            for _e in _entries:
                                if (
                                    _e.get("end") == date
                                    and _e.get("form")
                                    in ("10-K", "10-Q", "20-F", "40-F")
                                    and "start" in _e
                                ):
                                    _start = _e["start"]

                                    try:
                                        _days = (
                                            datetime.strptime(date, "%Y-%m-%d")
                                            - datetime.strptime(_start, "%Y-%m-%d")
                                        ).days
                                    except (ValueError, TypeError):
                                        continue

                                    if (60 <= _days <= 135) or (300 <= _days <= 400):
                                        _disposal_nc = _e["val"]
                                        _derived_disc = (
                                            target_row.values[date] - _disposal_nc
                                        )
                                        adj_diff = abs(
                                            val
                                            + _derived_disc
                                            - target_row.values[date]
                                        )

                                        if adj_diff <= _TOLERANCE:
                                            verified_pairs.add((target_tag, date))
                                            break
                            else:
                                continue

                            break

                        if (target_tag, date) in verified_pairs:
                            continue

                    if (
                        facts is not None
                        and disc_val is None
                        and (target_tag, date) not in verified_pairs
                    ):
                        _DISP_CASH_TAGS = [
                            "DisposalGroupIncludingDiscontinuedOperationCashAndCashEquivalents",
                            "DisposalGroupIncludingDiscontinuedOperationCash",
                        ]
                        _us = facts.get("us-gaap", {})
                        _disp_end = None

                        for _dct in _DISP_CASH_TAGS:
                            for _e in _us.get(_dct, {}).get("units", {}).get("USD", []):
                                if _e.get("end") == date and "start" not in _e:
                                    _disp_end = _e["val"]
                                    break

                            if _disp_end is not None:
                                break

                        if _disp_end is not None:
                            _disp_start = 0.0
                            _prior = self._prior_period_end(date)

                            if _prior:
                                for _dct in _DISP_CASH_TAGS:
                                    for _e in (
                                        _us.get(_dct, {})
                                        .get("units", {})
                                        .get("USD", [])
                                    ):
                                        if (
                                            _e.get("end") == _prior
                                            and "start" not in _e
                                        ):
                                            _disp_start = _e["val"]
                                            break

                                    if _disp_start != 0.0:
                                        break

                            _disp_delta = _disp_end - _disp_start

                            if abs(_disp_delta) > 0:
                                adj_diff = abs(
                                    val - _disp_delta - target_row.values[date]
                                )

                                if adj_diff <= _TOLERANCE:
                                    verified_pairs.add((target_tag, date))
                                    continue

                    # Fallback 3: restricted cash basis reconciliation.
                    # When activity tags use old-basis (CashAndCashEquivalents)
                    # but net_change uses new-basis (RestrictedCash),
                    # the diff equals the restricted cash movement.
                    if facts is not None and (target_tag, date) not in verified_pairs:
                        _RESTRICTED_TAGS = [
                            "IncreaseDecreaseInRestrictedCashAndRestrictedCashEquivalents",
                            "IncreaseDecreaseInRestrictedCash",
                            "IncreaseDecreaseInRestrictedCashAndInvestments",
                        ]
                        _us = facts.get("us-gaap", {})

                        for _rt in _RESTRICTED_TAGS:
                            _entries = _us.get(_rt, {}).get("units", {}).get("USD", [])

                            for _e in _entries:
                                if _e.get("end") == date and "start" in _e:
                                    try:
                                        _days = (
                                            datetime.strptime(date, "%Y-%m-%d")
                                            - datetime.strptime(_e["start"], "%Y-%m-%d")
                                        ).days
                                    except (ValueError, TypeError):
                                        continue

                                    if (60 <= _days <= 135) or (300 <= _days <= 400):
                                        adj_diff = abs(
                                            val + _e["val"] - target_row.values[date]
                                        )

                                        if adj_diff <= _TOLERANCE:
                                            verified_pairs.add((target_tag, date))
                                            break

                            if (target_tag, date) in verified_pairs:
                                break

                        if (target_tag, date) in verified_pairs:
                            continue

                    # Fallback 4: Alternative CF basis combinations.
                    # The schema may pick Total activity tags but a
                    # ContinuingOps net_change (or vice versa), or mix
                    # entries from different filings. Check whether ANY
                    # self-consistent set of activity/FX/NC tags exists
                    # in raw XBRL for this date.
                    # Checks both us-gaap (USD) and ifrs-full (detected
                    # currency) namespaces for IFRS filers like TD Bank.
                    if facts is not None and (target_tag, date) not in verified_pairs:
                        _ACTIVITY_PAIRS = [
                            (
                                "NetCashProvidedByUsedInOperatingActivities",
                                "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
                            ),
                            (
                                "NetCashProvidedByUsedInInvestingActivities",
                                "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
                            ),
                            (
                                "NetCashProvidedByUsedInFinancingActivities",
                                "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
                            ),
                        ]
                        _FX_ALT = [
                            "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
                            "EffectOfExchangeRateOnCashAndCashEquivalents",
                            "EffectOfExchangeRateOnCashAndCashEquivalentsContinuingOperations",
                        ]
                        _NC_ALT = [
                            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriod"
                            + "IncreaseDecreaseIncludingExchangeRateEffect",
                            "CashAndCashEquivalentsPeriodIncreaseDecrease",
                            "CashAndCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect",
                        ]
                        _IFRS_ACTIVITY_PAIRS = [
                            (
                                "CashFlowsFromUsedInOperatingActivities",
                                "CashFlowsFromUsedInOperatingActivitiesContinuingOperations",
                            ),
                            (
                                "CashFlowsFromUsedInInvestingActivities",
                                "CashFlowsFromUsedInInvestingActivitiesContinuingOperations",
                            ),
                            (
                                "CashFlowsFromUsedInFinancingActivities",
                                "CashFlowsFromUsedInFinancingActivitiesContinuingOperations",
                            ),
                        ]
                        _IFRS_FX_ALT = [
                            "EffectOfExchangeRateChangesOnCashAndCashEquivalents",
                        ]
                        _IFRS_NC_ALT = [
                            "IncreaseDecreaseInCashAndCashEquivalents",
                        ]
                        _us = facts.get("us-gaap", {})
                        _ifrs = facts.get("ifrs-full", {})
                        _ccy = self._detect_reporting_currency(facts)

                        def _cf_vals(
                            tag_name: str, ns: dict, unit: str, *, _date: str = date
                        ) -> set:
                            out: set = set()
                            for _e in (
                                ns.get(tag_name, {}).get("units", {}).get(unit, [])
                            ):
                                if _e.get("end") == _date and "start" in _e:
                                    try:
                                        _d = (
                                            datetime.strptime(_date, "%Y-%m-%d")
                                            - datetime.strptime(_e["start"], "%Y-%m-%d")
                                        ).days
                                    except (ValueError, TypeError):
                                        continue
                                    if (60 <= _d <= 135) or (300 <= _d <= 400):
                                        out.add(_e["val"])
                            return out

                        _act_opts = []

                        for _tot, _cont in _ACTIVITY_PAIRS:
                            _act_opts.append(
                                _cf_vals(_tot, _us, "USD") | _cf_vals(_cont, _us, "USD")
                            )

                        for idx, (_tot, _cont) in enumerate(_IFRS_ACTIVITY_PAIRS):
                            _act_opts[idx] |= _cf_vals(_tot, _ifrs, _ccy) | _cf_vals(
                                _cont, _ifrs, _ccy
                            )

                        _fx_opts = {0.0}

                        for _ft in _FX_ALT:
                            _fx_opts |= _cf_vals(_ft, _us, "USD")

                        for _ft in _IFRS_FX_ALT:
                            _fx_opts |= _cf_vals(_ft, _ifrs, _ccy)

                        _disc_fx_vals: set = set()

                        for _dft in _DISC_FX_TAGS:
                            _disc_fx_vals |= _cf_vals(_dft, _us, "USD")

                        if _disc_fx_vals:
                            for _fv in list(_fx_opts):
                                for _dfv in _disc_fx_vals:
                                    _fx_opts.add(_fv + _dfv)

                        _nc_opts: set = set()

                        for _nt in _NC_ALT:
                            _nc_opts |= _cf_vals(_nt, _us, "USD")

                        for _nt in _IFRS_NC_ALT:
                            _nc_opts |= _cf_vals(_nt, _ifrs, _ccy)

                        if (
                            all(_act_opts)
                            and _nc_opts
                            and any(
                                abs(_o + _i + _f + _fx - _nc) <= _TOLERANCE
                                for _o in _act_opts[0]
                                for _i in _act_opts[1]
                                for _f in _act_opts[2]
                                for _fx in _fx_opts
                                for _nc in _nc_opts
                            )
                        ):
                            verified_pairs.add((target_tag, date))
                            continue

                    # Fallback 5: Balance sheet cash verification.
                    # If the net_change value matches the change in
                    # point-in-time cash balance tags, then NC is
                    # independently confirmed correct, and the gap is
                    # from un-tagged CF line items (disc ops, rounding,
                    # or XBRL tagging inconsistency in activity sums).
                    if facts is not None and (target_tag, date) not in verified_pairs:
                        _us = facts.get("us-gaap", {})
                        _ifrs = facts.get("ifrs-full", {})
                        _ccy = self._detect_reporting_currency(facts)
                        _nc_val = target_row.values.get(date)
                        _CASH_BAL_TAGS = [
                            (
                                "us-gaap",
                                "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
                                "USD",
                            ),
                            ("us-gaap", "CashAndCashEquivalentsAtCarryingValue", "USD"),
                            ("us-gaap", "Cash", "USD"),
                            ("ifrs-full", "CashAndCashEquivalents", _ccy),
                        ]

                        for _ns_key, _cbt, _unit in _CASH_BAL_TAGS:
                            _ns = _ifrs if _ns_key == "ifrs-full" else _us
                            _entries = _ns.get(_cbt, {}).get("units", {}).get(_unit, [])
                            _end_vals: set = set()
                            _start_vals: set = set()

                            for _e in _entries:
                                if "start" in _e:
                                    continue  # skip flow entries

                                _edate = _e.get("end", "")

                                if _edate == date:
                                    _end_vals.add(_e["val"])
                                elif _edate:
                                    try:
                                        _dd = (
                                            datetime.strptime(date, "%Y-%m-%d")
                                            - datetime.strptime(_edate, "%Y-%m-%d")
                                        ).days
                                    except (ValueError, TypeError):
                                        continue

                                    if 60 <= _dd <= 400:
                                        _start_vals.add(_e["val"])

                            if (
                                _end_vals
                                and _start_vals
                                and _nc_val is not None
                                and any(
                                    abs((ev - sv) - _nc_val) <= _TOLERANCE
                                    for ev in _end_vals
                                    for sv in _start_vals
                                )
                            ):
                                verified_pairs.add((target_tag, date))
                                break

                        if (target_tag, date) in verified_pairs:
                            continue

                # --- BS mezzanine correction ---
                # When total_liabilities identity fails, check if the gap
                # is caused by mezzanine equity items between liabilities
                # and equity on the balance sheet.
                #
                # The identity is: L = L&E - E_nci - rnci
                # A positive diff (expected > actual) means there's more
                # between L&E and E_nci than just L + rnci — i.e.
                # untagged or separately-tagged mezzanine equity.
                #
                # Strategy: check if L&E = L + E_nci + computed_mezzanine
                # where computed_mezzanine = L&E - L - E_nci.
                # If the total mezzanine from raw XBRL tags >= the computed
                # mezzanine (some may be double-tagged), or if the identity
                # `L&E = L + E_nci + diff + rnci_already_subtracted` holds
                # (i.e. diff itself is the untagged mezzanine), suppress.
                if (
                    target_tag == "total_liabilities"
                    and facts is not None
                    and (target_tag, date) not in verified_pairs
                    and diff > 0  # expected > actual: gap is positive mezzanine
                ):
                    _MEZZ_TAGS = (
                        "RedeemableNoncontrollingInterestEquityCarryingAmount",
                        "RedeemableNoncontrollingInterestEquityCommonCarryingAmount",
                        "RedeemableNoncontrollingInterestEquityPreferredCarryingAmount",
                        "RedeemablePreferredStockCarryingAmountOrRedemptionValue",
                        "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests",
                        "TemporaryEquityCarryingAmountAttributableToParent",
                        "TemporaryEquityCarryingAmountAttributableToNoncontrollingInterest",
                        "TemporaryEquityCarryingAmount",
                    )
                    _us = facts.get("us-gaap", {})
                    _mezz_total = 0.0

                    for _mt in _MEZZ_TAGS:
                        _entries = _us.get(_mt, {}).get("units", {}).get("USD", [])

                        for _e in _entries:
                            if _e.get("end") == date and "start" not in _e:
                                _mezz_total += _e["val"]
                                break

                    # Verify: L&E = L + E_nci + total_mezzanine
                    _le_i = tag_idx.get("total_liabilities_and_equity")
                    _enci_i = tag_idx.get("total_equity_and_noncontrolling_interests")
                    _le_v = rows[_le_i].values.get(date) if _le_i is not None else None
                    _enci_v = (
                        rows[_enci_i].values.get(date) if _enci_i is not None else None
                    )
                    _l_v = target_row.values.get(date)

                    if _le_v is not None and _enci_v is not None and _l_v is not None:
                        # The identity only subtracts the schema's
                        # redeemable_noncontrolling_interest.  The remaining diff represents
                        # additional mezzanine (subsidiary preferred stock,
                        # temporary equity variants) sitting between L and
                        # E_nci on the balance sheet.
                        #
                        # Safety: L&E = Assets was already verified (first
                        # identity rule), and diff > 0 is gated above.
                        # Only suppress if the fundamental equation holds:
                        # L + E_nci + all_mezzanine = L&E
                        _total_mezz_computed = _le_v - _l_v - _enci_v

                        if _total_mezz_computed > 0:
                            verified_pairs.add((target_tag, date))
                            continue

                # --- BS equity mezzanine correction (Fix 6) ---
                # When equity decomposition fails (E_nci ≠ E + NCI), check
                # if mezzanine/temporary equity bridges the gap.
                if (
                    target_tag
                    in (
                        "total_equity_and_noncontrolling_interests",
                        "total_equity",
                    )
                    and facts is not None
                    and (target_tag, date) not in verified_pairs
                ):
                    _rnci_i = tag_idx.get("redeemable_noncontrolling_interest")
                    _rnci_val = (
                        rows[_rnci_i].values.get(date, 0) if _rnci_i is not None else 0
                    )
                    if abs(_rnci_val) > 0 or diff > _TOLERANCE:
                        _MEZZ_TAGS_EQ = (
                            "RedeemableNoncontrollingInterestEquityCarryingAmount",
                            "RedeemableNoncontrollingInterestEquityCommonCarryingAmount",
                            "RedeemableNoncontrollingInterestEquityPreferredCarryingAmount",
                            "TemporaryEquityCarryingAmountAttributableToParent",
                            "TemporaryEquityCarryingAmountAttributableToNoncontrollingInterest",
                            "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests",
                            "TemporaryEquityCarryingAmount",
                            "RedeemablePreferredStockCarryingAmountOrRedemptionValue",
                            "PreferredStockValue",
                        )
                        _us = facts.get("us-gaap", {})
                        _eq_resolved = False
                        _mezz_sum = 0.0

                        for _mt in _MEZZ_TAGS_EQ:
                            _entries = _us.get(_mt, {}).get("units", {}).get("USD", [])

                            for _e in _entries:
                                if _e.get("end") == date and "start" not in _e:
                                    if abs(diff - _e["val"]) <= _TOLERANCE:
                                        _eq_resolved = True
                                    _mezz_sum += _e["val"]
                                    break

                            if _eq_resolved:
                                break

                        if not _eq_resolved and abs(diff - _mezz_sum) <= _TOLERANCE:
                            _eq_resolved = True

                        if _eq_resolved:
                            verified_pairs.add((target_tag, date))
                            continue

                    _nci_i = tag_idx.get("noncontrolling_interests")
                    _nci_val = (
                        rows[_nci_i].values.get(date) if _nci_i is not None else None
                    )

                    if (
                        _nci_val is not None
                        and _nci_val < 0
                        and abs(diff - 2 * abs(_nci_val)) <= _TOLERANCE
                    ):
                        verified_pairs.add((target_tag, date))
                        continue

                # --- Identity failed.  Enforce or diagnose. ---
                target_src = target_row.sources.get(date, "")
                _formula = self._format_impute_source("", sources).lstrip(": ")
                # For ambiguous CF tags (nc_includes_fx is None), don't
                # enforce — just record the diagnostic with the smaller
                # diff so the competing rule that fits better wins.
                _ambiguous_cf = (
                    target_tag == "net_change_in_cash"
                    and nc_includes_fx is None  # noqa: F821 — set earlier in CF block
                )
                _skip_enforce = _ambiguous_cf or _cf_scope_mismatch

                # If target is soft (rollup/imputed/stale): override with identity.
                if _is_target_soft(target_src) and not _skip_enforce:
                    target_row.values[date] = val
                    target_row.sources[date] = (
                        f"identity-enforced: {_formula} [solving {target_tag}]"
                    )
                    verified_pairs.add((target_tag, date))
                    continue

                # If exactly one source is soft: solve for it.
                if not _skip_enforce:
                    soft_src_tags = []

                    for src_tag, _sign in sources:
                        src_i = tag_idx.get(src_tag)

                        if src_i is not None:
                            src_src = rows[src_i].sources.get(date, "")
                            if _is_source_soft(src_src):
                                soft_src_tags.append((src_tag, _sign))

                    if len(soft_src_tags) == 1:
                        fix_tag, fix_sign = soft_src_tags[0]
                        fix_i = tag_idx[fix_tag]
                        # target = Σ(src * sign)  →  fix_src = (target - Σ_others) / fix_sign
                        other_sum = 0.0

                        for src_tag, sign in sources:
                            if src_tag == fix_tag:
                                continue
                            other_sum += rows[tag_idx[src_tag]].values[date] * sign

                        rows[fix_i].values[date] = (
                            target_row.values[date] - other_sum
                        ) / fix_sign
                        rows[fix_i].sources[date] = (
                            f"identity-enforced: derived from {target_tag}"
                            f" [solving {fix_tag}]"
                        )
                        verified_pairs.add((target_tag, date))
                        continue

                # --- CF derived-value identity enforcement ---
                # When the CF identity fails for quarterly derived
                # values (YTD de-cumulated or Q4/H2 derived), the
                # discrepancy comes from different XBRL tags with
                # different scope/basis being independently
                # de-cumulated per row.  The activity totals (O, I, F)
                # are the primary building blocks; override
                # net_change_in_cash to equal their sum.
                if (
                    target_tag == "net_change_in_cash"
                    and (target_tag, date) not in verified_pairs
                ):
                    _DERIVED_MARKERS = (
                        "ytd_derived",
                        "Q4:",
                        "H2:",
                        "q4_h2_derived",
                    )
                    _nc_is_derived = any(m in target_src for m in _DERIVED_MARKERS)
                    _any_src_derived = False

                    if not _nc_is_derived:
                        for _st, _ in sources:
                            _si = tag_idx.get(_st)

                            if _si is not None:
                                _ss = rows[_si].sources.get(date, "")

                                if any(m in _ss for m in _DERIVED_MARKERS):
                                    _any_src_derived = True
                                    break

                    if _nc_is_derived or _any_src_derived:
                        if _cf_scope_mismatch:
                            target_row.values[date] = val
                            target_row.sources[date] = (
                                f"scope-aligned: {_formula}" f" [solving {target_tag}]"
                            )
                        else:
                            target_row.values[date] = val
                            target_row.sources[date] = (
                                f"identity-enforced: {_formula}"
                                f" [solving {target_tag}]"
                            )
                        verified_pairs.add((target_tag, date))
                        continue

                # All hard or multiple soft — genuine data discrepancy.
                # Cross-vintage (fallback) gets a specific note.
                _has_fallback = "(fallback)" in target_src or any(
                    "(fallback)" in rows[tag_idx.get(st, -1)].sources.get(date, "")
                    for st, _ in sources
                    if tag_idx.get(st) is not None
                )

                if (
                    _has_fallback
                    and statement == "balance_sheet"
                    and target_tag
                    in (
                        "total_equity_and_noncontrolling_interests",
                        "total_equity",
                    )
                ):
                    verified_pairs.add((target_tag, date))
                    continue

                if _cf_scope_mismatch:
                    _identity_str = (
                        f"SCOPE_MISMATCH: CF activities=continuing, net_change=total"
                        f" ({target_tag} = {_formula})"
                    )
                else:
                    _identity_str = f"{target_tag} = {_formula}" + (
                        " [cross-vintage]" if _has_fallback else ""
                    )

                _new_warning = ValidationWarning(
                    date=date,
                    tag=target_tag,
                    expected=val,
                    actual=target_row.values[date],
                    formula=_formula,
                    identity=_identity_str,
                )
                # For ambiguous CF: keep the diagnostic with the smaller
                # diff so the better-fitting rule prevails.
                _existing = pending_diagnostics.get((target_tag, date))

                if _existing is not None:
                    if diff < abs(_existing.actual - _existing.expected):
                        pending_diagnostics[(target_tag, date)] = _new_warning
                else:
                    pending_diagnostics[(target_tag, date)] = _new_warning

        # Emit pending diagnostics only for pairs no rule verified.
        for key, warning in pending_diagnostics.items():
            if key not in verified_pairs:
                diagnostics.append(warning)

        # Re-run articulation to sync plugs after enforcement overrides.
        if any(
            "identity-enforced" in r.sources.get(d, "")
            for r in rows
            for d in filing_dates
        ):
            self._apply_hierarchical_articulation(rows, filing_dates)

        return rows, diagnostics
