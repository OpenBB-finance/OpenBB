"""Shared handling for the TMX financial statements."""

from typing import Any

STATEMENT_KEYS = {
    "income": "IncomeStatement",
    "balance": "BalanceSheet",
    "cash": "CashFlow",
}


def to_snake_case(name: str) -> str:
    """Convert a QuoteMedia statement key to snake case.

    Parameters
    ----------
    name : str
        The key as published.

    Returns
    -------
    str
        The key in snake case.
    """
    import re

    stepped = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
    stepped = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", stepped)

    return stepped.lower()


def transform_reports(reports: list[dict], statement: str) -> list[dict]:
    """Flatten QuoteMedia reports into rows for one statement.

    Parameters
    ----------
    reports : list[dict]
        The reports as QuoteMedia returns them.
    statement : str
        One of 'income', 'balance', or 'cash'.

    Returns
    -------
    list[dict]
        One row per reporting period, newest first.
    """
    key = STATEMENT_KEYS[statement]
    results: list[dict] = []

    for report in reports:
        lines = report.get(key)

        if not lines:
            continue

        period_ending = report.get("periodEndDate") or report.get("reportDate")

        if not period_ending:
            continue

        quarter = report.get("reportQuarter")
        row: dict[str, Any] = {
            "period_ending": period_ending,
            "fiscal_period": (
                "annual" if report.get("reportPeriod") == "A" else f"Q{quarter}"
            ),
            "fiscal_year": report.get("reportYear"),
            "reported_currency": report.get("currency"),
        }
        row.update({to_snake_case(k): v for k, v in lines.items()})
        results.append(row)

    return sorted(results, key=lambda r: r["period_ending"], reverse=True)
