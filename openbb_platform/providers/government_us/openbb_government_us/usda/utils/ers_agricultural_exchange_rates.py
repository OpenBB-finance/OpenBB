"""USDA ERS Agricultural Exchange Rate Data Set file catalog and parsers."""

import csv
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/agricultural-exchange-rate-data-set"

MONTH_ORDER: dict[str, int] = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

EXCHANGE_RATE_FILES: dict[str, dict] = {
    "real_index_annual": {
        "media": "/media/5447/real-annual-commodity-trade-weighted-"
        "exchange-rate-indexes.csv",
        "kind": "index",
        "frequency": "annual",
        "label": "Real trade-weighted index (annual)",
    },
    "real_index_monthly": {
        "media": "/media/5449/real-monthly-commodity-trade-weighted-"
        "exchange-rate-indexes.csv",
        "kind": "index",
        "frequency": "monthly",
        "label": "Real trade-weighted index (monthly)",
    },
    "real_bilateral_annual": {
        "media": "/media/5457/annual-real-exchange-rates-local-currency-per-usd.csv",
        "kind": "bilateral",
        "frequency": "annual",
        "label": "Real bilateral rate, local currency per USD (annual)",
    },
    "real_bilateral_monthly": {
        "media": "/media/5451/monthly-real-exchange-rates-local-currency-per-usd.csv",
        "kind": "bilateral",
        "frequency": "monthly",
        "label": "Real bilateral rate, local currency per USD (monthly)",
    },
    "nominal_bilateral_annual": {
        "media": "/media/5453/annual-nominal-exchange-rates-local-currency-per-usd.csv",
        "kind": "bilateral",
        "frequency": "annual",
        "label": "Nominal bilateral rate, local currency per USD (annual)",
    },
    "nominal_bilateral_monthly": {
        "media": "/media/5455/monthly-nominal-exchange-rates-local-currency-per-usd.csv",
        "kind": "bilateral",
        "frequency": "monthly",
        "label": "Nominal bilateral rate, local currency per USD (monthly)",
    },
}

TRADE_WEIGHTS_MEDIA = (
    "/media/5459/agricultural-trade-weights-by-commodity-or-commodity-group.csv"
)

INDEX_WEIGHTS: tuple[str, ...] = (
    "U.S. competitors (country export weights)",
    "U.S. markets (U.S. export weights)",
    "U.S. suppliers (U.S. import weights)",
)

BILATERAL_REGIONS: tuple[str, ...] = (
    "Central America",
    "Europe",
    "Middle East",
    "North Africa",
    "North America",
    "Northeast Asia",
    "Oceania",
    "South America",
    "South Asia",
    "Southeast Asia",
    "Sub-Saharan Africa",
    "The Caribbean",
)


def media_path(table: str) -> str:
    """Return the media path of one table's CSV file.

    Parameters
    ----------
    table : str
        Table key from EXCHANGE_RATE_FILES.

    Returns
    -------
    str
        The '/media/{id}/{slug}.csv' path of the table's CSV file.
    """
    return EXCHANGE_RATE_FILES[table]["media"]


def build_url(table: str) -> str:
    """Return the full download URL of one table's CSV file.

    Parameters
    ----------
    table : str
        Table key from EXCHANGE_RATE_FILES.

    Returns
    -------
    str
        Full URL of the table's CSV file.
    """
    return f"{BASE_URL}{media_path(table)}"


def parse_table(text: str, table: str) -> list[dict]:
    """Parse one table's CSV text into long-format observation records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the table.
    table : str
        Table key from EXCHANGE_RATE_FILES.

    Returns
    -------
    list[dict]
        Records carrying the table key, kind, integer year, month label and
        calendar order, the pivot series name, the index weight scheme or the
        bilateral region, and the numeric value. Rows whose value or year is
        blank or non-numeric are skipped.
    """
    config = EXCHANGE_RATE_FILES[table]
    kind = config["kind"]
    has_month = config["frequency"] == "monthly"
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        raw_value = (row.get("Value") or "").strip()
        try:
            value = float(raw_value)
        except ValueError:
            continue
        year_label = (row.get("Year") or "").strip()
        if not year_label.isdigit():
            continue
        month = (row.get("Month") or "").strip() if has_month else ""
        record: dict = {
            "table": table,
            "kind": kind,
            "year": int(year_label),
            "month": month or None,
            "month_order": MONTH_ORDER.get(month) if month else None,
            "value": value,
        }
        if kind == "index":
            record["weights"] = (row.get("Weights") or "").strip() or None
            record["region"] = None
            record["series"] = (row.get("Commodity") or "").strip()
        else:
            record["weights"] = None
            record["region"] = (row.get("Region") or "").strip() or None
            record["series"] = (row.get("Country") or "").strip()
        records.append(record)
    return records


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one table through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table key from EXCHANGE_RATE_FILES.

    Returns
    -------
    list[dict]
        Long-format records from parse_table.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(media_path(table), product=PRODUCT_PAGE)
    return parse_table(content.decode("utf-8-sig", errors="replace"), table)
