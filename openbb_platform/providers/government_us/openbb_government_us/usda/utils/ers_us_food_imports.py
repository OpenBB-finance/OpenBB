"""USDA ERS U.S. Food Imports file catalog, parser, and pivot helpers."""

import csv
from collections import OrderedDict
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/us-food-imports"
MEDIA_PATH = (
    "/media/6495/summary-data-on-annual-food-imports-values-and-volume"
    "-by-food-category-and-source-country.csv"
)

FOOD_IMPORTS_FILES: dict[str, tuple[str, str]] = {"summary": (MEDIA_PATH, PRODUCT_PAGE)}

AGGREGATE_CATEGORIES = ("Food dollars", "Food volume", "Prices")

FOOD_GROUPS: "OrderedDict[str, str]" = OrderedDict(
    [
        ("Animals", "Live animals"),
        ("Meats", "Meats"),
        ("Fish", "Fish and shellfish"),
        ("Dairy", "Dairy"),
        ("Vegetables", "Vegetables"),
        ("Fruits", "Fruits"),
        ("Nuts", "Nuts"),
        ("Coffee", "Coffee, tea, and spices"),
        ("Grains", "Grains"),
        ("VegetablesOil", "Vegetable oils"),
        ("Sweets", "Sugar and candy"),
        ("Cocoa", "Cocoa and chocolate"),
        ("Other", "Other edible products"),
        ("Beverages", "Beverages"),
    ]
)

DEFAULT_FOOD_GROUP = "Fruits"
DEFAULT_COMMODITY = "Total fruit and preparations"

AGG_COLUMN_LABELS = {
    "U.S. imports": "Total foods",
    "Live meat animals": "Live animals",
    "Fish and shellfish": "Fish",
}

MEASURES: dict[str, dict] = {
    "value": {
        "label": "Import value (million $)",
        "category": "Food dollars",
        "subcategories": ("Total foods", "Foods"),
        "percent": False,
        "uniform_unit": "Million $",
    },
    "value_change": {
        "label": "Import value, year-over-year change (percent)",
        "category": "Food dollars",
        "subcategories": ("Total foods", "Foods"),
        "percent": True,
        "uniform_unit": "percent",
    },
    "volume": {
        "label": "Import volume",
        "category": "Food volume",
        "subcategories": ("Foods",),
        "percent": False,
        "uniform_unit": None,
    },
    "volume_change": {
        "label": "Import volume, year-over-year change (percent)",
        "category": "Food volume",
        "subcategories": ("Foods",),
        "percent": True,
        "uniform_unit": "percent",
    },
    "unit_price": {
        "label": "Import unit price",
        "category": "Prices",
        "subcategories": ("Imported food prices",),
        "percent": False,
        "uniform_unit": None,
    },
    "inflation": {
        "label": "Import price inflation (percent)",
        "category": "Prices",
        "subcategories": ("Import price inflation",),
        "percent": True,
        "uniform_unit": "percent",
    },
}

SOURCE_MEASURES = ("value", "volume")

SMALL_WORDS = frozenset({"and", "of", "or", "the"})

COUNTRY_FIXES = {
    "GERMANY, FED. REPUBLIC": "Germany",
    "COTE D'IVOIRE": "Cote d'Ivoire",
    "REST OF WORLD": "Rest of world",
    "WORLD": "World",
    "WORLD (QUANTITY)": "World",
}

UNIT_LABELS = {"1,000": "1,000 head"}


def build_url() -> str:
    """Build the download URL of the summary CSV."""
    return f"{BASE_URL}{MEDIA_PATH}"


def clean_country(raw: str) -> str:
    """Clean a source-country label to title case with special-case fixes.

    Parameters
    ----------
    raw : str
        Country label as published, uppercase and sometimes carrying a
        replacement character for a curly apostrophe or a trailing space.

    Returns
    -------
    str
        The title-cased label, with 'GERMANY, FED. REPUBLIC', Cote d'Ivoire,
        and the world aggregates mapped to their canonical forms.
    """
    text = raw.replace("�", "'").strip()
    key = text.upper()
    if key in COUNTRY_FIXES:
        return COUNTRY_FIXES[key]
    words = text.split()
    parts: list[str] = []
    for index, word in enumerate(words):
        lower = word.lower()
        if index and lower in SMALL_WORDS:
            parts.append(lower)
        else:
            parts.append(lower[:1].upper() + lower[1:])
    return " ".join(parts)


def unit_label(uom: str) -> str:
    """Return a display unit label, disambiguating the bare '1,000' head unit."""
    return UNIT_LABELS.get(uom.strip(), uom.strip())


def food_group_column_label(commodity: str) -> str:
    """Return the by-food-group column label for an aggregate commodity name."""
    return AGG_COLUMN_LABELS.get(commodity, commodity)


def parse_rows(text: str) -> list[dict]:
    """Parse the summary CSV text into tidy long-format observation records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the summary file.

    Returns
    -------
    list[dict]
        Records with commodity, country, uom, category, subcategory,
        row_number, year, and value keys. Rows whose year token is a period
        average ('means', 'means10years') or whose value is non-numeric are
        skipped.
    """
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        year_token = (row.get("YearNum") or "").strip()
        if not year_token.isdigit():
            continue
        raw_value = (row.get("FoodValue") or "").strip()
        try:
            value = float(raw_value)
        except ValueError:
            continue
        raw_row_number = (row.get("RowNumber") or "").strip()
        try:
            row_number = int(raw_row_number)
        except ValueError:
            continue
        records.append(
            {
                "commodity": (row.get("Commodity") or "").strip(),
                "country": (row.get("Country") or "").strip(),
                "uom": (row.get("UOM") or "").strip(),
                "category": (row.get("Category") or "").strip(),
                "subcategory": (row.get("SubCategory") or "").strip(),
                "row_number": row_number,
                "year": int(year_token),
                "value": value,
            }
        )
    return records


def product_lines(records: list[dict], food_group: str) -> list[str]:
    """List a food group's product-line commodities in published rank order.

    Parameters
    ----------
    records : list[dict]
        Long-format records from parse_rows.
    food_group : str
        Detail food-group category code, e.g. 'Fruits'.

    Returns
    -------
    list[str]
        Distinct product-line commodity names, ordered by their first
        RowNumber, e.g. 'Total fruit and preparations' first.
    """
    first_seen: dict[str, int] = {}
    for record in records:
        if record["category"] != food_group:
            continue
        name = record["commodity"]
        if name not in first_seen or record["row_number"] < first_seen[name]:
            first_seen[name] = record["row_number"]
    return sorted(first_seen, key=lambda name: first_seen[name])


async def afetch_records() -> list[dict]:
    """Download and parse the summary CSV through the ERS disk cache.

    Returns
    -------
    list[dict]
        Long-format records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(MEDIA_PATH, product=PRODUCT_PAGE)
    return parse_rows(content.decode("utf-8-sig", errors="replace"))
