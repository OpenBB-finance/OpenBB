"""USDA ERS Dairy Data file catalog and parsers."""

import csv
from calendar import monthrange
from datetime import date
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/dairy-data"

DAIRY_DATA_FILES: dict[str, dict] = {
    "situation_at_a_glance": {
        "media_id": 5501,
        "slug": "us-dairy-situation-at-a-glance-monthly-and-annual",
        "title": "U.S. dairy situation at a glance (monthly and annual)",
    },
    "milk_production_quarterly": {
        "media_id": 5503,
        "slug": "us-milk-production-and-related-data-quarterly-and-annual",
        "title": "U.S. milk production and related data (quarterly and annual)",
    },
    "supply_utilization_products": {
        "media_id": 5505,
        "slug": "supply-and-utilization-of-dairy-product-categories-monthly-and-annual",
        "title": "Supply and utilization of dairy product categories"
        + " (monthly and annual)",
    },
    "supply_utilization_milk": {
        "media_id": 5507,
        "slug": "supply-and-utilization-of-milk-in-all-products-monthly-and-annual",
        "title": "Supply and utilization of milk in all products (monthly and annual)",
    },
    "milk_fat_skim_solids_allocation": {
        "media_id": 7134,
        "slug": "supply-and-allocation-of-milk-fat-and-skim-solids-by-product-annual",
        "title": "Supply and allocation of milk fat and skim solids by product"
        + " (annual)",
    },
    "per_capita_consumption": {
        "media_id": 5510,
        "slug": "dairy-products-per-capita-consumption-united-states-annual",
        "title": "Dairy products: per capita consumption, United States (annual)",
    },
    "fluid_milk_sales": {
        "media_id": 5512,
        "slug": "fluid-beverage-milk-sales-quantities-by-product-annual",
        "title": "Fluid beverage milk sales quantities by product (annual)",
    },
    "soft_products_domestic_use": {
        "media_id": 5514,
        "slug": "selected-soft-dairy-products-domestic-use-annual",
        "title": "Selected soft dairy products, domestic use (annual)",
    },
    "milk_cows_by_state": {
        "media_id": 5516,
        "slug": "milk-cows-and-production-by-state-and-region-annual",
        "title": "Milk cows and production by State and region (annual)",
    },
    "production_factors": {
        "media_id": 5518,
        "slug": "annual-milk-production-and-factors-affecting-supply-annual",
        "title": "Annual milk production and factors affecting supply (annual)",
    },
    "fluid_milk_plants": {
        "media_id": 5520,
        "slug": "number-and-average-size-of-u-s-fluid-milk-product-plants",
        "title": "Number and average size of U.S. fluid milk product plants (annual)",
    },
    "cheese_per_capita": {
        "media_id": 5522,
        "slug": "per-capita-consumption-of-selected-cheese-varieties-annual",
        "title": "Per capita consumption of selected cheese varieties (annual)",
    },
}


def build_url(table: str) -> str:
    """Build the download URL for one table's tidy CSV.

    Parameters
    ----------
    table : str
        Table key from DAIRY_DATA_FILES.

    Returns
    -------
    str
        Full URL of the table's CSV file.
    """
    return f"{BASE_URL}{media_path(table)}"


def media_path(table: str) -> str:
    """Build the media path for one table's tidy CSV.

    Parameters
    ----------
    table : str
        Table key from DAIRY_DATA_FILES.

    Returns
    -------
    str
        The '/media/{id}/{slug}.csv' path of the table's CSV file.
    """
    entry = DAIRY_DATA_FILES[table]
    return f"/media/{entry['media_id']}/{entry['slug']}.csv"


def period_end(year: int, timeperiod_id: int) -> date:
    """Resolve a Year and Timeperiod_id pair to the period's end date.

    Parameters
    ----------
    year : int
        Calendar year of the observation.
    timeperiod_id : int
        ERS time period id: 1-12 for months, 13-16 for quarters,
        17 for annual.

    Returns
    -------
    date
        Month end for 1-12, quarter end for 13-16, December 31 otherwise.
    """
    if 1 <= timeperiod_id <= 12:
        return date(year, timeperiod_id, monthrange(year, timeperiod_id)[1])
    if 13 <= timeperiod_id <= 16:
        month = (timeperiod_id - 12) * 3
        return date(year, month, monthrange(year, month)[1])
    return date(year, 12, 31)


def frequency_of(timeperiod_id: int) -> str:
    """Resolve an ERS Timeperiod_id to an observation frequency.

    Parameters
    ----------
    timeperiod_id : int
        ERS time period id: 1-12 for months, 13-16 for quarters,
        17 for annual.

    Returns
    -------
    str
        One of 'monthly', 'quarterly', or 'annual'.
    """
    if 1 <= timeperiod_id <= 12:
        return "monthly"
    if 13 <= timeperiod_id <= 16:
        return "quarterly"
    return "annual"


def clean_label(value: str | None) -> str | None:
    """Strip stray whitespace, including embedded newlines, from a label.

    Parameters
    ----------
    value : str | None
        Raw label text from a CSV cell.

    Returns
    -------
    str | None
        The label with whitespace runs collapsed to single spaces, or None
        when the input is missing or blank.
    """
    if value is None:
        return None
    cleaned = " ".join(value.split())
    return cleaned or None


def parse_rows(text: str) -> list[dict]:
    """Parse one tidy CSV's text into normalized row records.

    Parameters
    ----------
    text : str
        Decoded CSV text of one Dairy Data machine-readable file.

    Returns
    -------
    list[dict]
        Records with date, year, period, frequency, sub_table, product,
        category, data_item, data_item_id, data_item_description, region,
        state, value, and unit keys, skipping rows whose value is empty or
        'NA'. Values pass through raw; the unit is as published.
    """
    rows: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        raw_value = (row.get("Value") or row.get("Quantity") or "").strip()
        if not raw_value or raw_value.upper() == "NA":
            continue
        year = int((row.get("Year") or "").strip())
        timeperiod_id = int((row.get("Timeperiod_id") or "17").strip())
        rows.append(
            {
                "date": period_end(year, timeperiod_id),
                "year": year,
                "period": clean_label(row.get("Period")),
                "frequency": frequency_of(timeperiod_id),
                "sub_table": clean_label(row.get("Table")),
                "product": clean_label(row.get("Product")),
                "category": clean_label(row.get("Category")),
                "data_item": clean_label(row.get("Data_item")) or "",
                "data_item_id": clean_label(row.get("Data_item_id")),
                "data_item_description": clean_label(row.get("Data_item_description")),
                "region": clean_label(row.get("Region")),
                "state": clean_label(row.get("State")),
                "value": float(raw_value),
                "unit": clean_label(row.get("Unit") or row.get("Units")) or "",
            }
        )
    return rows


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one table's tidy CSV through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table key from DAIRY_DATA_FILES.

    Returns
    -------
    list[dict]
        Normalized row records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(media_path(table), product=PRODUCT_PAGE)
    return parse_rows(content.decode("utf-8-sig"))
