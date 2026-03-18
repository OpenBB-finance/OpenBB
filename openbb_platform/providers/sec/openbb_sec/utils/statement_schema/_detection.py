"""Company type detection, filing-date resolution, and fiscal metadata."""

# pylint: disable=R0912,R0914

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

from openbb_sec.utils.statement_schema._types import (
    ALL_FORMS,
    ANNUAL_FORMS,
    PRELIMINARY_FORMS,
    QUARTERLY_FORMS,
    SEMI_ANNUAL_FORMS,
    CompanyType,
    Frequency,
)


def detect_type(
    facts: dict[str, Any],
    *,
    insurance_is_signals: list[str],
    insurance_bs_signals: list[str],
    financial_signals: list[str],
    min_financial_signals: int,
    industrial_signals: list[str],
    diversified_signals: list[str],
) -> CompanyType:
    """Classify a company as industrial, financial, diversified, or insurance."""
    company_tags: set[str] = set()

    for ns_data in facts.values():
        if isinstance(ns_data, dict):
            company_tags.update(ns_data.keys())

    ins_is = sum(1 for s in insurance_is_signals if s in company_tags)
    ins_bs = sum(1 for s in insurance_bs_signals if s in company_tags)
    ins_total = ins_is + ins_bs
    is_insurance = ins_is >= 1 and ins_total >= 2
    fin_count = sum(1 for s in financial_signals if s in company_tags)
    is_financial = fin_count >= min_financial_signals

    if is_insurance and is_financial:
        return "insurance" if ins_total > fin_count else "financial"
    if is_insurance:
        return "insurance"
    if is_financial:
        return "financial"

    has_cogs = any(
        s in company_tags and _has_recent_data(facts, s) for s in industrial_signals
    )

    if has_cogs:
        return "industrial"

    has_cne = any(s in company_tags for s in diversified_signals)

    if has_cne:
        return "diversified"

    return "industrial"


def _has_recent_data(facts: dict[str, Any], tag: str, max_age_years: int = 5) -> bool:
    """Check if a tag has data from a recent 10-K filing."""
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


def get_filing_dates(  # noqa: PLR0912
    facts: dict[str, Any],
    frequency: Frequency = "annual",
    include_preliminary: bool = False,
) -> set[str]:
    """Determine canonical period-end dates from actual filings."""
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

    if include_preliminary:
        filing_dates |= preliminary_candidates - filing_dates

    if frequency != "annual" and filing_dates:
        canonical_annual = get_filing_dates(
            facts, "annual", include_preliminary=include_preliminary
        )
        filing_dates |= canonical_annual

    if frequency == "annual" and len(filing_dates) > 3:
        parsed = [(d, datetime.strptime(d, "%Y-%m-%d")) for d in filing_dates]
        md_counts: Counter[tuple[int, int]] = Counter()

        for _, dt in parsed:
            md_counts[(dt.month, dt.day)] += 1

        dominant_md, dom_freq = md_counts.most_common(1)[0]
        dom_m, dom_d = dominant_md

        if dom_freq >= max(3, len(parsed) * 0.4):
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

            filtered = set(canonical)

            for d, dt in non_canonical:
                has_nearby = any(abs((dt - ct).days) <= 200 for ct in canonical_dts)
                if not has_nearby:
                    filtered.add(d)

            filing_dates = filtered

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


def get_fiscal_meta(  # noqa: PLR0912
    facts: dict[str, Any],
    frequency: Frequency,
    filing_dates: set[str],
) -> dict[str, dict[str, Any]]:
    """Build fiscal metadata for each period-end date."""
    annual_dates = get_filing_dates(facts, "annual")
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
                        if end not in best_quarterly or filed < best_quarterly[end][0]:
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
        elif date in annual_dates:
            info = best_annual.get(date)
            period = "Q4"
            if not best_quarterly and best_semi:
                non_annual = {d for d in filing_dates if d not in annual_dates}
                period = "Q4" if len(non_annual) > len(annual_dates) else "H2"
            result[date] = {
                "fiscal_year": info[1] if info else int(date[:4]),
                "fiscal_period": period,
            }
        else:
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

    if frequency == "annual" and result:
        sorted_dates = sorted(result.keys())
        for i in range(len(sorted_dates) - 2, -1, -1):
            cur = sorted_dates[i]
            nxt = sorted_dates[i + 1]
            if result[cur]["fiscal_year"] >= result[nxt]["fiscal_year"]:
                result[cur]["fiscal_year"] = result[nxt]["fiscal_year"] - 1

    elif frequency == "quarterly" and result:
        sorted_dates = sorted(result.keys())
        annual_set = set(annual_dates)

        for i, date in enumerate(sorted_dates):
            if (
                date in annual_set
                and result[date]["fiscal_period"] in ("Q4", "H2")
                and i > 0
            ):
                prev = sorted_dates[i - 1]
                prev_meta = result[prev]
                if prev_meta["fiscal_period"] in ("Q1", "Q2", "Q3", "H1"):
                    prev_fy = prev_meta["fiscal_year"]
                    if result[date]["fiscal_year"] != prev_fy:
                        result[date]["fiscal_year"] = prev_fy

    return result


def detect_reporting_currency(facts: dict[str, Any]) -> str:
    """Detect the reporting currency from the SEC facts data."""
    currency_counts: dict[str, int] = {}
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

                if len(unit_key) == 3 and unit_key.isalpha() and unit_key.isupper():
                    currency_counts[unit_key] = currency_counts.get(unit_key, 0) + 1

    if not currency_counts:
        return "USD"

    return max(currency_counts, key=currency_counts.get)  # type: ignore[arg-type]


def prior_period_end(date: str) -> str | None:
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
