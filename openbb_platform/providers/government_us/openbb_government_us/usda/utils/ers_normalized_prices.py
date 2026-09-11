"""USDA ERS Normalized Prices catalog, zip fetch, and long-format parser."""

import csv
import io
import zipfile
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/normalized-prices"
MEDIA_PATH = "/media/5552/all-tables-2025-csv-format.zip"

INDEX_UNITS = "Index, 2011=100"

NORMALIZED_PRICES_TABLES: dict[str, dict] = {
    "table1_national_prices": {
        "label": "Table 1 - National normalized prices by commodity and report year",
        "csv_prefix": "table1",
        "dimension": "year",
        "commodity_field": "Commodity",
        "description_field": "Description",
        "units_field": "Units",
        "units_constant": None,
        "column_field": "Report Year",
        "value_field": "Price",
    },
    "table2_national_indices": {
        "label": "Table 2 - National price indices by series and index year (2011=100)",
        "csv_prefix": "table2",
        "dimension": "year",
        "commodity_field": "Commodity",
        "description_field": None,
        "units_field": None,
        "units_constant": INDEX_UNITS,
        "column_field": "Price index year",
        "value_field": "Price",
    },
    "table3_state_prices": {
        "label": "Table 3 - State normalized prices by commodity and State",
        "csv_prefix": "table3",
        "dimension": "state",
        "commodity_field": "Commodity",
        "description_field": "Description",
        "units_field": "Units",
        "units_constant": None,
        "column_field": "State",
        "value_field": "Price",
    },
}

DEFAULT_TABLE = "table1_national_prices"


def parse_value(value: str | None) -> float | None:
    """Parse a raw price cell to a float, keeping full precision.

    Parameters
    ----------
    value : str | None
        Raw price cell; blank or suppressed cells are non-numeric.

    Returns
    -------
    float | None
        The numeric value, or None when the cell is blank or non-numeric.
    """
    text = (value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_column(token: str, dimension: str) -> int | str | None:
    """Parse a pivot-column token into an integer year or a State name.

    Parameters
    ----------
    token : str
        Raw report-year, index-year, or State cell.
    dimension : str
        'year' to require a four-digit year, 'state' to keep the name.

    Returns
    -------
    int | str | None
        The integer year, the State name, or None when the token is empty
        or not a four-digit year.
    """
    text = token.strip()
    if dimension == "year":
        return int(text) if len(text) == 4 and text.isdigit() else None
    return text or None


def parse_table(text: str, table: str) -> list[dict]:
    """Parse one inner CSV into long-format observation records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the selected table.
    table : str
        Table slug from NORMALIZED_PRICES_TABLES.

    Returns
    -------
    list[dict]
        Records with table, commodity, description, units, dimension, column
        (integer year or State name), value, and the stable first-seen order
        of the commodity or series row. Rows without a commodity or a valid
        pivot column are skipped.
    """
    config = NORMALIZED_PRICES_TABLES[table]
    dimension = config["dimension"]
    records: list[dict] = []
    seen: dict[tuple, int] = {}
    for row in csv.DictReader(StringIO(text)):
        commodity = (row.get(config["commodity_field"]) or "").strip()
        if not commodity:
            continue
        description = None
        if config["description_field"]:
            description = (row.get(config["description_field"]) or "").strip() or None
        units = config["units_constant"]
        if units is None and config["units_field"]:
            units = (row.get(config["units_field"]) or "").strip() or None
        column = parse_column(row.get(config["column_field"]) or "", dimension)
        if column is None:
            continue
        row_key = (commodity, description, units)
        if row_key not in seen:
            seen[row_key] = len(seen)
        records.append(
            {
                "table": table,
                "commodity": commodity,
                "description": description,
                "units": units,
                "dimension": dimension,
                "column": column,
                "value": parse_value(row.get(config["value_field"])),
                "order": seen[row_key],
            }
        )
    return records


def extract_inner_csv(zip_bytes: bytes, prefix: str) -> str:
    """Extract and decode one table's CSV member from the all-tables zip.

    Parameters
    ----------
    zip_bytes : bytes
        Raw bytes of the all-tables csv-format zip archive.
    prefix : str
        Inner-file basename prefix, e.g. 'table1', matched year-agnostically.

    Returns
    -------
    str
        The decoded CSV text of the matching '.csv' member.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        name = next(
            member
            for member in archive.namelist()
            if member.rsplit("/", 1)[-1].startswith(prefix)
            and member.lower().endswith(".csv")
        )
        raw = archive.read(name)
    return raw.decode("utf-8-sig", errors="replace")


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download the all-tables zip and parse one table through the ERS cache.

    Parameters
    ----------
    table : str
        Table slug from NORMALIZED_PRICES_TABLES.

    Returns
    -------
    list[dict]
        Long-format records from parse_table.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(MEDIA_PATH, product=PRODUCT_PAGE)
    text = extract_inner_csv(content, NORMALIZED_PRICES_TABLES[table]["csv_prefix"])
    return parse_table(text, table)
