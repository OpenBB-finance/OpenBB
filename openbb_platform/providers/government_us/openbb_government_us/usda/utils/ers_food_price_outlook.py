"""USDA ERS Food Price Outlook file catalog and parsers."""

import csv
import re
from datetime import date
from io import StringIO

from openbb_core.app.model.abstract.error import OpenBBError

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/food-price-outlook"

FOOD_PRICE_OUTLOOK_FILES: dict[str, dict] = {
    "cpi_forecast": {
        "media_id": 6460,
        "slug": "changes-in-consumer-price-indexes-2023-through-2026",
        "kind": "snapshot",
        "index": "cpi",
    },
    "ppi_forecast": {
        "media_id": 6468,
        "slug": "changes-in-producer-price-indexes-2023-through-2026",
        "kind": "snapshot",
        "index": "ppi",
    },
    "cpi_annual": {
        "media_id": 6462,
        "slug": (
            "annual-percent-changes-in-selected-consumer-price-indexes"
            "-1974-through-2025"
        ),
        "kind": "annual",
        "index": "cpi",
    },
    "ppi_annual": {
        "media_id": 6470,
        "slug": (
            "annual-percent-changes-in-selected-producer-price-indexes"
            "-1974-through-2025"
        ),
        "kind": "annual",
        "index": "ppi",
    },
    "cpi_forecast_history": {
        "media_id": 6464,
        "slug": "historical-consumer-price-index-cpi-forecast-series",
        "kind": "history",
        "index": "cpi",
    },
    "ppi_forecast_history": {
        "media_id": 6466,
        "slug": "historical-producer-price-index-ppi-forecast-series",
        "kind": "history",
        "index": "ppi",
    },
}

CPI_ITEMS: dict[str, str] = {
    "all_food": "All food",
    "food_away_from_home": "Food away from home",
    "food_at_home": "Food at home",
    "meats_poultry_and_fish": "Meats, poultry, and fish",
    "meats": "Meats",
    "beef_and_veal": "Beef and veal",
    "pork": "Pork",
    "other_meats": "Other meats",
    "poultry": "Poultry",
    "fish_and_seafood": "Fish and seafood",
    "eggs": "Eggs",
    "dairy_products": "Dairy products",
    "fats_and_oils": "Fats and oils",
    "fruits_and_vegetables": "Fruits and vegetables",
    "fresh_fruits_and_vegetables": "Fresh fruits and vegetables",
    "fresh_fruits": "Fresh fruits",
    "fresh_vegetables": "Fresh vegetables",
    "processed_fruits_and_vegetables": "Processed fruits and vegetables",
    "sugar_and_sweets": "Sugar and sweets",
    "cereals_and_bakery_products": "Cereals and bakery products",
    "nonalcoholic_beverages": "Nonalcoholic beverages",
    "other_foods": "Other foods",
}

PPI_ITEMS: dict[str, str] = {
    "unprocessed_foodstuffs_and_feedstuffs": "Unprocessed foodstuffs and feedstuffs",
    "processed_foods_and_feeds": "Processed foods and feeds",
    "finished_consumer_foods": "Finished consumer foods",
    "farm_level_cattle": "Farm-level cattle",
    "wholesale_beef": "Wholesale beef",
    "wholesale_pork": "Wholesale pork",
    "wholesale_poultry": "Wholesale poultry",
    "farm_level_eggs": "Farm-level eggs",
    "farm_level_milk": "Farm-level milk",
    "wholesale_dairy": "Wholesale dairy",
    "farm_level_soybeans": "Farm-level soybeans",
    "wholesale_fats_and_oils": "Wholesale fats and oils",
    "farm_level_fruits": "Farm-level fruits",
    "farm_level_vegetables": "Farm-level vegetables",
    "farm_level_wheat": "Farm-level wheat",
    "wholesale_wheat_flour": "Wholesale wheat flour",
}

ALL_ITEMS: dict[str, str] = {**CPI_ITEMS, **PPI_ITEMS}

ITEM_RENAMES = {"Farm-level fruit": "Farm-level fruits"}

HIERARCHY_COLUMNS = ("Top-level", "Aggregate", "Mid-level", "Low-level", "Disaggregate")
HIERARCHY_FIELDS = ("top_level", "aggregate", "mid_level", "low_level", "disaggregate")

SNAPSHOT_YEAR_PATTERN = re.compile(
    r"^(?:Annual|(?:Lower bound|Mid point|Upper bound) of prediction interval)"
    r" (\d{4})$"
)

_SUPERSCRIPT_TABLE = str.maketrans("", "", "⁰¹²³⁴⁵⁶⁷⁸⁹*")


def table_items(table: str) -> dict[str, str]:
    """Map item slugs to published names for one table's item universe.

    Parameters
    ----------
    table : str
        Table key from FOOD_PRICE_OUTLOOK_FILES.

    Returns
    -------
    dict[str, str]
        CPI_ITEMS for CPI tables, PPI_ITEMS for PPI tables.
    """
    entry = FOOD_PRICE_OUTLOOK_FILES[table]
    return CPI_ITEMS if entry["index"] == "cpi" else PPI_ITEMS


def media_path(table: str) -> str:
    """Build the media path of one table's tidy CSV.

    Parameters
    ----------
    table : str
        Table key from FOOD_PRICE_OUTLOOK_FILES.

    Returns
    -------
    str
        The '/media/{id}/{slug}.csv' path of the table's CSV file.
    """
    entry = FOOD_PRICE_OUTLOOK_FILES[table]
    return f"/media/{entry['media_id']}/{entry['slug']}.csv"


def build_url(table: str) -> str:
    """Build the download URL of one table's tidy CSV.

    Parameters
    ----------
    table : str
        Table key from FOOD_PRICE_OUTLOOK_FILES.

    Returns
    -------
    str
        Full URL of the table's CSV file.
    """
    return f"{BASE_URL}{media_path(table)}"


def clean_label(text: str | None) -> str:
    """Strip whitespace and footnote superscripts from a label.

    Parameters
    ----------
    text : str | None
        Raw label text.

    Returns
    -------
    str
        The cleaned label.
    """
    return (text or "").translate(_SUPERSCRIPT_TABLE).strip()


def normalize_item(text: str | None) -> str:
    """Clean an item label and normalize known cross-file spelling variants.

    Parameters
    ----------
    text : str | None
        Raw item label text.

    Returns
    -------
    str
        The canonical published item name.
    """
    label = clean_label(text)
    return ITEM_RENAMES.get(label, label)


def attribute_year(attribute: str) -> int | None:
    """Parse the trailing year out of an annual or prediction-interval attribute.

    Parameters
    ----------
    attribute : str
        Cleaned attribute label from a snapshot table.

    Returns
    -------
    int | None
        The four-digit year for 'Annual YYYY' and prediction-interval
        attributes, None for every other measure.
    """
    match = SNAPSHOT_YEAR_PATTERN.match(attribute)
    return int(match.group(1)) if match else None


def _item_value(row: dict) -> str:
    """Read the price-index item column of one CSV row.

    Parameters
    ----------
    row : dict
        A csv.DictReader row.

    Returns
    -------
    str
        The raw item cell value.

    Raises
    ------
    OpenBBError
        If the row has no 'Price Index item' column.
    """
    for key, value in row.items():
        if key and key.strip().endswith("Price Index item"):
            return value or ""
    raise OpenBBError(
        "No 'Price Index item' column found. Columns: " + ", ".join(map(str, row))
    )


def parse_snapshot_rows(text: str) -> list[dict]:
    """Parse a current CPI or PPI changes CSV into tidy records.

    Parameters
    ----------
    text : str
        Decoded CSV text of a 'Changes in ... Price Indexes' file.

    Returns
    -------
    list[dict]
        Records with item, hierarchy parents (CPI only), attribute, unit,
        year, and value keys, skipping rows with an empty Value.
    """
    rows: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        value = (row.get("Value") or "").strip()
        if not value:
            continue
        attribute = clean_label(row.get("Attribute"))
        record = {
            "attribute": attribute,
            "unit": clean_label(row.get("Unit")),
            "year": attribute_year(attribute),
            "value": float(value),
        }
        if "Top-level" in row:
            levels = [clean_label(row.get(col)) for col in HIERARCHY_COLUMNS]
            record.update(zip(HIERARCHY_FIELDS, (level or None for level in levels)))
            record["item"] = next((level for level in reversed(levels) if level), "")
        else:
            record["item"] = normalize_item(_item_value(row))
        rows.append(record)
    return rows


def parse_annual_rows(text: str) -> list[dict]:
    """Parse an annual percent-changes CSV into tidy records.

    Parameters
    ----------
    text : str
        Decoded CSV text of an 'Annual percent changes' file.

    Returns
    -------
    list[dict]
        Records with item, attribute, unit, year, and value keys, skipping
        rows with an empty Percent change.
    """
    rows: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        value = (row.get("Percent change") or "").strip()
        if not value:
            continue
        rows.append(
            {
                "item": normalize_item(_item_value(row)),
                "attribute": "Annual percent change",
                "unit": "Percent change",
                "year": int((row.get("Year") or "").strip()),
                "value": float(value),
            }
        )
    return rows


def parse_history_rows(text: str) -> list[dict]:
    """Parse a historical forecast-series CSV into tidy records.

    Parameters
    ----------
    text : str
        Decoded CSV text of a 'Historical ... forecast series' file.

    Returns
    -------
    list[dict]
        Records with item, attribute, unit, year (the year being forecast),
        forecast_date, and value keys, skipping rows with an empty forecast.
    """
    rows: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        value = (row.get("Forecast percent change") or "").strip()
        if not value:
            continue
        rows.append(
            {
                "item": normalize_item(_item_value(row)),
                "attribute": clean_label(row.get("Attribute")),
                "unit": "Percent change",
                "year": int((row.get("Year being forecast") or "").strip()),
                "forecast_date": date(
                    int((row.get("Year of forecast") or "").strip()),
                    int((row.get("Month of forecast") or "").strip()),
                    1,
                ),
                "value": float(value),
            }
        )
    return rows


def parse_table(text: str, table: str) -> list[dict]:
    """Parse one table's CSV text with the parser matching its kind.

    Parameters
    ----------
    text : str
        Decoded CSV text.
    table : str
        Table key from FOOD_PRICE_OUTLOOK_FILES.

    Returns
    -------
    list[dict]
        Tidy records from the kind-specific parser.
    """
    kind = FOOD_PRICE_OUTLOOK_FILES[table]["kind"]
    if kind == "snapshot":
        return parse_snapshot_rows(text)
    if kind == "annual":
        return parse_annual_rows(text)
    return parse_history_rows(text)


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one table's tidy CSV through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table key from FOOD_PRICE_OUTLOOK_FILES.

    Returns
    -------
    list[dict]
        Tidy records from parse_table.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(media_path(table), product=PRODUCT_PAGE)
    return parse_table(content.decode("utf-8-sig"), table)
