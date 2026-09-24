"""USDA ERS Price Spreads from Farm to Consumer file catalog and parsers."""

import csv
import re
from io import StringIO

from openbb_core.app.model.abstract.error import OpenBBError

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/price-spreads-from-farm-to-consumer"

PRICE_SPREADS_FILES: dict[str, dict] = {
    "milk_and_dairy_basket": {
        "media_id": 5716,
        "slug": "milk-and-dairy-basket",
        "category": "dairy",
    },
    "butter": {
        "media_id": 5718,
        "slug": "butter-1-pound",
        "category": "dairy",
    },
    "cheddar_cheese": {
        "media_id": 5720,
        "slug": "cheddar-cheese-1-pound",
        "category": "dairy",
    },
    "ice_cream": {
        "media_id": 5722,
        "slug": "ice-cream-regular-one-half-gallon",
        "category": "dairy",
    },
    "whole_milk": {
        "media_id": 5724,
        "slug": "whole-milk-1-gallon",
        "category": "dairy",
    },
    "fresh_fruit_basket": {
        "media_id": 5734,
        "slug": "fresh-fruit-basket",
        "category": "fresh_fruit",
    },
    "fresh_apples": {
        "media_id": 5736,
        "slug": "fresh-apples",
        "category": "fresh_fruit",
    },
    "fresh_grapefruit": {
        "media_id": 5738,
        "slug": "fresh-grapefruit",
        "category": "fresh_fruit",
    },
    "fresh_grapes": {
        "media_id": 5740,
        "slug": "fresh-grapes",
        "category": "fresh_fruit",
    },
    "fresh_oranges": {
        "media_id": 5742,
        "slug": "fresh-oranges",
        "category": "fresh_fruit",
    },
    "fresh_peaches": {
        "media_id": 5744,
        "slug": "fresh-peaches",
        "category": "fresh_fruit",
    },
    "fresh_strawberries": {
        "media_id": 5746,
        "slug": "fresh-strawberries",
        "category": "fresh_fruit",
    },
    "fresh_vegetables_basket": {
        "media_id": 5748,
        "slug": "fresh-vegetables-basket",
        "category": "fresh_vegetables",
    },
    "fresh_broccoli": {
        "media_id": 5750,
        "slug": "fresh-broccoli",
        "category": "fresh_vegetables",
    },
    "fresh_carrots": {
        "media_id": 5752,
        "slug": "fresh-carrots",
        "category": "fresh_vegetables",
    },
    "fresh_lettuce_iceberg": {
        "media_id": 5754,
        "slug": "fresh-lettuce-iceberg",
        "category": "fresh_vegetables",
    },
    "fresh_lettuce_romaine": {
        "media_id": 5756,
        "slug": "fresh-lettuce-romaine",
        "category": "fresh_vegetables",
    },
    "fresh_potatoes": {
        "media_id": 5758,
        "slug": "fresh-potatoes",
        "category": "fresh_vegetables",
    },
    "fresh_tomatoes": {
        "media_id": 5760,
        "slug": "fresh-tomatoes",
        "category": "fresh_vegetables",
    },
    "orange_juice_nfc": {
        "media_id": 5762,
        "slug": "orange-juice-not-from-concentrate-one-gallon",
        "category": "processed",
    },
    "flour": {
        "media_id": 5726,
        "slug": "flour-white-all-purpose-per-pound",
        "category": "field_crops",
    },
    "vegetable_oil": {
        "media_id": 5728,
        "slug": "vegetable-soybean-oil-per-gallon",
        "category": "field_crops",
    },
    "sugar": {
        "media_id": 5730,
        "slug": "sugar-white-per-pound",
        "category": "field_crops",
    },
    "white_pan_bread": {
        "media_id": 5732,
        "slug": "white-pan-bread-per-pound",
        "category": "field_crops",
    },
}

ATTRIBUTE_PATTERN = re.compile(r"^(?P<measure>.+?)\s*\((?P<unit>[^)]+)\)$")

MEASURE_NAMES = {
    "Retail price": "retail_price",
    "Farm price": "farm_price",
    "Farm value": "farm_value",
    "Farm share": "farm_share",
    "Farm-value share": "farm_share",
    "Retail cost": "retail_cost_index",
    "Farm-to-retail spread": "farm_to_retail_spread_index",
}


def build_url(item: str) -> str:
    """Build the download URL for one item's tidy CSV.

    Parameters
    ----------
    item : str
        Item slug from PRICE_SPREADS_FILES.

    Returns
    -------
    str
        Full URL of the item's CSV file.
    """
    return f"{BASE_URL}{media_path(item)}"


def media_path(item: str) -> str:
    """Build the media path for one item's tidy CSV.

    Parameters
    ----------
    item : str
        Item slug from PRICE_SPREADS_FILES.

    Returns
    -------
    str
        The '/media/{id}/{slug}.csv' path of the item's CSV file.
    """
    entry = PRICE_SPREADS_FILES[item]
    return f"/media/{entry['media_id']}/{entry['slug']}.csv"


def parse_attribute(attribute: str) -> tuple[str, str]:
    """Parse a published attribute string into a measure name and unit.

    Parameters
    ----------
    attribute : str
        Attribute string, e.g. 'Retail price (dollars/pound)'.

    Returns
    -------
    tuple[str, str]
        Snake-case measure name and the unit label.

    Raises
    ------
    OpenBBError
        If the attribute format or measure text is unrecognized.
    """
    match = ATTRIBUTE_PATTERN.match(attribute.strip())
    if match is None:
        raise OpenBBError(f"Unrecognized attribute format: '{attribute}'")
    measure_text = match["measure"].strip()
    unit = match["unit"].strip()
    if unit == "cents/pounds":
        unit = "cents/pound"
    measure = MEASURE_NAMES.get(measure_text)
    if measure is None:
        raise OpenBBError(
            f"Unrecognized measure '{measure_text}' in attribute '{attribute}'."
            + " Expected one of: "
            + ", ".join(sorted(MEASURE_NAMES))
        )
    if measure == "farm_value" and "= 100" in unit:
        measure = "farm_value_index"
    return measure, unit


def parse_rows(text: str) -> list[dict]:
    """Parse one tidy CSV's text into raw row records.

    Parameters
    ----------
    text : str
        Decoded CSV text with columns Commodity, Year, Attribute, Value.

    Returns
    -------
    list[dict]
        Records with commodity, year (raw string), attribute, and value keys,
        skipping rows with an empty Value.
    """
    rows: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        value = (row.get("Value") or "").strip()
        if not value:
            continue
        rows.append(
            {
                "commodity": (row.get("Commodity") or "").strip(),
                "year": (row.get("Year") or "").strip(),
                "attribute": (row.get("Attribute") or "").strip(),
                "value": float(value),
            }
        )
    return rows


async def afetch_item(item: str, **kwargs) -> list[dict]:
    """Download and parse one item's tidy CSV through the ERS disk cache.

    Parameters
    ----------
    item : str
        Item slug from PRICE_SPREADS_FILES.

    Returns
    -------
    list[dict]
        Raw row records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(media_path(item), product=PRODUCT_PAGE)
    return parse_rows(content.decode("utf-8-sig"))
