"""USDA ERS Meat Price Spreads file catalog and parsers."""

import csv
from io import StringIO

from openbb_government_us.utils.serializers import is_null_token

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/meat-price-spreads"

MEAT_PRICE_SPREADS_FILES: dict[str, dict] = {
    "summary": {
        "media_id": 5025,
        "slug": "summary-of-retail-prices-and-price-spreads",
        "title": "Summary of retail prices and price spreads",
        "period_column": "Month",
        "period_number_column": "Month_Number",
    },
    "choice_beef": {
        "media_id": 5020,
        "slug": "choice-beef-values-and-spreads-and-the-all-fresh-retail-value",
        "title": "Choice beef values and spreads and the all-fresh retail value",
        "period_column": "Period",
        "period_number_column": "Period_Number",
    },
    "pork": {
        "media_id": 5026,
        "slug": "pork-values-and-spreads",
        "title": "Pork values and spreads",
        "period_column": "Period",
        "period_number_column": "Period_Number",
    },
    "retail_prices": {
        "media_id": 5024,
        "slug": "retail-prices-for-beef-pork-poultry-cuts-eggs-and-dairy-products",
        "title": "Retail prices for beef, pork, poultry cuts, eggs, and dairy products",
        "period_column": "Month",
        "period_number_column": "Month_Number",
    },
    "historical_monthly": {
        "media_id": 5028,
        "slug": "historical-monthly-price-spread-data-for-beef-pork-broilers",
        "title": "Historical monthly price spread data for beef, pork, broilers",
        "period_column": "Month",
        "period_number_column": "Month-number",
    },
}

ANNUAL_PERIOD_NUMBER = 17
QUARTER_PERIOD_NUMBERS = range(13, 17)


def media_path(table: str) -> str:
    """Build the media path for one table's tidy CSV.

    Parameters
    ----------
    table : str
        Table key from MEAT_PRICE_SPREADS_FILES.

    Returns
    -------
    str
        The '/media/{id}/{slug}.csv' path of the table's CSV file.
    """
    entry = MEAT_PRICE_SPREADS_FILES[table]
    return f"/media/{entry['media_id']}/{entry['slug']}.csv"


def build_url(table: str) -> str:
    """Build the download URL for one table's tidy CSV.

    Parameters
    ----------
    table : str
        Table key from MEAT_PRICE_SPREADS_FILES.

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
        Raw cell text, which may carry comma thousands separators, e.g.
        '1,009.30', or a null token such as '' or 'NA'.

    Returns
    -------
    float | None
        The parsed value, or None for empty and null-token cells.
    """
    text = (raw or "").strip()
    if not text or is_null_token(text):
        return None
    return float(text.replace(",", ""))


def frequency_for(period_number: int) -> str:
    """Classify a period number into an observation frequency.

    Parameters
    ----------
    period_number : int
        Source period number: 1-12 for months, 13-16 for quarters, 17 for the
        annual row.

    Returns
    -------
    str
        One of 'annual', 'quarterly', or 'monthly'.
    """
    if period_number == ANNUAL_PERIOD_NUMBER:
        return "annual"
    if period_number in QUARTER_PERIOD_NUMBERS:
        return "quarterly"
    return "monthly"


def parse_rows(text: str, table: str) -> list[dict]:
    """Parse one table's tidy CSV text into long row records.

    Parameters
    ----------
    text : str
        Decoded CSV text with a Year column, the table's period and period
        number columns, a Data_Item column, and a Value column.
    table : str
        Table key from MEAT_PRICE_SPREADS_FILES, selecting the period and
        period number column names.

    Returns
    -------
    list[dict]
        Records with year, period, period_number, frequency, data_item, and
        value keys, skipping rows with an empty or null-token Value.
    """
    entry = MEAT_PRICE_SPREADS_FILES[table]
    period_column = entry["period_column"]
    number_column = entry["period_number_column"]
    rows: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        value = parse_value(row.get("Value"))
        if value is None:
            continue
        period_number = int((row.get(number_column) or "0").strip() or "0")
        rows.append(
            {
                "year": int((row.get("Year") or "").strip()),
                "period": (row.get(period_column) or "").strip(),
                "period_number": period_number,
                "frequency": frequency_for(period_number),
                "data_item": (row.get("Data_Item") or "").strip(),
                "value": value,
            }
        )
    return rows


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one table's tidy CSV through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table key from MEAT_PRICE_SPREADS_FILES.

    Returns
    -------
    list[dict]
        Long row records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(media_path(table), product=PRODUCT_PAGE)
    return parse_rows(content.decode("utf-8-sig", errors="replace"), table)
