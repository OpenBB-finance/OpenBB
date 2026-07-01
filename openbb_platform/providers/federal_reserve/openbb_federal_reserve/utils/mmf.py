"""FRB Enhanced Financial Accounts: Money Market Funds Investment Holdings.

The EFA project publishes eight historical CSV tables of money market fund
holdings. Most are time series (a ``Date`` column plus holding categories); the
detail table adds a ``Country`` column. Both shapes melt to a single long-format
shape: ``(date, country, label, value)`` with values in millions of dollars.
"""

from __future__ import annotations

from typing import Any

BASE_URL = "https://www.federalreserve.gov/releases/efa"

# Friendly table key -> the published CSV filename.
TABLES = {
    "total": "total-money-market-funds-investment-holdings-historical.csv",
    "prime": "prime-money-market-funds-investment-holdings-historical.csv",
    "government": "government-money-market-funds-investment-holdings-historical.csv",
    "exempt": "exempt-money-market-funds-investment-holdings-historical.csv",
    "holdings": "money-market-funds-investment-holdings-historical.csv",
    "detail": "money-market-funds-investment-holdings-detail-historical.csv",
    "commercial_paper": "money-market-fund-commercial-paper-holdings-historical.csv",
    "repo": "repo-money-market-funds-holdings-historical.csv",
}


def fetch_mmf(table: str) -> str:
    """Download a money market funds holdings CSV (cached monthly)."""
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> str:
        """Fetch the table's CSV text."""
        response = make_request(f"{BASE_URL}/{TABLES[table]}", timeout=60)
        response.raise_for_status()
        return response.text

    return cached(
        ("mmf", table), lambda: seconds_until_next_release("monthly"), _producer
    )


def parse_mmf(text: str) -> list[dict[str, Any]]:
    """Melt a holdings CSV into long-format ``(date, country, label, value)`` rows."""
    from io import StringIO

    from pandas import isna, notna, read_csv, to_datetime, to_numeric

    frame = read_csv(StringIO(text))
    frame.columns = [str(column).strip() for column in frame.columns]
    index = [column for column in ("Date", "Country") if column in frame.columns]
    melted = frame.melt(id_vars=index, var_name="label", value_name="value")
    melted["date"] = to_datetime(
        melted["Date"], format="%b %d, %Y", errors="coerce"
    ).dt.date
    melted["label"] = (
        melted["label"]
        .astype(str)
        .str.replace(r"\s*\(millions\)\s*$", "", regex=True)
        .str.strip()
    )
    melted["value"] = to_numeric(melted["value"], errors="coerce")

    rows: list[dict[str, Any]] = []
    for record in melted.to_dict("records"):
        if not notna(record["date"]):
            continue
        rows.append(
            {
                "date": record["date"],
                "country": record.get("Country"),
                "label": record["label"],
                "value": None if isna(record["value"]) else float(record["value"]),
            }
        )
    return rows
