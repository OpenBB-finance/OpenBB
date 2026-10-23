"""USDA ERS Fruit and Vegetable Prices file catalog and parser."""

import csv
from io import StringIO

from openbb_government_us.utils.serializers import is_null_token

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/fruit-and-vegetable-prices"

DATA_YEAR = 2023

FVP_TABLES: dict[str, dict] = {
    "fruit": {
        "media_id": 6210,
        "slug": "all-fruits-average-prices-csv-format",
        "item_column": "Fruit",
        "item_label": "Fruit",
        "title": "All fruits, average retail prices and cup-equivalent prices",
    },
    "vegetable": {
        "media_id": 6240,
        "slug": "all-vegetables-average-prices-csv-format",
        "item_column": "Vegetable",
        "item_label": "Vegetable",
        "title": "All vegetables, average retail prices and cup-equivalent prices",
    },
}


def media_path(table: str) -> str:
    """Build the media path for one table's tidy CSV.

    Parameters
    ----------
    table : str
        Table key from FVP_TABLES.

    Returns
    -------
    str
        The '/media/{id}/{slug}.csv' path of the table's CSV file.
    """
    entry = FVP_TABLES[table]
    return f"/media/{entry['media_id']}/{entry['slug']}.csv"


def build_url(table: str) -> str:
    """Build the download URL for one table's tidy CSV.

    Parameters
    ----------
    table : str
        Table key from FVP_TABLES.

    Returns
    -------
    str
        Full URL of the table's CSV file.
    """
    return f"{BASE_URL}{media_path(table)}"


def parse_value(raw: str | None) -> float | None:
    """Parse a raw CSV value cell into a float.

    Parameters
    ----------
    raw : str | None
        Raw cell text, which may carry comma thousands separators or a null
        token such as '' or 'NA'.

    Returns
    -------
    float | None
        The parsed value, or None for empty and null-token cells.
    """
    text = (raw or "").strip()
    if not text or is_null_token(text):
        return None
    return float(text.replace(",", ""))


def parse_rows(text: str, table: str) -> list[dict]:
    """Parse one table's tidy CSV text into wide-on-measure records.

    Each source row already carries all six measures for one item and form, so
    the parser strips the trailing-space header, renames headers to snake_case,
    coerces the four numeric measures to float, and keeps the two unit-label
    columns as text.

    Parameters
    ----------
    text : str
        Decoded CSV text with the item column, a Form column, and the six
        measure columns.
    table : str
        Table key from FVP_TABLES, selecting the item column name.

    Returns
    -------
    list[dict]
        Records with item, form, average_retail_price, average_retail_price_unit,
        preparation_yield_factor, cup_equivalent_size, cup_equivalent_unit, and
        average_price_per_cup_equivalent keys, skipping rows with a blank item.
    """
    item_column = FVP_TABLES[table]["item_column"]
    records: list[dict] = []
    for raw in csv.DictReader(StringIO(text)):
        row = {(key or "").strip(): value for key, value in raw.items()}
        item = (row.get(item_column) or "").strip()
        if not item:
            continue
        records.append(
            {
                "item": item,
                "form": (row.get("Form") or "").strip() or None,
                "average_retail_price": parse_value(row.get("AverageRetailPrice")),
                "average_retail_price_unit": (
                    row.get("AverageRetailPriceUnitOfMeasure") or ""
                ).strip()
                or None,
                "preparation_yield_factor": parse_value(
                    row.get("PreparationYieldFactor")
                ),
                "cup_equivalent_size": parse_value(row.get("SizeOfACupEquivalent")),
                "cup_equivalent_unit": (
                    row.get("CupEquivalentUnitOfMeasure") or ""
                ).strip()
                or None,
                "average_price_per_cup_equivalent": parse_value(
                    row.get("AveragePricePerCupEquivalent")
                ),
            }
        )
    return records


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one table's tidy CSV through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table key from FVP_TABLES.

    Returns
    -------
    list[dict]
        Wide-on-measure records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(media_path(table), product=PRODUCT_PAGE)
    return parse_rows(content.decode("utf-8-sig", errors="replace"), table)
