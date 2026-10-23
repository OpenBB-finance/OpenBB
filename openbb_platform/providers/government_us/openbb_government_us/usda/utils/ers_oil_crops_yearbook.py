"""USDA ERS Oil Crops Yearbook file catalog and long-format parser."""

import csv
from io import StringIO

from openbb_government_us.utils.serializers import is_null_token

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/oil-crops-yearbook"
OILCROPS_CSV = "/media/5218/all-tables-oil-crops-yearbook.csv"

DEFAULT_TABLE = "soybeans_supply_disappearance_price"

OIL_CROPS_TABLES: dict[str, dict] = {
    "soybean_stocks_quarterly": {
        "label": "Soybean stocks: U.S. on-farm, off-farm, and total, by quarter",
        "table_number": "1",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "soybeans_acreage_production_yield_value": {
        "label": "Soybeans: U.S. acreage, yield, production, and value",
        "table_number": "2",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "soybeans_supply_disappearance_price": {
        "label": "Soybeans: U.S. supply, disappearance, and price",
        "table_number": "3",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "soybean_meal_supply_disappearance_price": {
        "label": "Soybean meal: U.S. supply, disappearance, and price",
        "table_number": "4",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "soybean_oil_supply_disappearance_price": {
        "label": "Soybean oil: U.S. supply, disappearance, and price",
        "table_number": "5",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "soybeans_supply_disappearance_by_quarter": {
        "label": "Soybeans: U.S. supply and disappearance, by crop-year quarter",
        "table_number": "6",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "soybean_meal_supply_disappearance_by_month": {
        "label": "Soybean meal: U.S. supply and disappearance, by month",
        "table_number": "7",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "soybean_oil_supply_disappearance_by_month": {
        "label": "Soybean oil: U.S. supply and disappearance, by month",
        "table_number": "8",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "soybean_crush_value_price_spread": {
        "label": "Soybeans: value of products per bushel crushed and spot price spread",
        "table_number": "9",
        "attribute_filter": None,
        "series_col": "Attribute_Desc2",
        "commodity_col": None,
        "geography_col": None,
    },
    "peanuts_acreage_production_yield_value": {
        "label": "Peanuts: U.S. acreage, yield, production, and value",
        "table_number": "10",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "peanuts_supply_disappearance_price": {
        "label": "Peanuts (farmers' stock basis): U.S. supply, disappearance, and price",
        "table_number": "11",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "peanuts_food_use": {
        "label": "Peanuts: U.S. food uses, shelled basis",
        "table_number": "12",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "peanuts_planted_acreage_by_state": {
        "label": "Peanuts: U.S. planted acreage, by State and region",
        "table_number": "13",
        "attribute_filter": None,
        "series_col": "Geography_Desc2",
        "commodity_col": None,
        "geography_col": None,
    },
    "peanuts_harvested_acreage_by_state": {
        "label": "Peanuts: U.S. harvested acreage, by State and region",
        "table_number": "14",
        "attribute_filter": None,
        "series_col": "Geography_Desc2",
        "commodity_col": None,
        "geography_col": None,
    },
    "peanuts_production_by_state": {
        "label": "Peanuts: U.S. production, by State and region",
        "table_number": "15",
        "attribute_filter": None,
        "series_col": "Geography_Desc2",
        "commodity_col": None,
        "geography_col": None,
    },
    "peanuts_yield_by_state": {
        "label": "Peanuts: U.S. yield per harvested acre, by State and region",
        "table_number": "16",
        "attribute_filter": None,
        "series_col": "Geography_Desc2",
        "commodity_col": None,
        "geography_col": None,
    },
    "cottonseed_acreage_production_yield_value": {
        "label": "Cottonseed: U.S. acreage, yield, production, and value",
        "table_number": "17",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "cottonseed_supply_disappearance_price": {
        "label": "Cottonseed: U.S. supply, disappearance, and price",
        "table_number": "18",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "cottonseed_meal_supply_disappearance_price": {
        "label": "Cottonseed meal: U.S. supply, disappearance, and price",
        "table_number": "19",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "cottonseed_oil_supply_disappearance_price": {
        "label": "Cottonseed oil: U.S. supply, disappearance, and price",
        "table_number": "20",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "sunflowerseed_acreage_production_yield_value": {
        "label": "Sunflowerseed: U.S. acreage, yield, production, and value, by type",
        "table_number": "21",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": "Commodity_Desc2",
        "geography_col": None,
    },
    "sunflowerseed_supply_disappearance_price": {
        "label": "Sunflowerseed: U.S. supply, disappearance, and price",
        "table_number": "22",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "sunflowerseed_meal_supply_disappearance_price": {
        "label": "Sunflowerseed meal: U.S. supply, disappearance, and price",
        "table_number": "23",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "sunflowerseed_oil_supply_disappearance_price": {
        "label": "Sunflowerseed oil: U.S. supply, disappearance, and price",
        "table_number": "24",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "canola_seed_supply_disappearance_price": {
        "label": "Canola seed: U.S. acreage, supply, disappearance, price, and value",
        "table_number": "25",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "canola_oil_supply_disappearance_price": {
        "label": "Canola oil: U.S. supply, disappearance, and price",
        "table_number": "26",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "canola_meal_supply_disappearance_price": {
        "label": "Canola meal: U.S. supply, disappearance, and price",
        "table_number": "27",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "flaxseed_acreage_production_yield_value": {
        "label": "Flaxseed: U.S. acreage, yield, production, and value",
        "table_number": "28",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "flaxseed_supply_disappearance_price": {
        "label": "Flaxseed: U.S. supply, disappearance, and price",
        "table_number": "29",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "linseed_meal_supply_disappearance_price": {
        "label": "Linseed meal: U.S. supply, disappearance, and price",
        "table_number": "30",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "linseed_oil_supply_disappearance_price": {
        "label": "Linseed oil: U.S. supply, disappearance, and price",
        "table_number": "31",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "edible_fats_and_oils_supply_disappearance": {
        "label": "Edible fats and oils: U.S. supply and disappearance, by product",
        "table_number": "32",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": "Commodity_Desc2",
        "geography_col": None,
    },
    "corn_oil_supply_disappearance_price": {
        "label": "Corn oil: U.S. supply, disappearance, and price",
        "table_number": "33",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "prices_received_by_farmers": {
        "label": "Prices received by U.S. farmers, by month",
        "table_number": "34",
        "attribute_filter": "Received by U.S. farmers",
        "series_col": "Attribute_Desc2",
        "commodity_col": None,
        "geography_col": None,
    },
    "prices_terminal_markets": {
        "label": "Cash prices at terminal markets, by month",
        "table_number": "34",
        "attribute_filter": "Cash prices at terminal markets",
        "series_col": "Attribute_Desc2",
        "commodity_col": None,
        "geography_col": None,
    },
    "prices_oilmeals": {
        "label": "Oilmeal prices, by month",
        "table_number": "34",
        "attribute_filter": "Meal prices",
        "series_col": "Attribute_Desc2",
        "commodity_col": None,
        "geography_col": None,
    },
    "prices_fats_and_oils_wholesale": {
        "label": "Wholesale prices of fats and oils, by month",
        "table_number": "34",
        "attribute_filter": "Wholesale prices",
        "series_col": "Attribute_Desc2",
        "commodity_col": None,
        "geography_col": None,
    },
    "prices_producer_price_indexes": {
        "label": "Producer price indexes for fats and oils products, by month",
        "table_number": "34",
        "attribute_filter": "Bureau of Labor Statistics Producer Price Indexes",
        "series_col": "Attribute_Desc2",
        "commodity_col": None,
        "geography_col": None,
    },
    "lard_supply_disappearance_price": {
        "label": "Lard: U.S. supply, disappearance, and price",
        "table_number": "35",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "edible_tallow_supply_disappearance_price": {
        "label": "Edible tallow: U.S. supply, disappearance, and price",
        "table_number": "36",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": None,
        "geography_col": None,
    },
    "world_soybean_complex_supply_and_use": {
        "label": "World soybean, meal, and oil supply and use, by region",
        "table_number": "37",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": "Commodity_Desc2",
        "geography_col": "Geography_Desc2",
    },
    "soybean_exports_by_destination": {
        "label": "U.S. soybean exports, by selected destination",
        "table_number": "38",
        "attribute_filter": None,
        "series_col": "Geography_Desc2",
        "commodity_col": None,
        "geography_col": None,
    },
    "soybean_meal_exports_by_destination": {
        "label": "U.S. soybean meal exports, by selected destination",
        "table_number": "39",
        "attribute_filter": None,
        "series_col": "Geography_Desc2",
        "commodity_col": None,
        "geography_col": None,
    },
    "soybean_oil_exports_by_destination": {
        "label": "U.S. soybean oil exports, by selected destination",
        "table_number": "40",
        "attribute_filter": None,
        "series_col": "Geography_Desc2",
        "commodity_col": None,
        "geography_col": None,
    },
    "world_oilseed_supply_and_distribution": {
        "label": "World oilseed supply and distribution, by oilseed",
        "table_number": "41",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": "Commodity_Desc2",
        "geography_col": None,
    },
    "world_vegetable_oils_supply_and_distribution": {
        "label": "World vegetable oils supply and distribution, by oil",
        "table_number": "42",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": "Commodity_Desc2",
        "geography_col": None,
    },
    "world_protein_meal_supply_and_distribution": {
        "label": "World protein meal supply and distribution, by meal",
        "table_number": "43",
        "attribute_filter": None,
        "series_col": "Attribute_Desc",
        "commodity_col": "Commodity_Desc2",
        "geography_col": None,
    },
}

MONTH_NUMBERS: dict[str, int] = {
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

MONTH_ABBREVIATIONS: dict[str, str] = {
    "January": "Jan",
    "February": "Feb",
    "March": "Mar",
    "April": "Apr",
    "May": "May",
    "June": "Jun",
    "July": "Jul",
    "August": "Aug",
    "September": "Sep",
    "October": "Oct",
    "November": "Nov",
    "December": "Dec",
}

QUARTER_ORDER: list[str] = ["Sep.–Nov.", "Dec.–Feb.", "Mar.–May", "June–Aug."]

POINT_IN_TIME_ORDER: list[str] = [
    "September 1",
    "December 1",
    "March 1",
    "June 1",
]

FREQUENCY_ORDER: list[str] = ["point_in_time", "annual", "quarterly", "monthly"]

FREQUENCY_LABELS: dict[str, str] = {
    "point_in_time": "Point-in-time",
    "annual": "Annual",
    "quarterly": "Quarterly",
    "monthly": "Monthly",
}

_POINT_IN_TIME_TABLES: frozenset[str] = frozenset({"soybean_stocks_quarterly"})
_QUARTERLY_MONTHLY_ANNUAL_TABLES: frozenset[str] = frozenset(
    {"soybeans_supply_disappearance_by_quarter"}
)
_MONTHLY_ANNUAL_TABLES: frozenset[str] = frozenset(
    {
        "soybean_meal_supply_disappearance_by_month",
        "soybean_oil_supply_disappearance_by_month",
        "soybean_crush_value_price_spread",
    }
)
_MONTHLY_ONLY_TABLES: frozenset[str] = frozenset(
    {
        "prices_received_by_farmers",
        "prices_terminal_markets",
        "prices_oilmeals",
        "prices_fats_and_oils_wholesale",
        "prices_producer_price_indexes",
    }
)


def _table_frequencies(table: str) -> list[str]:
    """Return the frequency tokens present in a table, in fixed order."""
    if table in _POINT_IN_TIME_TABLES:
        present = {"point_in_time"}
    elif table in _QUARTERLY_MONTHLY_ANNUAL_TABLES:
        present = {"annual", "quarterly", "monthly"}
    elif table in _MONTHLY_ANNUAL_TABLES:
        present = {"annual", "monthly"}
    elif table in _MONTHLY_ONLY_TABLES:
        present = {"monthly"}
    else:
        present = {"annual"}
    return [freq for freq in FREQUENCY_ORDER if freq in present]


FREQUENCIES_BY_TABLE: dict[str, list[str]] = {
    table: _table_frequencies(table) for table in OIL_CROPS_TABLES
}


def default_frequency(table: str) -> str:
    """Return the default frequency for a table, the finest that stays dense."""
    freqs = FREQUENCIES_BY_TABLE[table]
    for candidate in ("point_in_time", "quarterly", "monthly"):
        if candidate in freqs:
            return candidate
    return "annual"


DEFAULT_FREQUENCY: dict[str, str] = {
    table: default_frequency(table) for table in OIL_CROPS_TABLES
}


def parse_amount(raw: str | None) -> float | None:
    """Parse a raw Amount cell into a float.

    Parameters
    ----------
    raw : str | None
        Raw cell text, or a null token such as '' or 'NA'.

    Returns
    -------
    float | None
        The parsed value, or None for empty, null-token, or non-numeric cells.
    """
    text = (raw or "").strip()
    if not text or is_null_token(text):
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def coerce_period(raw: str | None) -> str | None:
    """Coerce a Timeperiod_Desc cell into a period label or None.

    Parameters
    ----------
    raw : str | None
        Raw Timeperiod_Desc value; 'MY Total' marks a whole-year total.

    Returns
    -------
    str | None
        The stripped period label, or None for 'MY Total' and blank cells.
    """
    text = (raw or "").strip()
    if not text or text == "MY Total":
        return None
    return text


def frequency_of(raw: str | None) -> str:
    """Classify a Timeperiod_Desc token into a frequency bucket.

    Parameters
    ----------
    raw : str | None
        Raw Timeperiod_Desc value.

    Returns
    -------
    str
        One of 'point_in_time', 'monthly', 'quarterly', or 'annual'.
    """
    text = (raw or "").strip()
    if not text or text == "MY Total":
        return "annual"
    if "–" in text or "-" in text:
        return "quarterly"
    parts = text.split()
    if len(parts) == 2 and parts[0] in MONTH_NUMBERS and parts[1].isdigit():
        return "point_in_time"
    if text in MONTH_NUMBERS:
        return "monthly"
    return "annual"


def start_month(my_definition: str | None) -> int:
    """Return the first calendar month of a marketing-year definition.

    Parameters
    ----------
    my_definition : str | None
        MY_Definition value, e.g. 'October–September'.

    Returns
    -------
    int
        The month number of the opening month, or 1 when unknown.
    """
    text = (my_definition or "").strip()
    for separator in ("–", "-"):
        if separator in text:
            first = text.split(separator, 1)[0].strip()
            return MONTH_NUMBERS.get(first, 1)
    return MONTH_NUMBERS.get(text, 1)


def annual_descriptor(my_definition: str | None) -> str:
    """Build a readable annual period label from a marketing-year definition.

    Parameters
    ----------
    my_definition : str | None
        MY_Definition value, e.g. 'September–August'.

    Returns
    -------
    str
        A label such as 'Marketing year (Sep-Aug)', or 'Marketing year'.
    """
    text = (my_definition or "").strip()
    for separator in ("–", "-"):
        if separator in text:
            first, last = (part.strip() for part in text.split(separator, 1))
            start = MONTH_ABBREVIATIONS.get(first)
            end = MONTH_ABBREVIATIONS.get(last)
            if start and end:
                return f"Marketing year ({start}-{end})"
    return "Marketing year"


def format_period(
    period: str | None, frequency: str, my_definition: str | None
) -> str | None:
    """Format a period token for display given its frequency.

    Parameters
    ----------
    period : str | None
        The coerced period token, or None for whole-year totals.
    frequency : str
        The frequency bucket the row belongs to.
    my_definition : str | None
        MY_Definition value, used to label annual rows.

    Returns
    -------
    str | None
        The display label, or None when no period applies.
    """
    if period is None:
        return annual_descriptor(my_definition) if frequency == "annual" else None
    if frequency == "quarterly":
        cleaned = period.replace(".", "").replace("–", "-")
        rank = QUARTER_ORDER.index(period) if period in QUARTER_ORDER else 0
        return f"{cleaned} (Q{rank + 1})"
    return period


def period_ordinal(
    period: str | None, frequency: str, my_definition: str | None
) -> int:
    """Return a within-year sort rank for a period token.

    Parameters
    ----------
    period : str | None
        The coerced period token.
    frequency : str
        The frequency bucket the row belongs to.
    my_definition : str | None
        MY_Definition value, giving the opening month of the marketing year.

    Returns
    -------
    int
        The position of the period within its marketing year.
    """
    if period is None:
        return 0
    if frequency == "point_in_time":
        return POINT_IN_TIME_ORDER.index(period) if period in POINT_IN_TIME_ORDER else 0
    if frequency == "quarterly":
        return QUARTER_ORDER.index(period) if period in QUARTER_ORDER else 0
    if frequency == "monthly" and period in MONTH_NUMBERS:
        return (MONTH_NUMBERS[period] - start_month(my_definition)) % 12
    return 0


def parse_rows(text: str, table: str) -> list[dict]:
    """Parse the all-tables CSV into one table's long-format records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the all-tables Oil Crops Yearbook file.
    table : str
        Table key from OIL_CROPS_TABLES, selecting the Table_number, the
        Attribute_Desc split filter, and the pivot columns.

    Returns
    -------
    list[dict]
        Records carrying the year label, integer year, period, frequency,
        marketing-year definition, commodity, geography, unit, series name,
        and numeric amount for the selected table, skipping rows with a blank
        or non-numeric Amount.
    """
    config = OIL_CROPS_TABLES[table]
    table_number = config["table_number"]
    attribute_filter = config["attribute_filter"]
    series_col = config["series_col"]
    commodity_col = config["commodity_col"]
    geography_col = config["geography_col"]
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        if row.get("Table_number") != table_number:
            continue
        if (
            attribute_filter is not None
            and row.get("Attribute_Desc") != attribute_filter
        ):
            continue
        amount = parse_amount(row.get("Amount"))
        if amount is None:
            continue
        year_label = (row.get("Marketing_Year") or "").strip()
        if not year_label[:4].isdigit():
            continue
        timeperiod = row.get("Timeperiod_Desc")
        records.append(
            {
                "table": table,
                "marketing_year": year_label,
                "year": int(year_label[:4]),
                "period": coerce_period(timeperiod),
                "frequency": frequency_of(timeperiod),
                "my_definition": (row.get("MY_Definition") or "").strip() or None,
                "commodity": (
                    ((row.get(commodity_col) or "").strip() or None)
                    if commodity_col
                    else None
                ),
                "geography": (
                    ((row.get(geography_col) or "").strip() or None)
                    if geography_col
                    else None
                ),
                "unit_desc": (row.get("Unit_Desc") or "").strip() or None,
                "series": (row.get(series_col) or "").strip(),
                "amount": amount,
            }
        )
    return records


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one Oil Crops Yearbook table through the ERS cache.

    Parameters
    ----------
    table : str
        Table key from OIL_CROPS_TABLES.

    Returns
    -------
    list[dict]
        Long-format records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(OILCROPS_CSV, product=PRODUCT_PAGE)
    return parse_rows(content.decode("utf-8-sig", errors="replace"), table)
