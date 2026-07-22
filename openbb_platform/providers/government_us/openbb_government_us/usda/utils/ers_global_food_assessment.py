"""USDA ERS Global Food Assessment file catalog and long-format parser."""

import csv
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/global-food-assessment"
MEDIA_PATH = (
    "/media/6171/grain-food-demand-other-demand-total-demand-production-and-"
    "implied-additional-supply-required-for-global-food-assessment-countries.csv"
)

GLOBAL_FOOD_ASSESSMENT_FILES: dict[str, tuple[str, str]] = {
    "global_food_assessment": (MEDIA_PATH, PRODUCT_PAGE)
}

ELEMENTS: tuple[str, ...] = (
    "Food grain demand",
    "Other grain demand",
    "Grain production",
    "Implied additional supply required",
    "Total grain demand",
)

REGIONS: tuple[str, ...] = (
    "Asia",
    "Former Soviet Union",
    "Latin America and the Caribbean",
    "Middle East and North Africa",
    "Sub-Saharan Africa",
    "GFA countries",
)

DEFAULT_ELEMENT = "Total grain demand"

VALUE_COLUMN = "Millions of metric tons"
UNIT = "Millions of metric tons"


def build_url() -> str:
    """Build the download URL of the global food assessment CSV."""
    return f"{BASE_URL}{MEDIA_PATH}"


def parse_amount(raw: str) -> float | None:
    """Parse a value cell into a float, or None for a blank or placeholder.

    Parameters
    ----------
    raw : str
        Value cell as published.

    Returns
    -------
    float | None
        The numeric amount, with negatives preserved; None when the cell is
        blank or a non-numeric placeholder.
    """
    text = raw.replace(",", "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_rows(text: str) -> list[dict]:
    """Parse the CSV text into tidy long-format observation records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the global food assessment file.

    Returns
    -------
    list[dict]
        Records with element, region, subregion, year, and amount keys. The
        constant Dataset title column is carried as context only and never
        returned as a value; the unit lives in the value-column header and is
        supplied as the UNIT constant rather than a per-row value.
    """
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        records.append(
            {
                "element": (row.get("Element") or "").strip(),
                "region": (row.get("Region") or "").strip(),
                "subregion": (row.get("Subregion") or "").strip(),
                "year": (row.get("Year") or "").strip(),
                "amount": parse_amount(row.get(VALUE_COLUMN) or ""),
            }
        )
    return records


async def afetch_records() -> list[dict]:
    """Download and parse the CSV through the ERS disk cache.

    Returns
    -------
    list[dict]
        Long-format records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(MEDIA_PATH, product=PRODUCT_PAGE)
    return parse_rows(content.decode("utf-8-sig", errors="replace"))
