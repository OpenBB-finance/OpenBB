"""Shape standardized SEC financial statements for OpenBB Workspace widgets."""

from typing import Any, cast

_STATEMENT_MAP = {
    "balance": "balance_sheet",
    "income": "income_statement",
    "cash": "cash_flow",
}

_PERIOD_MAP = {
    ("FY", "None"): "annual",
    ("Q", "None"): "quarterly",
    ("TTM", "None"): "ttm",
    ("FY", "% YoY"): "yoy",
    ("Q", "% YoY"): "yoy_quarterly",
    ("Q", "% PoP"): "pop",
}


def _model_field_order(statement_type: str) -> dict:
    """Map each line-item tag to its index in the statement model's field order."""
    from openbb_sec.models.balance_sheet import SecBalanceSheetData
    from openbb_sec.models.cash_flow import SecCashFlowStatementData
    from openbb_sec.models.income_statement import SecIncomeStatementData

    model = {
        "balance": SecBalanceSheetData,
        "income": SecIncomeStatementData,
        "cash": SecCashFlowStatementData,
    }[statement_type]
    return {name: index for index, name in enumerate(model.model_fields)}


def _format_provenance(sources: dict[str, str]) -> str:
    """Render a line item's sources, collapsed to one line when uniform."""
    if not sources:
        return "_No source detail available._"
    if len(set(sources.values())) == 1:
        return next(iter(sources.values()))
    return "\n".join(
        f"- **{period}**: {source}"
        for period, source in sorted(sources.items(), reverse=True)
    )


async def get_statement_widget_rows(
    symbol: str,
    statement_type: str,
    period: str = "FY",
    transform: str = "None",
    transpose: bool = True,
    limit: int = 10,
    use_cache: bool = True,
) -> list[dict]:
    """Return standardized statement rows shaped for a Workspace table widget."""
    from openbb_sec.utils.company_facts import (
        PeriodType,
        _compute_pct_change,
        get_standardized_financials,
    )

    statement_name = _STATEMENT_MAP.get(statement_type)
    if statement_name is None:
        raise ValueError(f"Unknown statement_type: {statement_type}")

    ttm_pop = period == "TTM" and transform == "% PoP"
    resolved = "ttm" if ttm_pop else _PERIOD_MAP.get((period, transform))
    if resolved is None:
        resolved = _PERIOD_MAP[(period, "None")]

    result = await get_standardized_financials(
        symbol=symbol, period=cast("PeriodType", resolved), use_cache=use_cache
    )
    records: list[dict] = getattr(result, statement_name, [])
    if ttm_pop and records:
        records = _compute_pct_change(records, mode="pop")
    if not records:
        return []

    periods: dict[str, dict] = {}
    field_meta: dict[str, dict] = {}
    sources: dict[str, dict[str, str]] = {}
    order: list[str] = []

    for record in records:
        date = record["period_ending"]
        label = f"{record.get('fiscal_period') or ''} {date}".strip()
        tag = record["tag"]
        periods.setdefault(date, {"label": label})[tag] = record["value"]
        if record.get("source"):
            sources.setdefault(tag, {})[label] = record["source"]
        if tag not in field_meta:
            field_meta[tag] = {
                "Line Item": record.get("label") or tag,
                "description": record.get("description") or "",
                "parent": record.get("parent"),
                "sequence": record.get("sequence"),
            }
            order.append(tag)

    field_index = _model_field_order(statement_type)
    end_index = len(field_index)

    def _resolve(tag: str, seen: frozenset = frozenset()) -> tuple[int, int] | None:
        """Return (anchor_index, depth) by walking parents up to a model field."""
        if tag in field_index:
            return field_index[tag], 0
        parent = field_meta.get(tag, {}).get("parent")
        if not parent or parent in seen:
            return None
        result = _resolve(parent, seen | {tag})
        if result is None:
            return None
        anchor, depth = result
        return anchor, depth + 1

    def _sort_key(tag: str) -> tuple[float, int, float]:
        resolved = _resolve(tag)
        if resolved is None:
            return (float(end_index), 0, 0.0)
        anchor, depth = resolved
        seq = field_meta[tag].get("sequence") or 0.0
        if depth == 0:
            return (float(anchor), 0, 0.0)
        return (float(anchor) - 0.5, -depth, float(seq))

    order.sort(key=_sort_key)

    period_keys = sorted(periods, reverse=True)
    if limit and limit > 0:
        period_keys = period_keys[:limit]

    order = [
        tag
        for tag in order
        if any(periods[date].get(tag) is not None for date in period_keys)
    ]
    period_labels = [periods[date]["label"] for date in period_keys]

    if not transpose:
        rows: list[dict] = []
        for date in period_keys:
            row = {"Period": periods[date]["label"]}
            for tag in order:
                row[field_meta[tag]["Line Item"]] = periods[date].get(tag)
            rows.append(row)
        return rows

    rows = []
    for tag in order:
        row: dict[str, Any] = {
            "Line Item": field_meta[tag]["Line Item"],
            "description": field_meta[tag]["description"],
            "provenance": _format_provenance(sources.get(tag, {})),
        }
        for date, label in zip(period_keys, period_labels):
            row[label] = periods[date].get(tag)
        rows.append(row)
    return rows
