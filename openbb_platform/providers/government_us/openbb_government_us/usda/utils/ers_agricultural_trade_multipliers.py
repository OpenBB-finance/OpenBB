"""USDA ERS Agricultural Trade Multipliers file catalog and parser."""

import csv
from io import StringIO

from openbb_government_us.utils.serializers import is_null_token

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/agricultural-trade-multipliers"
DEFAULT_TABLE = "agricultural_trade_multipliers"

AGRICULTURAL_TRADE_MULTIPLIERS_FILES: dict[str, str] = {
    "agricultural_trade_multipliers": "/media/6492/agricultural-trade-multipliers.csv",
}

AGGREGATE_COMMODITY = "All agricultural exports"

VARIABLE_FIELDS: dict[str, str] = {
    "Producer Output Multiplier": "producer_output_multiplier",
    "Producer Employment Multiplier": "producer_employment_multiplier",
    "Port Output Multiplier": "port_output_multiplier",
    "Port Employment Multiplier": "port_employment_multiplier",
    "Export Value": "export_value",
}


def media_path(table: str = DEFAULT_TABLE) -> str:
    """Return the media path for one table's CSV.

    Parameters
    ----------
    table : str
        Table key from AGRICULTURAL_TRADE_MULTIPLIERS_FILES.

    Returns
    -------
    str
        The '/media/{id}/{slug}.csv' path of the table's CSV file.
    """
    return AGRICULTURAL_TRADE_MULTIPLIERS_FILES[table]


def build_url(table: str = DEFAULT_TABLE) -> str:
    """Return the download URL for one table's CSV.

    Parameters
    ----------
    table : str
        Table key from AGRICULTURAL_TRADE_MULTIPLIERS_FILES.

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


def parse_commodity_id(raw: str | None) -> int | None:
    """Parse a raw commodity id cell into an integer.

    Parameters
    ----------
    raw : str | None
        Raw COMMID cell text, which may be a null token on the aggregate row.

    Returns
    -------
    int | None
        The parsed identifier, or None for empty and null-token cells.
    """
    text = (raw or "").strip()
    if not text or is_null_token(text):
        return None
    return int(text)


def parse_rows(text: str) -> list[dict]:
    """Parse the Agricultural Trade Multipliers CSV into long row records.

    Parameters
    ----------
    text : str
        Decoded CSV text with COMMID, CommodityName, Variable, Unit, Value, and
        Year columns.

    Returns
    -------
    list[dict]
        Records with commodity_id, commodity, year, field, unit, and value
        keys, one per commodity and variable. The aggregate row, published with
        a null-token commodity, is relabeled to AGGREGATE_COMMODITY with a null
        commodity_id.
    """
    rows: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        variable = (row.get("Variable") or "").strip()
        field = VARIABLE_FIELDS.get(variable)
        if field is None:
            continue
        name = (row.get("CommodityName") or "").strip()
        if is_null_token(name):
            commodity = AGGREGATE_COMMODITY
            commodity_id = None
        else:
            commodity = name
            commodity_id = parse_commodity_id(row.get("COMMID"))
        rows.append(
            {
                "commodity_id": commodity_id,
                "commodity": commodity,
                "year": int((row.get("Year") or "").strip()),
                "field": field,
                "unit": (row.get("Unit") or "").strip() or None,
                "value": parse_value(row.get("Value")),
            }
        )
    return rows


async def afetch_table(table: str = DEFAULT_TABLE, **kwargs) -> list[dict]:
    """Download and parse the Agricultural Trade Multipliers CSV through the cache.

    Parameters
    ----------
    table : str
        Table key from AGRICULTURAL_TRADE_MULTIPLIERS_FILES.

    Returns
    -------
    list[dict]
        Long row records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(media_path(table), product=PRODUCT_PAGE)
    return parse_rows(content.decode("utf-8-sig", errors="replace"))
