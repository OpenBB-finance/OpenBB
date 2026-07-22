"""USDA ERS State Agricultural Trade catalog, fetch, and CSV parsers."""

import csv
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/state-agricultural-trade-data"

ALL_DATA_CSV = "/media/5420/csv-comma-separated-values-format-of-all-data.csv"
TOP_EXPORTS_CSV = (
    "/media/5422/top-5-us-agricultural-export-commodities-by-state-fiscal-year.csv"
)
TOP_IMPORTS_CSV = (
    "/media/5424/top-5-us-agricultural-import-commodities-by-state-fiscal-year.csv"
)

STATE_AG_TRADE_FILES: dict[str, tuple[str, str]] = {
    "exports_by_commodity": (ALL_DATA_CSV, PRODUCT_PAGE),
    "exports_by_state": (ALL_DATA_CSV, PRODUCT_PAGE),
    "top_exports": (TOP_EXPORTS_CSV, PRODUCT_PAGE),
    "top_imports": (TOP_IMPORTS_CSV, PRODUCT_PAGE),
}

TABLE_LABELS: dict[str, str] = {
    "exports_by_commodity": "Exports by commodity (state, calendar year)",
    "exports_by_state": "Exports by state (commodity, calendar year)",
    "top_exports": "Top export commodities (state, fiscal year)",
    "top_imports": "Top import commodities (state, fiscal year)",
}

STATE_SCOPED_TABLES: frozenset[str] = frozenset(
    {"exports_by_commodity", "top_exports", "top_imports"}
)
DATASET_A_TABLES: frozenset[str] = frozenset(
    {"exports_by_commodity", "exports_by_state"}
)
DATASET_B_TABLES: frozenset[str] = frozenset({"top_exports", "top_imports"})

TABLE_UNITS: dict[str, str] = {
    "exports_by_commodity": "Million dollars",
    "exports_by_state": "Million dollars",
    "top_exports": "Dollars",
    "top_imports": "Dollars",
}

STATE_CODE_TO_NAME: dict[str, str] = {
    "US": "United States",
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "VI": "Virgin Islands",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}

STATE_NAME_TO_CODE: dict[str, str] = {
    name: code for code, name in STATE_CODE_TO_NAME.items()
}

DATASET_A_CODES: frozenset[str] = frozenset(STATE_CODE_TO_NAME) - {"DC", "PR", "VI"}
DATASET_B_CODES: frozenset[str] = frozenset(STATE_CODE_TO_NAME)

NATIONAL_NAME = "United States"

COMMODITIES: tuple[str, ...] = (
    "Total agricultural exports",
    "Total animal products",
    "Total plant products",
    "Beef and veal",
    "Broiler meat",
    "Corn",
    "Cotton",
    "Dairy products",
    "Feeds and other feed grains",
    "Fruits, fresh",
    "Fruits, processed",
    "Grain products",
    "Hides and skins",
    "Other livestock products",
    "Other oilseeds and products",
    "Other plant products",
    "Other poultry products",
    "Pork",
    "Rice",
    "Soybean meal",
    "Soybeans",
    "Tobacco",
    "Tree nuts",
    "Vegetable oils",
    "Vegetables, fresh",
    "Vegetables, processed",
    "Wheat",
)

DEFAULT_TABLE = "exports_by_commodity"
DEFAULT_STATE = "California"
DEFAULT_COMMODITY = "Total agricultural exports"


def _state_names(codes: frozenset[str]) -> tuple[str, ...]:
    """Order a code set's names with the national total first, then alphabetically.

    Parameters
    ----------
    codes : frozenset[str]
        Two-letter state codes to render as labeled names.

    Returns
    -------
    tuple[str, ...]
        Full state names led by 'United States', the remaining names sorted.
    """
    others = sorted(STATE_CODE_TO_NAME[code] for code in codes if code != "US")
    return (NATIONAL_NAME, *others)


DATASET_A_STATE_NAMES: tuple[str, ...] = _state_names(DATASET_A_CODES)
DATASET_B_STATE_NAMES: tuple[str, ...] = _state_names(DATASET_B_CODES)


def allowed_state_names(table: str) -> tuple[str, ...]:
    """Return the state names published for a table's underlying dataset.

    Parameters
    ----------
    table : str
        Table key from TABLE_LABELS.

    Returns
    -------
    tuple[str, ...]
        The 51 calendar-year state names for the all-data tables, or the 54
        fiscal-year state names for the top-commodity tables.
    """
    return DATASET_B_STATE_NAMES if table in DATASET_B_TABLES else DATASET_A_STATE_NAMES


def state_options(table: str) -> list[dict]:
    """Build the labeled state options for a table's scoping selector.

    Parameters
    ----------
    table : str
        Table key from TABLE_LABELS.

    Returns
    -------
    list[dict]
        Label/value option dictionaries whose value is the full state name.
    """
    return [{"label": name, "value": name} for name in allowed_state_names(table)]


def commodity_options() -> list[dict]:
    """Build the labeled commodity options for the exports-by-state selector."""
    return [{"label": name, "value": name} for name in COMMODITIES]


def parse_value(raw: str | None) -> float | None:
    """Parse a raw numeric cell to a float, keeping full precision.

    Parameters
    ----------
    raw : str | None
        Raw value cell.

    Returns
    -------
    float | None
        The numeric value, or None when the cell is blank or non-numeric.
    """
    text = (raw or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_dataset_a(text: str) -> list[dict]:
    """Parse the all-data export CSV into tidy calendar-year records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the all-data file.

    Returns
    -------
    list[dict]
        Records with commodity, state (full name), year, unit, and value keys.
        Rows whose year token is non-numeric are skipped.
    """
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        year_token = (row.get("Year") or "").strip()
        if not year_token.isdigit():
            continue
        records.append(
            {
                "commodity": (row.get("Commodity") or "").strip(),
                "state": (row.get("State") or "").strip(),
                "year": int(year_token),
                "unit": (row.get("Units") or "").strip(),
                "value": parse_value(row.get("Value")),
            }
        )
    return records


def parse_dataset_b(text: str) -> list[dict]:
    """Parse a top-commodity fiscal-year CSV into all-destination annual totals.

    Parameters
    ----------
    text : str
        Decoded CSV text of a top-export or top-import file.

    Returns
    -------
    list[dict]
        Records with state (two-letter code), year (fiscal), commodity, and
        value keys, kept only for the World destination and the fiscal-year
        total quarter, and only for numeric fiscal years.
    """
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        if (row.get("Country") or "").strip() != "World":
            continue
        if (row.get("Fiscal quarter") or "").strip() != "0":
            continue
        year_token = (row.get("Fiscal year") or "").strip()
        if not year_token.isdigit():
            continue
        records.append(
            {
                "state": (row.get("State") or "").strip(),
                "year": int(year_token),
                "commodity": (row.get("Commodity name") or "").strip(),
                "value": parse_value(row.get("Dollar value")),
            }
        )
    return records


async def _afetch_csv(media_path: str) -> str:
    """Fetch and decode an ERS media CSV through the disk cache.

    Parameters
    ----------
    media_path : str
        Media path of the CSV to fetch.

    Returns
    -------
    str
        The decoded CSV text.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(media_path, product=PRODUCT_PAGE)
    return content.decode("utf-8-sig", errors="replace")


async def afetch_table(table: str) -> list[dict]:
    """Download and parse the long-format records backing a table.

    Parameters
    ----------
    table : str
        Table key from TABLE_LABELS.

    Returns
    -------
    list[dict]
        Calendar-year records from parse_dataset_a for the all-data tables, or
        fiscal-year all-destination records from parse_dataset_b for the
        top-commodity tables.
    """
    media_path = STATE_AG_TRADE_FILES[table][0]
    text = await _afetch_csv(media_path)
    if table in DATASET_A_TABLES:
        return parse_dataset_a(text)
    return parse_dataset_b(text)
