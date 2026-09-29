"""FRB Enhanced Financial Accounts: International Portfolio Investment."""

from __future__ import annotations

from typing import Any

BASE_URL = "https://www.federalreserve.gov/releases/efa"

TABLES = {
    "table1": (
        "international-portfolio-investment-table1-historical.csv",
        "Foreign residents' holdings of total U.S. long-term securities",
    ),
    "table1a": (
        "international-portfolio-investment-table1a-historical.csv",
        "Foreign residents' holdings of U.S. long-term Treasury securities",
    ),
    "table1b": (
        "international-portfolio-investment-table1b-historical.csv",
        "Foreign residents' holdings of U.S. long-term agency bonds",
    ),
    "table1c": (
        "international-portfolio-investment-table1c-historical.csv",
        "Foreign residents' holdings of U.S. long-term corporate and other bonds",
    ),
    "table1d": (
        "international-portfolio-investment-table1d-historical.csv",
        "Foreign residents' holdings of U.S. corporate stocks",
    ),
    "table1e": (
        "international-portfolio-investment-table1e-historical.csv",
        "Foreign residents' holdings of U.S. short-term Treasury securities (memo)",
    ),
    "table2": (
        "international-portfolio-investment-table2-historical.csv",
        "U.S. residents' holdings of total foreign long-term securities",
    ),
    "table2a": (
        "international-portfolio-investment-table2a-historical.csv",
        "U.S. residents' holdings of foreign long-term bonds",
    ),
    "table2b": (
        "international-portfolio-investment-table2b-historical.csv",
        "U.S. residents' holdings of foreign corporate stocks",
    ),
}


def fetch_ipi(table: str) -> str:
    """Download an international portfolio investment CSV (cached monthly)."""
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> str:
        """Fetch the table's CSV text."""
        response = make_request(f"{BASE_URL}/{TABLES[table][0]}", timeout=60)
        response.raise_for_status()
        return response.text

    return cached(
        ("ipi", table), lambda: seconds_until_next_release("monthly"), _producer
    )


def parse_ipi(text: str, label: str) -> list[dict[str, Any]]:
    """Melt a holdings-by-country CSV into ``(date, country, label, value)`` rows."""
    from io import StringIO

    from pandas import isna, notna, read_csv, to_datetime, to_numeric

    frame = read_csv(StringIO(text))
    frame.columns = [str(column).strip() for column in frame.columns]
    melted = frame.melt(id_vars=["Date"], var_name="country", value_name="value")
    melted["date"] = to_datetime(
        melted["Date"], format="%b %Y", errors="coerce"
    ).dt.date
    melted["value"] = to_numeric(melted["value"], errors="coerce")

    rows: list[dict[str, Any]] = []
    for record in melted.to_dict("records"):
        if not notna(record["date"]):
            continue
        rows.append(
            {
                "date": record["date"],
                "country": str(record["country"]).strip(),
                "label": label,
                "value": None if isna(record["value"]) else float(record["value"]),
            }
        )
    return rows
