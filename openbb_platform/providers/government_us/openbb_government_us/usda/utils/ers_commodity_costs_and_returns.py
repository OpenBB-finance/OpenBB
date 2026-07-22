"""USDA ERS Commodity Costs and Returns file catalog and parsers."""

import csv
import re
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/commodity-costs-and-returns"

COMMODITY_FILES: dict[str, dict] = {
    "corn": {"media_id": 4962, "slug": "corn", "label": "Corn"},
    "cotton": {"media_id": 4964, "slug": "cotton", "label": "Cotton"},
    "barley": {"media_id": 4966, "slug": "barley", "label": "Barley"},
    "peanuts": {"media_id": 4968, "slug": "peanuts", "label": "Peanuts"},
    "rice": {"media_id": 4970, "slug": "rice", "label": "Rice"},
    "sorghum": {"media_id": 4972, "slug": "sorghum", "label": "Sorghum"},
    "oats": {"media_id": 4974, "slug": "oats", "label": "Oats"},
    "soybeans": {"media_id": 4976, "slug": "soybeans", "label": "Soybeans"},
    "wheat": {"media_id": 4978, "slug": "wheat", "label": "Wheat"},
    "milk": {"media_id": 4980, "slug": "milk", "label": "Milk"},
    "cow_calf": {"media_id": 4982, "slug": "cow-calf", "label": "Cow-calf"},
    "hogs_all": {
        "media_id": 4984,
        "slug": "hogs-all",
        "label": "Hogs (all enterprises)",
    },
    "hogs_farrow_finish": {
        "media_id": 4986,
        "slug": "hogs-farrow-finish",
        "label": "Hogs, farrow-to-finish",
    },
    "hogs_farrow_feeder": {
        "media_id": 4988,
        "slug": "hogs-farrow-feeder",
        "label": "Hogs, farrow-to-feeder",
    },
    "hogs_feeder_finish": {
        "media_id": 4990,
        "slug": "hogs-feeder-finish",
        "label": "Hogs, feeder-to-finish",
    },
    "hogs_farrow_weanling": {
        "media_id": 4992,
        "slug": "hogs-farrow-weanling",
        "label": "Hogs, farrow-to-weanling",
    },
    "hogs_weanling_feeder": {
        "media_id": 4994,
        "slug": "hogs-weanling-feeder",
        "label": "Hogs, weanling-to-feeder",
    },
}

US_TOTAL = "U.S. total"

COMMODITY_REGIONS: dict[str, list[str]] = {
    "corn": [
        US_TOTAL,
        "Eastern Uplands",
        "Heartland",
        "Northern Crescent",
        "Northern Great Plains",
        "Prairie Gateway",
        "Southern Seaboard",
    ],
    "cotton": [
        US_TOTAL,
        "Eastern Uplands",
        "Fruitful Rim",
        "Heartland",
        "Mississippi Portal",
        "Prairie Gateway",
        "Southern Seaboard",
    ],
    "barley": [
        US_TOTAL,
        "Basin and Range",
        "Fruitful Rim",
        "Heartland",
        "Northern Crescent",
        "Northern Great Plains",
    ],
    "peanuts": [
        US_TOTAL,
        "Fruitful Rim",
        "Prairie Gateway",
        "Southern Seaboard (AL, GA)",
        "Southern Seaboard (VA, NC, SC)",
    ],
    "rice": [
        US_TOTAL,
        "Arkansas Non-Delta",
        "California",
        "Gulf Coast",
        "Mississippi River Delta",
    ],
    "sorghum": [
        US_TOTAL,
        "Eastern Uplands",
        "Fruitful Rim",
        "Heartland",
        "Mississippi Portal",
        "Northern Great Plains",
        "Prairie Gateway",
    ],
    "oats": [
        US_TOTAL,
        "Eastern Uplands",
        "Heartland",
        "Northern Crescent",
        "Northern Great Plains",
        "Prairie Gateway",
    ],
    "soybeans": [
        US_TOTAL,
        "Eastern Uplands",
        "Heartland",
        "Mississippi Portal",
        "Northern Crescent",
        "Northern Great Plains",
        "Prairie Gateway",
        "Southern Seaboard",
    ],
    "wheat": [
        US_TOTAL,
        "Basin and Range",
        "Fruitful Rim",
        "Heartland",
        "Mississippi Portal",
        "Northern Crescent",
        "Northern Great Plains",
        "Prairie Gateway",
        "Southern Seaboard",
    ],
    "milk": [
        US_TOTAL,
        "Basin and Range",
        "Eastern Uplands",
        "Fruitful Rim",
        "Heartland",
        "Northern Crescent",
        "Prairie Gateway",
        "Southern Seaboard",
    ],
    "cow_calf": [
        US_TOTAL,
        "Basin and Range",
        "Eastern Uplands",
        "Fruitful Rim",
        "Heartland",
        "Mississippi Portal",
        "Northern Great Plains",
        "Prairie Gateway",
        "Southern Seaboard",
    ],
    "hogs_all": [
        US_TOTAL,
        "Eastern Uplands",
        "Heartland",
        "Mississippi Portal",
        "Northern Crescent",
        "Northern Great Plains",
        "Prairie Gateway",
        "Southern Seaboard",
    ],
    "hogs_farrow_finish": [
        US_TOTAL,
        "Eastern Uplands",
        "Heartland",
        "Northern Crescent",
        "Prairie Gateway",
        "Southern Seaboard",
    ],
    "hogs_farrow_feeder": [
        US_TOTAL,
        "Eastern Uplands",
        "Southern Seaboard",
    ],
    "hogs_feeder_finish": [
        US_TOTAL,
        "Eastern Uplands",
        "Heartland",
        "Northern Crescent",
        "Southern Seaboard",
    ],
    "hogs_farrow_weanling": [US_TOTAL],
    "hogs_weanling_feeder": [
        US_TOTAL,
        "Heartland",
        "Southern Seaboard",
    ],
}

CATEGORY_CHOICES: dict[str, str] = {
    "gross_value_of_production": "Gross value of production",
    "operating_costs": "Operating costs",
    "net_value": "Net value",
    "allocated_overhead": "Allocated overhead",
    "costs_listed": "Costs listed",
    "supporting_information": "Supporting information",
    "production_practices": "Production practices",
    "size_of_operation": "Size of operation",
    "production_arrangement": "Production arrangement",
}

CATEGORY_ORDER: dict[str, int] = {
    "Gross value of production": 0,
    "Operating costs": 1,
    "Net value": 2,
    "Allocated overhead": 3,
    "Costs listed": 4,
    "Size of operation": 5,
    "Production arrangement": 6,
    "Supporting information": 7,
    "Production practices": 8,
}

SUPERSCRIPT_PATTERN = re.compile(r"[¹²³⁴⁵⁶⁷⁸⁹⁰]")
WHITESPACE_PATTERN = re.compile(r"\s+")


def media_path(commodity: str) -> str:
    """Build the media path for one commodity's tidy CSV.

    Parameters
    ----------
    commodity : str
        Commodity key from COMMODITY_FILES.

    Returns
    -------
    str
        The '/media/{id}/{slug}.csv' path of the commodity's CSV file.
    """
    entry = COMMODITY_FILES[commodity]
    return f"/media/{entry['media_id']}/{entry['slug']}.csv"


def build_url(commodity: str) -> str:
    """Build the download URL for one commodity's tidy CSV.

    Parameters
    ----------
    commodity : str
        Commodity key from COMMODITY_FILES.

    Returns
    -------
    str
        Full URL of the commodity's CSV file.
    """
    return f"{BASE_URL}{media_path(commodity)}"


def clean_item(item: str) -> str:
    """Strip footnote superscripts and normalize whitespace in an item label.

    Parameters
    ----------
    item : str
        Item label as published, e.g. 'Fertilizer  ' or 'Custom services  '.

    Returns
    -------
    str
        Cleaned label, e.g. 'Fertilizer'.
    """
    return WHITESPACE_PATTERN.sub(" ", SUPERSCRIPT_PATTERN.sub("", item)).strip()


def category_order(category: str) -> int:
    """Return the budget-section sort rank of a published category label.

    Parameters
    ----------
    category : str
        Published Category value, e.g. 'Operating costs'.

    Returns
    -------
    int
        The section's rank; a large sentinel for any unmapped category.
    """
    return CATEGORY_ORDER.get(category, 99)


def parse_rows(text: str, commodity: str) -> list[dict]:
    """Parse one commodity's tidy CSV text into row records.

    Parameters
    ----------
    text : str
        Decoded CSV text with columns Commodity, Category, Item, Units,
        Size, Region, Country, Year, Value, and Survey base year.
    commodity : str
        Commodity key from COMMODITY_FILES tagged on each record.

    Returns
    -------
    list[dict]
        Records with commodity, commodity_key, category, item, units,
        region, year, value, and survey_base_year keys, skipping rows with
        an empty Value.
    """
    rows: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        value = (row.get("Value") or "").strip()
        if not value:
            continue
        rows.append(
            {
                "commodity_key": commodity,
                "commodity": (row.get("Commodity") or "").strip(),
                "category": (row.get("Category") or "").strip(),
                "item": clean_item(row.get("Item") or ""),
                "units": (row.get("Units") or "").strip(),
                "region": (row.get("Region") or "").strip(),
                "year": int((row.get("Year") or "").strip()),
                "value": float(value),
                "survey_base_year": (row.get("Survey base year") or "").strip(),
            }
        )
    return rows


async def afetch_commodity(commodity: str, **kwargs) -> list[dict]:
    """Download and parse one commodity's tidy CSV through the ERS disk cache.

    Parameters
    ----------
    commodity : str
        Commodity key from COMMODITY_FILES.

    Returns
    -------
    list[dict]
        Row records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(media_path(commodity), product=PRODUCT_PAGE)
    return parse_rows(content.decode("utf-8-sig", errors="replace"), commodity)
