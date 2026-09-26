"""USDA ERS Rice Yearbook file catalog, long-format parser, and wide pivots."""

import csv
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/rice-yearbook"

MEDIA_ACREAGE = "/media/5670/us-rice-acreage-production-and-yield.csv"
MEDIA_SUPPLY = "/media/5676/us-supply-disappearance-and-stocks.csv"
MEDIA_STOCKS = "/media/5678/rice-stocks-rough-and-milled-1983-to-present.csv"
MEDIA_EXPORTS = (
    "/media/5672/us-rice-exports-by-type-and-top-10-us-rice-export-markets.csv"
)
MEDIA_IMPORTS = "/media/5674/us-rice-imports-by-origin-market-years.csv"
MEDIA_PRICES = (
    "/media/5664/us-rough-and-milled-rice-prices-monthly-and-marketing-year.csv"
)
MEDIA_PROGRAM = "/media/5666/program-payment-rates.csv"
MEDIA_WORLD_SUPPLY = (
    "/media/5680/world-rice-supply-and-utilization-196061-to-present.csv"
)
MEDIA_WORLD_TRADE = (
    "/media/5682/"
    "world-rice-trade-milled-basis-exports-and-imports-of-selected-countries-or-regions.csv"
)
MEDIA_ASIA_PRICES = (
    "/media/5668/export-prices-for-thailand-vietnam-india-and-pakistan.csv"
)

ANNUAL = "Annual"
MONTHLY = "Monthly"
WEEKLY = "Weekly"
POINT_IN_TIME = "Point-in-time"
FREQUENCY_ORDER = (MONTHLY, WEEKLY, POINT_IN_TIME, ANNUAL)

MONTHS = (
    "JANUARY",
    "FEBRUARY",
    "MARCH",
    "APRIL",
    "MAY",
    "JUNE",
    "JULY",
    "AUGUST",
    "SEPTEMBER",
    "OCTOBER",
    "NOVEMBER",
    "DECEMBER",
)
MONTH_SET = frozenset(MONTHS)
CALENDAR_MONTH_ORDER = {month: rank for rank, month in enumerate(MONTHS, start=1)}
MARKETING_MONTH_ORDER = {
    month: rank
    for rank, month in enumerate(
        (
            "AUGUST",
            "SEPTEMBER",
            "OCTOBER",
            "NOVEMBER",
            "DECEMBER",
            "JANUARY",
            "FEBRUARY",
            "MARCH",
            "APRIL",
            "MAY",
            "JUNE",
            "JULY",
        ),
        start=1,
    )
}

RICE_TABLES: dict[str, dict] = {
    "us_area_planted_by_class": {
        "label": "U.S. rice area planted, by class and State",
        "media": MEDIA_ACREAGE,
        "table_number": "1",
        "layout": "engine1",
        "pivot_field": "location",
        "frequencies": (ANNUAL,),
    },
    "us_state_yields": {
        "label": "U.S. rice yield, by State",
        "media": MEDIA_ACREAGE,
        "table_number": "2",
        "layout": "engine1",
        "pivot_field": "location",
        "frequencies": (ANNUAL,),
    },
    "us_acreage_yield_production": {
        "label": "U.S. rice acreage, yield, and production",
        "media": MEDIA_ACREAGE,
        "table_number": "3",
        "layout": "engine1",
        "pivot_field": "series",
        "frequencies": (ANNUAL,),
    },
    "us_production_by_class": {
        "label": "U.S. rice production, by class and State",
        "media": MEDIA_ACREAGE,
        "table_number": "4",
        "layout": "engine1",
        "pivot_field": "location",
        "frequencies": (ANNUAL,),
    },
    "us_state_acreage_yield_production_by_class": {
        "label": "U.S. rice acreage, yield, and production, by class and State",
        "media": MEDIA_ACREAGE,
        "table_number": "5",
        "layout": "engine1",
        "pivot_field": "series",
        "frequencies": (ANNUAL,),
    },
    "us_production_class_distribution": {
        "label": "U.S. rice production and class distribution",
        "media": MEDIA_ACREAGE,
        "table_number": "6",
        "layout": "engine1",
        "pivot_field": "rice_class",
        "frequencies": (ANNUAL,),
    },
    "us_supply_use_by_class": {
        "label": "U.S. rice supply and use, by class and region",
        "media": MEDIA_SUPPLY,
        "table_number": "7",
        "layout": "engine2",
        "pivot_field": "series",
        "frequencies": (ANNUAL,),
        "default_scope": {"rice_class": "ALL CLASSES", "location": "U.S. TOTAL"},
        "scope_fields": ("rice_class", "location"),
    },
    "us_supply_disappearance_price": {
        "label": "U.S. rice supply, disappearance, and price",
        "media": MEDIA_SUPPLY,
        "table_number": "8",
        "layout": "engine2",
        "pivot_field": "series",
        "frequencies": (ANNUAL,),
    },
    "long_grain_supply_disappearance_price": {
        "label": "U.S. long-grain rice supply, disappearance, and price",
        "media": MEDIA_SUPPLY,
        "table_number": "9",
        "layout": "engine2",
        "pivot_field": "series",
        "frequencies": (ANNUAL,),
    },
    "medium_short_grain_supply_disappearance_price": {
        "label": "U.S. medium- and short-grain rice supply, disappearance, and price",
        "media": MEDIA_SUPPLY,
        "table_number": "10",
        "layout": "engine2",
        "pivot_field": "series",
        "frequencies": (ANNUAL,),
        "default_scope": {"location": "U.S. TOTAL"},
        "scope_fields": ("location",),
    },
    "us_stocks_rough_and_milled": {
        "label": "U.S. rice stocks, rough and milled",
        "media": MEDIA_STOCKS,
        "table_number": "11",
        "layout": "engine1",
        "pivot_field": "series",
        "frequencies": (POINT_IN_TIME,),
    },
    "us_exports_by_type": {
        "label": "U.S. rice exports, by type",
        "media": MEDIA_EXPORTS,
        "table_number": "12",
        "layout": "engine2",
        "pivot_field": "rice_class",
        "frequencies": (ANNUAL,),
    },
    "us_top_export_markets": {
        "label": "Top 10 U.S. rice export markets",
        "media": MEDIA_EXPORTS,
        "table_number": "13",
        "layout": "engine1",
        "pivot_field": "series",
        "frequencies": (ANNUAL,),
        "chrono_first": True,
    },
    "us_imports_by_origin": {
        "label": "U.S. rice imports, by origin",
        "media": MEDIA_IMPORTS,
        "table_number": "14",
        "layout": "engine2",
        "pivot_field": "location",
        "frequencies": (ANNUAL,),
    },
    "us_rough_price_by_month": {
        "label": "U.S. rough rice prices received, by month and State",
        "media": MEDIA_PRICES,
        "table_number": "15",
        "layout": "engine1",
        "pivot_field": "series",
        "frequencies": (MONTHLY, ANNUAL),
    },
    "us_rough_price_by_month_and_class": {
        "label": "U.S. rough rice prices received, by month and class",
        "media": MEDIA_PRICES,
        "table_number": "16",
        "layout": "engine1",
        "pivot_field": "rice_class",
        "frequencies": (MONTHLY, ANNUAL),
    },
    "us_milled_price_milling_centers": {
        "label": "U.S. milled rice prices at milling centers",
        "media": MEDIA_PRICES,
        "table_number": "17",
        "layout": "engine1",
        "pivot_field": "location",
        "frequencies": (MONTHLY, ANNUAL),
    },
    "us_byproduct_prices": {
        "label": "U.S. rice byproduct prices",
        "media": MEDIA_PRICES,
        "table_number": "18",
        "layout": "engine1",
        "pivot_field": "rice_class",
        "frequencies": (MONTHLY, ANNUAL),
    },
    "us_brewers_rice_prices": {
        "label": "U.S. brewers' rice prices",
        "media": MEDIA_PRICES,
        "table_number": "19",
        "layout": "engine1",
        "pivot_field": "series",
        "frequencies": (MONTHLY, ANNUAL),
    },
    "us_prices_and_payment_rates": {
        "label": "U.S. rice prices and program payment rates",
        "media": MEDIA_PROGRAM,
        "table_number": "20",
        "layout": "engine1",
        "pivot_field": "series",
        "frequencies": (ANNUAL,),
    },
    "us_class_loan_values": {
        "label": "U.S. rice loan rates, by class",
        "media": MEDIA_PROGRAM,
        "table_number": "21",
        "layout": "engine1",
        "pivot_field": "rice_class",
        "frequencies": (ANNUAL,),
        "default_scope": {"statistic": "LOAN RATE"},
        "scope_fields": ("statistic",),
    },
    "world_market_prices_loan_basis": {
        "label": "World rice market prices, loan basis",
        "media": MEDIA_PROGRAM,
        "table_number": "22",
        "layout": "engine1",
        "pivot_field": "rice_class",
        "frequencies": (WEEKLY,),
        "default_scope": {"statistic": "MILLED-KERNEL RATE"},
        "scope_fields": ("statistic",),
    },
    "world_supply_and_utilization": {
        "label": "World rice supply and utilization",
        "media": MEDIA_WORLD_SUPPLY,
        "table_number": "23",
        "layout": "engine2",
        "pivot_field": "series",
        "frequencies": (ANNUAL,),
    },
    "world_trade_milled_basis": {
        "label": "World rice trade, milled basis",
        "media": MEDIA_WORLD_TRADE,
        "table_number": "24",
        "layout": "engine2",
        "pivot_field": "location",
        "frequencies": (ANNUAL,),
        "default_scope": {"statistic": "IMPORTS"},
        "scope_fields": ("statistic",),
    },
    "thailand_export_prices": {
        "label": "Thailand rice export prices",
        "media": MEDIA_ASIA_PRICES,
        "table_number": "25",
        "layout": "engine1",
        "pivot_field": "rice_class",
        "frequencies": (MONTHLY, ANNUAL),
    },
    "vietnam_export_prices": {
        "label": "Vietnam rice export prices",
        "media": MEDIA_ASIA_PRICES,
        "table_number": "26",
        "layout": "engine1",
        "pivot_field": "rice_class",
        "frequencies": (MONTHLY, ANNUAL),
    },
    "india_export_prices": {
        "label": "India rice export prices",
        "media": MEDIA_ASIA_PRICES,
        "table_number": "27",
        "layout": "engine1",
        "pivot_field": "rice_class",
        "frequencies": (MONTHLY, ANNUAL),
    },
    "pakistan_export_prices": {
        "label": "Pakistan rice export prices",
        "media": MEDIA_ASIA_PRICES,
        "table_number": "28",
        "layout": "engine1",
        "pivot_field": "rice_class",
        "frequencies": (MONTHLY, ANNUAL),
    },
}

NULL_TOKENS = frozenset({"", "-", "--", "n/a", "na", "null", "none", "nan"})


def clean_token(value: str | None) -> str | None:
    """Strip a cell and coerce blank or placeholder tokens to None.

    Parameters
    ----------
    value : str | None
        Raw cell value as read from the CSV.

    Returns
    -------
    str | None
        The stripped text, or None when blank or a placeholder such as 'NA'.
    """
    text = (value or "").strip()
    if not text or text.casefold() in NULL_TOKENS:
        return None
    return text


def classify_frequency(period: str | None) -> str:
    """Classify a reference-period token into its observation frequency.

    Parameters
    ----------
    period : str | None
        Reference-period token as published.

    Returns
    -------
    str
        One of Monthly, Annual, Point-in-time, or Weekly.
    """
    if period is None:
        return ANNUAL
    upper = period.upper()
    if upper in MONTH_SET:
        return MONTHLY
    if (
        upper.startswith("CROP YEAR")
        or upper.startswith("MARKETING YEAR")
        or upper in ("CALENDAR YEAR", "MARKETING")
    ):
        return ANNUAL
    parts = period.split()
    if len(parts) == 2 and parts[0].upper() in MONTH_SET and parts[1].isdigit():
        return POINT_IN_TIME
    return WEEKLY


def display_period(period: str | None) -> str | None:
    """Return the period token for display, title-casing bare month names.

    Parameters
    ----------
    period : str | None
        Reference-period token as published.

    Returns
    -------
    str | None
        The token with bare month names title-cased; other tokens unchanged.
    """
    if period is None:
        return None
    if period.upper() in MONTH_SET:
        return period.title()
    return period


def _weekly_sort_key(display: str) -> int:
    """Return the calendar month-and-day rank of a weekly period token."""
    month = day = 0
    for token in display.split(" - ", maxsplit=1)[0].replace("-", " ").split():
        if token.isdigit():
            day = int(token)
            continue
        name = token.upper()
        if len(name) < 3:
            continue
        month = next(
            (
                rank
                for label, rank in CALENDAR_MONTH_ORDER.items()
                if label.startswith(name)
            ),
            month,
        )
    return month * 100 + day


def _period_sort_key(display: str | None, frequency: str) -> int:
    """Return the within-year rank of a sub-annual period, else zero."""
    if display is None:
        return 0
    if frequency == WEEKLY:
        return _weekly_sort_key(display)
    if frequency in (MONTHLY, POINT_IN_TIME):
        return MARKETING_MONTH_ORDER.get(display.split()[0].upper(), 0)
    return 0


async def table_frequencies(table: str, **kwargs) -> list[str]:
    """List the frequencies present in a table's data, annual first.

    Parameters
    ----------
    table : str
        Table key from RICE_TABLES.

    Returns
    -------
    list[str]
        Distinct frequencies present, ordered Annual, Point-in-time, Weekly,
        Monthly.
    """
    records = await afetch_table(table)
    present = {classify_frequency(record["period"]) for record in records}
    return [label for label in reversed(FREQUENCY_ORDER) if label in present]


def parse_table(text: str, table: str) -> list[dict]:
    """Parse one numbered table's rows from its parent CSV into long records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the parent media file.
    table : str
        Table key from RICE_TABLES.

    Returns
    -------
    list[dict]
        Records carrying the table key, integer year, period, the row-dimension
        fields, the statistic name, its unit, and the numeric value. Rows
        outside the table number, or whose value is blank or non-numeric, or
        whose year is not a four-digit number, are skipped.
    """
    table_number = RICE_TABLES[table]["table_number"]
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        if (row.get("TABLE_NUMBER") or "").strip() != table_number:
            continue
        raw_value = (row.get("VALUE") or "").strip()
        try:
            value = float(raw_value)
        except ValueError:
            continue
        year_label = (row.get("YEAR") or "").strip()
        if not year_label[:4].isdigit():
            continue
        records.append(
            {
                "table": table,
                "year": int(year_label[:4]),
                "period": clean_token(row.get("REFERENCE_PERIOD_DESCRIPTION")),
                "rice_class": clean_token(row.get("CLASS_DESCRIPTION")),
                "location": clean_token(row.get("LOCATION_DESCRIPTION")),
                "rank": clean_token(row.get("RANK")),
                "aggregate_level": clean_token(row.get("AGGREGATE_LEVEL_DESCRIPTION")),
                "series": (row.get("STATISTIC_DESCRIPTION") or "").strip(),
                "unit": clean_token(row.get("UNIT_DESCRIPTION")),
                "value": value,
            }
        )
    return records


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one rice-yearbook table through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table key from RICE_TABLES.

    Returns
    -------
    list[dict]
        Long-format records from parse_table.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = RICE_TABLES[table]
    content = await afetch_ers_file(config["media"], product=PRODUCT_PAGE)
    return parse_table(content.decode("utf-8-sig", errors="replace"), table)
