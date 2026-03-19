"""Company Facts — Standardized Financial Statements from SEC XBRL Data."""

# pylint: disable=R0917

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Literal

from openbb_sec.utils.statement_schema import (
    Frequency,
    StatementSchema,
    ValidationWarning,
)
from pydantic import BaseModel

PeriodType = Literal[
    "annual", "quarterly", "both", "ttm", "yoy", "yoy_quarterly", "pop"
]


def normalize_period_fields(
    periods: dict[str, dict],
    model_cls: type[BaseModel],
) -> None:
    """Rebuild every period dict in model-field declaration order.

    After pivoting long-format records into per-period dicts, each dict
    only contains the tags that had values for that period — and Python
    dict key order follows insertion order from the pivot loop, not the
    model's field declaration.  Downstream serialisation (``model_dump``,
    ``to_df``) preserves that insertion order, producing misaligned
    columns when different periods report different fields.

    This function collects the union of all tags seen across *every*
    period, then **rebuilds** each dict from scratch in model-field
    declaration order, back-filling absent tags with ``float('nan')``.
    NaN (rather than None) survives ``exclude_none=True`` and
    ``exclude_unset=True`` in downstream ``model_dump`` calls, ensuring
    every period carries the same keys in the same order.

    Fields whose annotation does not accept ``float`` (e.g. ``int | None``)
    are back-filled with ``None`` instead, because ``float('nan')`` would
    fail Pydantic validation for non-float types.
    """
    _NAN = float("nan")

    int_fields: set[str] = set()
    for fname, finfo in model_cls.model_fields.items():
        ann = finfo.annotation
        if ann is int or (
            hasattr(ann, "__args__") and int in getattr(ann, "__args__", ())
        ):
            int_fields.add(fname)

    all_tags: set[str] = set()
    for d in periods.values():
        all_tags.update(d)

    model_fields = list(model_cls.model_fields)
    ordered_tags = [f for f in model_fields if f in all_tags]

    for key, old in periods.items():
        periods[key] = {
            tag: old.get(tag, None if tag in int_fields else _NAN)
            for tag in ordered_tags
        }


def order_field_meta(
    field_meta: dict[str, dict],
    model_cls: type[BaseModel],
) -> dict[str, dict]:
    """Reorder field_meta by model field declaration order with sequential sequence."""
    ordered: dict[str, dict] = {}
    seq = 1
    for fname in model_cls.model_fields:
        if fname in field_meta:
            entry = field_meta[fname]
            entry["sequence"] = seq
            ordered[fname] = entry
            seq += 1
    for fname, entry in field_meta.items():
        if fname not in ordered:
            entry["sequence"] = seq
            ordered[fname] = entry
            seq += 1
    return ordered


# Module-level schema instance (loaded once, reused for all calls)
_schema = StatementSchema()

_STATEMENT_NAMES = ("income_statement", "balance_sheet", "cash_flow")

# Tickers whose full history requires merging facts from multiple CIKs.
# Order: newest CIK first (used for entityName / primary cik metadata).
MULTI_CIK_TICKERS: dict[str, list[str]] = {
    "DIS": ["0001744489", "0001001039"],
    "BLK": ["0002012383", "0001364742"],
    "GOOG": ["0001652044", "0001288776"],
}


@dataclass
class StandardizedStatements:
    """Container for all three standardized financial statements.

    Each statement is a list of dicts (records) in **long format**: one
    record per (period × line-item), carrying full metadata.  Suitable for
    direct conversion to a DataFrame.
    """

    entity_name: str
    cik: int | str
    company_type: str = "industrial"
    currency: str = "USD"
    income_statement: list[dict[str, Any]] = field(default_factory=list)
    balance_sheet: list[dict[str, Any]] = field(default_factory=list)
    cash_flow: list[dict[str, Any]] = field(default_factory=list)
    diagnostics: list[ValidationWarning] = field(default_factory=list)


def _calendar_quarter(date_str: str) -> str:
    """Map a period-ending date to its calendar quarter (Q1–Q4)."""
    month = int(date_str[5:7])
    return f"Q{(month - 1) // 3 + 1}"


def _build_records(
    result: Any,
    fiscal_years: list[int] | None = None,
) -> list[dict[str, Any]]:
    """Convert a StatementResult into long-format records.

    Each record represents one **line-item in one period** and includes:
        fiscal_year, fiscal_period, calendar_year, calendar_period,
        period_ending, tag, label, description, sequence, factor,
        balance, unit, currency, value, source
    """
    records: list[dict[str, Any]] = []
    currency = result.currency

    all_zero_tags: set[str] = set()
    for r in result.rows:
        if (
            r.values
            and all(v == 0 for v in r.values.values())
            and (
                not r.sources
                or not any(
                    s.startswith(("imputed", "corrected", "reconciled"))
                    for s in r.sources.values()
                )
            )
        ):
            all_zero_tags.add(r.tag)

    for date in result.dates:
        # Fiscal metadata from SEC fy/fp fields
        fm = result.fiscal_data.get(date, {})
        fiscal_year = fm.get("fiscal_year", int(date[:4]))
        fiscal_period = fm.get("fiscal_period", "FY")

        if fiscal_years and fiscal_year not in fiscal_years:
            continue

        calendar_year = int(date[:4])
        calendar_period = _calendar_quarter(date)

        for r in result.rows:
            if r.tag in all_zero_tags:
                continue
            val = r.values.get(date)
            if val is None:
                continue

            source_str = r.sources.get(date, "")

            # Suspect Zero policy: Imputed/derived exact zeros are highly likely false
            # identities rather than true $0 reported economics, especially for complex rules.
            if val == 0 and any(
                source_str.startswith(p)
                for p in ("imputed", "corrected", "reconciled", "Q4:", "H2:")
            ):
                if source_str.startswith("imputed"):
                    source_str = source_str.replace("imputed", "imputed-zero", 1)
                else:
                    source_str = f"imputed-zero: {source_str}"

            records.append(
                {
                    "period_ending": date,
                    "fiscal_year": fiscal_year,
                    "fiscal_period": (
                        f"{fiscal_period} (Preliminary)"
                        if date in result.preliminary_dates
                        else fiscal_period
                    ),
                    "calendar_year": calendar_year,
                    "calendar_period": calendar_period,
                    "tag": r.tag,
                    "label": r.label,
                    "description": r.description,
                    "parent": r.parent,
                    "sequence": r.sequence,
                    "factor": r.factor,
                    "balance": r.balance,
                    "unit": r.unit,
                    "period_type": r.period_type,
                    "currency": currency,
                    "value": val,
                    "source": source_str,
                }
            )

    return records


_SHARES_TAGS = frozenset(
    {
        "weighted_average_shares_outstanding",
        "weighted_average_shares_outstanding_diluted",
    }
)


def _compute_ttm(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute trailing-twelve-month records from quarterly data.

    Duration monetary/per_share items are summed over 4 quarters.
    Instant items, shares, and BS snapshots are averaged.
    """
    by_tag: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rec in records:
        by_tag[rec["tag"]].append(rec)

    ttm_records: list[dict[str, Any]] = []

    for tag, tag_recs in by_tag.items():
        sorted_recs = sorted(tag_recs, key=lambda r: r["period_ending"])
        if len(sorted_recs) < 4:
            continue

        period_type = sorted_recs[0].get("period_type", "duration")
        use_avg = period_type == "instant" or tag in _SHARES_TAGS

        for i in range(3, len(sorted_recs)):
            window = sorted_recs[i - 3 : i + 1]
            vals = [w["value"] for w in window]
            dates = [w["period_ending"] for w in window]

            if use_avg:
                ttm_val = sum(vals) / 4
                method = "avg"
            else:
                ttm_val = sum(vals)
                method = "sum"

            anchor = window[-1]
            ttm_records.append(
                {
                    "period_ending": anchor["period_ending"],
                    "fiscal_year": anchor["fiscal_year"],
                    "fiscal_period": "TTM",
                    "calendar_year": anchor["calendar_year"],
                    "calendar_period": anchor["calendar_period"],
                    "tag": tag,
                    "label": anchor["label"],
                    "description": anchor["description"],
                    "parent": anchor["parent"],
                    "sequence": anchor["sequence"],
                    "factor": anchor["factor"],
                    "balance": anchor["balance"],
                    "unit": anchor["unit"],
                    "period_type": anchor["period_type"],
                    "currency": anchor["currency"],
                    "value": ttm_val,
                    "source": f"TTM: {method}({' + '.join(dates)})",
                    "frequency": "ttm",
                }
            )

    return ttm_records


def _compute_pct_change(
    records: list[dict[str, Any]],
    mode: Literal["yoy", "pop"],
) -> list[dict[str, Any]]:
    """Compute period-over-period percentage change.

    mode='yoy': same fiscal_period, prior fiscal_year
    mode='pop': immediately preceding period by date order
    """
    by_tag: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for rec in records:
        by_tag[rec["tag"]].append(rec)

    pct_records: list[dict[str, Any]] = []

    for tag_recs in by_tag.values():
        sorted_recs = sorted(tag_recs, key=lambda r: r["period_ending"])

        if mode == "yoy":
            lookup: dict[tuple[int, str], dict[str, Any]] = {}

            for rec in sorted_recs:
                lookup[(rec["fiscal_year"], rec["fiscal_period"])] = rec

            for rec in sorted_recs:
                prior = lookup.get((rec["fiscal_year"] - 1, rec["fiscal_period"]))

                if prior is None or prior["value"] == 0:
                    continue

                pct = (rec["value"] - prior["value"]) / abs(prior["value"])
                pct_records.append(_pct_record(rec, prior, pct, "yoy"))
        else:
            for i in range(1, len(sorted_recs)):
                cur = sorted_recs[i]
                prior = sorted_recs[i - 1]

                if prior["value"] == 0:
                    continue

                pct = (cur["value"] - prior["value"]) / abs(prior["value"]) * 100
                pct_records.append(_pct_record(cur, prior, pct, "pop"))

    return pct_records


def _pct_record(
    current: dict[str, Any],
    prior: dict[str, Any],
    pct: float,
    freq: str,
) -> dict[str, Any]:
    return {
        "period_ending": current["period_ending"],
        "fiscal_year": current["fiscal_year"],
        "fiscal_period": current["fiscal_period"],
        "calendar_year": current["calendar_year"],
        "calendar_period": current["calendar_period"],
        "tag": current["tag"],
        "label": current["label"],
        "description": current["description"],
        "parent": current["parent"],
        "sequence": current["sequence"],
        "factor": current["factor"],
        "balance": current["balance"],
        "unit": "percent",
        "period_type": current["period_type"],
        "currency": "",
        "value": round(pct, 4),
        "source": (
            f"{freq}: ({current['period_ending']}: {current['value']}"
            f" / {prior['period_ending']}: {prior['value']} - 1)"
            f" = {round(pct, 2)}%"
        ),
        "frequency": freq,
    }


def resolve_company_facts(
    facts_json: dict[str, Any],
    fiscal_years: list[int] | None = None,
    period: PeriodType = "both",
    pit_mode: bool = False,
    include_preliminary: bool = False,
) -> StandardizedStatements:
    """Parse an SEC company-facts JSON and produce standardized statements.

    Parameters
    ----------
    facts_json : dict
        The raw JSON response from
        ``https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json``
    fiscal_years : list[int] | None
        Restrict to specific fiscal years.  ``None`` means all available.
    period : PeriodType
        Which periods to include in the output tables.
    pit_mode : bool
        If True, skip the 10-K vintage override for quarterly data.
        Quarterly values will reflect the original 10-Q filing vintage,
        preserving point-in-time fidelity for backtesting.  Note:
        Q4 values may not reconcile to FY totals in this mode.

    Returns
    -------
    StandardizedStatements
        Contains ``.income_statement``, ``.balance_sheet``, ``.cash_flow``
        as list-of-dicts ready for DataFrame conversion.
    """
    entity_name = facts_json.get("entityName", "")
    cik = facts_json.get("cik", "")
    facts = facts_json.get("facts", {})

    company_type = _schema.detect_type(facts)

    output = StandardizedStatements(
        entity_name=entity_name,
        cik=cik,
        company_type=company_type,
    )

    derived = period in ("ttm", "yoy", "yoy_quarterly", "pop")

    if derived:
        freq: Frequency = (
            "quarterly" if period in ("ttm", "yoy_quarterly", "pop") else "annual"
        )
        stmts = _schema.extract_all(
            facts_json,
            frequency=freq,
            company_type=company_type,
            pit_mode=pit_mode,  # type: ignore
            include_preliminary=include_preliminary,
        )
        for stmt_result in stmts.values():
            output.currency = stmt_result.currency
            break

        for stmt_name in _STATEMENT_NAMES:
            stmt_result = stmts[stmt_name]
            records = _build_records(stmt_result, fiscal_years)
            for rec in records:
                rec["frequency"] = freq

            if period == "ttm":
                records = _compute_ttm(records)
            elif period == "yoy":
                records = _compute_pct_change(records, mode="yoy")
            elif period == "yoy_quarterly":
                pct = _compute_pct_change(records, mode="yoy")
                for rec in pct:
                    rec["frequency"] = "yoy_quarterly"
                records = pct
            elif period == "pop":
                records = _compute_pct_change(records, mode="pop")

            getattr(output, stmt_name).extend(records)
            output.diagnostics.extend(stmt_result.diagnostics)
    else:
        frequencies: list[Frequency] = []
        if period in ("annual", "both"):
            frequencies.append("annual")
        if period in ("quarterly", "both"):
            frequencies.append("quarterly")

        for freq in frequencies:
            stmts = _schema.extract_all(
                facts_json,
                frequency=freq,
                company_type=company_type,
                pit_mode=pit_mode,  # type: ignore
                include_preliminary=include_preliminary,
            )
            for stmt_result in stmts.values():
                output.currency = stmt_result.currency
                break

            for stmt_name in _STATEMENT_NAMES:
                stmt_result = stmts[stmt_name]
                records = _build_records(stmt_result, fiscal_years)
                for rec in records:
                    rec["frequency"] = freq
                existing = getattr(output, stmt_name)
                existing.extend(records)
                output.diagnostics.extend(stmt_result.diagnostics)

    return output


async def get_standardized_financials(
    symbol: str | None = None,
    cik: str | int | None = None,
    fiscal_years: list[int] | None = None,
    period: PeriodType = "both",
    use_cache: bool = True,
    pit_mode: bool = False,
    include_preliminary: bool = False,
) -> StandardizedStatements:
    """Fetch company facts from SEC and return standardized financial statements.

    Provide either ``symbol`` (ticker) or ``cik`` (10-digit zero-padded or integer).

    For tickers in ``MULTI_CIK_TICKERS``, facts are fetched for every CIK and
    merged via ``StatementSchema.merge_facts`` so the full history is available.

    Parameters
    ----------
    symbol : str | None
        Ticker symbol (e.g. "AAPL").
    cik : str | int | None
        CIK number (e.g. 320193 or "0000320193").
    fiscal_years : list[int] | None
        Filter to specific fiscal years.
    period : PeriodType
        Which periods to return.
    use_cache : bool
        Whether to use in-memory HTTP caching (6-hour TTL).
    pit_mode : bool
        If True, skip the 10-K vintage override for quarterly data,
        preserving point-in-time fidelity for backtesting.
    include_preliminary : bool
        If True, include 8-K filing data for periods not yet covered
        by a 10-Q/K.

    Returns
    -------
    StandardizedStatements
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import amake_request
    from openbb_sec.utils.definitions import HEADERS
    from openbb_sec.utils.helpers import symbol_map

    if symbol and not cik:
        cik = await symbol_map(symbol, use_cache=use_cache)
        if not cik:
            raise OpenBBError(f"Could not find CIK for symbol: {symbol}")

    # Determine the list of CIKs to fetch.
    symbol_upper = symbol.upper() if symbol else ""
    if symbol_upper in MULTI_CIK_TICKERS:
        cik_list = MULTI_CIK_TICKERS[symbol_upper]
    elif isinstance(cik, int):
        cik_list = [str(cik).zfill(10)]
    elif isinstance(cik, str):
        cik_list = [cik.lstrip("0").zfill(10)] if cik else []
    else:
        raise OpenBBError("Either symbol or cik must be provided.")

    if not cik_list:
        raise OpenBBError("Either symbol or cik must be provided.")

    async def _fetch(cik_str: str) -> dict:
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_str}.json"
        if use_cache:
            from aiohttp_client_cache.session import (
                CachedSession,
            )  # pylint: disable=import-outside-toplevel

            async with CachedSession(expire_after=3600 * 6) as session:
                try:
                    resp = await amake_request(
                        url, headers=HEADERS, session=session, timeout=300
                    )
                finally:
                    await session.close()
        else:
            resp = await amake_request(url, headers=HEADERS, timeout=300)
        if not isinstance(resp, dict) or "facts" not in resp:
            raise OpenBBError(f"Unexpected response from SEC for CIK {cik_str}")
        return resp  # type: ignore[return-value]

    responses = [await _fetch(c) for c in cik_list]

    if len(responses) == 1:
        facts_json = responses[0]
    else:
        # Use the first (newest) CIK's metadata, merge all facts.
        primary = responses[0]
        merged_facts = _schema.merge_facts(*(r for r in responses))
        facts_json = {
            "entityName": primary.get("entityName", ""),
            "cik": primary.get("cik", ""),
            "facts": merged_facts,
        }

    return resolve_company_facts(
        facts_json,
        fiscal_years=fiscal_years,
        period=period,
        pit_mode=pit_mode,
        include_preliminary=include_preliminary,
    )
