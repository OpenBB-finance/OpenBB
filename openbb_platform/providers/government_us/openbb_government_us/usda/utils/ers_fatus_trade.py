"""USDA ERS U.S. Agricultural Trade Data Update file catalog and parsers."""

import csv
import re
from collections import OrderedDict
from io import StringIO

from openbb_core.app.model.abstract.error import OpenBBError

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = (
    "data-products/foreign-agricultural-trade-of-the-united-states-fatus"
    "/us-agricultural-trade-data-update"
)
MEDIA_PATH = "/media/5029/csv-comma-separated-values-format-of-all-data.csv"

TRADE_TABLES: dict[str, str] = {
    "summary": "U.S. agricultural trade, fiscal years, calendar years,"
    " year-to-date, and current month",
    "monthly": "Total value of U.S. agricultural trade and trade balance, monthly",
    "exports_ytd": "U.S. agricultural exports, year-to-date and current months",
    "imports_ytd": "U.S. agricultural imports, year-to-date and current months",
    "top_export_markets": "Top 10 U.S. export markets for soybeans, corn, wheat,"
    " and cotton, by volume",
    "top_import_sources": "Top 10 sources of U.S. imports of fruits and vegetables,"
    " by value",
}

TABLE_ALIASES = {name: alias for alias, name in TRADE_TABLES.items()}

DIRECTIONS = {
    "Exports": "exports",
    "Imports": "imports",
    "Trade balance (exports minus imports)": "balance",
}

VALUE_TYPES = {
    "Customs value": "value",
    "Volume": "volume",
    "Cost, insurance, and freight (c.i.f.)": "cif",
}

TABLE_MEASURES: dict[str, list[str]] = {
    "summary": ["value"],
    "monthly": ["value"],
    "exports_ytd": ["value", "volume"],
    "imports_ytd": ["value", "volume", "cif"],
    "top_export_markets": ["volume"],
    "top_import_sources": ["value"],
}

MEASURE_LABELS: dict[str, str] = {
    "value": "Value",
    "volume": "Volume",
    "cif": "CIF value",
}

SPREAD_DIMENSION: dict[str, str] = {
    "summary": "direction",
    "monthly": "direction",
    "exports_ytd": "commodity",
    "imports_ytd": "commodity",
    "top_export_markets": "country",
    "top_import_sources": "country",
}

DIRECTION_LABELS: "OrderedDict[str, str]" = OrderedDict(
    [("exports", "Exports"), ("imports", "Imports"), ("balance", "Balance")]
)

MONTH_INDEX: dict[str, int] = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

LABEL_FIXES = {
    "Korea, South": "South Korea",
    "Cotton, ex linters": "Cotton, excluding linters",
}

FISCAL_MONTH_ORDER = {
    "October": 1,
    "November": 2,
    "December": 3,
    "January": 4,
    "February": 5,
    "March": 6,
    "April": 7,
    "May": 8,
    "June": 9,
    "July": 10,
    "August": 11,
    "September": 12,
}

VINTAGE_PATTERN = re.compile(r"update of ([A-Za-z]+)")


def build_url() -> str:
    """Build the download URL of the all-data CSV."""
    return f"{BASE_URL}{MEDIA_PATH}"


def vintage_order(update_version: str | None) -> int:
    """Rank a monthly update vintage by its data month in fiscal-year order.

    Parameters
    ----------
    update_version : str | None
        Published vintage label, e.g. 'July update of May data'.

    Returns
    -------
    int
        Position of the data month within the October-September fiscal year,
        or 0 when the vintage is missing or unrecognized.
    """
    if not update_version:
        return 0
    match = VINTAGE_PATTERN.search(update_version)
    if match is None:
        return 0
    return FISCAL_MONTH_ORDER.get(match[1], 0)


def period_rank(period: str) -> int:
    """Rank a time period within its year for chronological row ordering.

    Parameters
    ----------
    period : str
        Published time period, e.g. 'May', 'January-May', 'October-May', or
        'Fiscal year, October-September'.

    Returns
    -------
    int
        Sort rank placing bare calendar months (1-12) first, then calendar
        year-to-date spans (100 + end month), then fiscal year-to-date spans
        (200 + end month), then the annual fiscal-year (900) and calendar-year
        (901) totals; 500 for an unrecognized period.
    """
    if period in MONTH_INDEX:
        return MONTH_INDEX[period]
    if period.startswith("Fiscal year"):
        return 900
    if period.startswith("Calendar year"):
        return 901
    parts = period.split("-")
    if len(parts) == 2 and parts[0] in MONTH_INDEX and parts[1] in MONTH_INDEX:
        if parts[0] == "January":
            return 100 + MONTH_INDEX[parts[1]]
        return 200 + MONTH_INDEX[parts[1]]
    return 500


PERIOD_BASIS_ORDER = (
    "Fiscal year",
    "Calendar year",
    "Fiscal year-to-date",
    "Calendar year-to-date",
    "Monthly",
)


def classify_period(period: str) -> str | None:
    """Classify a published time period into its reporting basis.

    Parameters
    ----------
    period : str
        Published time period, e.g. 'May', 'January-May', 'October-May',
        'Fiscal year, October-September', or a 'Change, ...' delta row.

    Returns
    -------
    str | None
        One of 'Fiscal year', 'Calendar year', 'Fiscal year-to-date',
        'Calendar year-to-date', or 'Monthly'; None for change rows and
        unrecognized periods.
    """
    if period.startswith("Fiscal year"):
        return "Fiscal year"
    if period.startswith("Calendar year"):
        return "Calendar year"
    if period in MONTH_INDEX:
        return "Monthly"
    parts = period.split("-")
    if len(parts) == 2 and parts[0] in MONTH_INDEX and parts[1] in MONTH_INDEX:
        return (
            "Calendar year-to-date" if parts[0] == "January" else "Fiscal year-to-date"
        )
    return None


def within_year_rank(basis: str, period: str) -> int:
    """Rank a period within its year for chronological ordering under a basis.

    Parameters
    ----------
    basis : str
        The reporting basis from classify_period.
    period : str
        Published time period.

    Returns
    -------
    int
        The month or fiscal-month position that orders the rows within a year;
        zero for the annual bases, whose year alone orders the series.
    """
    if basis == "Monthly":
        return MONTH_INDEX.get(period, 0)
    if basis == "Calendar year-to-date":
        return MONTH_INDEX.get(period.split("-")[1], 0)
    if basis == "Fiscal year-to-date":
        return FISCAL_MONTH_ORDER.get(period.split("-")[1], 0)
    return 0


async def table_period_bases(table: str, **kwargs) -> list[str]:
    """List the period bases a trade table publishes, coarsest first.

    Parameters
    ----------
    table : str
        Table key from TRADE_TABLES.

    Returns
    -------
    list[str]
        Distinct reporting bases present in the table, ordered from the annual
        totals through the year-to-date spans to the monthly rows.
    """
    records = await afetch_trade_data()
    present = {
        classify_period(record["time_period"])
        for record in records
        if record["table"] == table
    }
    return [basis for basis in PERIOD_BASIS_ORDER if basis in present]


def filter_latest(records: list[dict]) -> list[dict]:
    """Keep only each table's most recent monthly update vintage.

    Parameters
    ----------
    records : list[dict]
        Parsed row records from parse_rows.

    Returns
    -------
    list[dict]
        Rows whose vintage matches the per-table maximum; rows without an
        update vintage pass through unchanged.
    """
    latest: dict[str, int] = {}
    for record in records:
        order = vintage_order(record["update_version"])
        if order > latest.get(record["table"], 0):
            latest[record["table"]] = order
    return [
        record
        for record in records
        if record["update_version"] is None
        or vintage_order(record["update_version"]) == latest.get(record["table"], 0)
    ]


def _clean(value: str | None) -> str | None:
    """Strip a raw CSV cell, mapping empty text and the 'NA' sentinel to None."""
    text = (value or "").strip()
    if not text or text == "NA":
        return None
    return text


def parse_rows(text: str) -> list[dict]:
    """Parse the all-data CSV text into tidy row records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the FATUS all-data file.

    Returns
    -------
    list[dict]
        Records with table, source_table, commodity, country, time_period,
        year (raw string), direction, value_type, units, value,
        update_version, notes, and data_source keys, skipping rows with an
        empty Value.

    Raises
    ------
    OpenBBError
        If a row carries an unrecognized source table, trade direction, or
        value type.
    """
    reader = csv.DictReader(StringIO(text))
    reader.fieldnames = [name.strip() for name in reader.fieldnames or []]
    rows: list[dict] = []
    for row in reader:
        value = (row.get("Value") or "").strip()
        if not value:
            continue
        source_table = (row.get("Source_table") or "").strip()
        table = TABLE_ALIASES.get(source_table)
        if table is None:
            raise OpenBBError(
                f"Unrecognized source table: '{source_table}'."
                + " Expected one of: "
                + "; ".join(sorted(TABLE_ALIASES))
            )
        direction_text = (row.get("US_Trade") or "").strip()
        direction = DIRECTIONS.get(direction_text)
        if direction is None:
            raise OpenBBError(
                f"Unrecognized trade direction: '{direction_text}'."
                + " Expected one of: "
                + "; ".join(sorted(DIRECTIONS))
            )
        value_type_text = (row.get("Value_type") or "").strip()
        value_type = VALUE_TYPES.get(value_type_text)
        if value_type is None:
            raise OpenBBError(
                f"Unrecognized value type: '{value_type_text}'."
                + " Expected one of: "
                + "; ".join(sorted(VALUE_TYPES))
            )
        commodity = (row.get("Commodity") or "").strip()
        country = (row.get("Country") or "").strip()
        rows.append(
            {
                "table": table,
                "source_table": source_table,
                "commodity": LABEL_FIXES.get(commodity, commodity),
                "country": LABEL_FIXES.get(country, country),
                "time_period": (row.get("Time_period") or "").strip(),
                "year": (row.get("Year") or "").strip(),
                "direction": direction,
                "value_type": value_type,
                "units": (row.get("Units") or "").strip(),
                "value": float(value),
                "update_version": _clean(row.get("Update_version")),
                "notes": _clean(row.get("Notes")),
                "data_source": _clean(row.get("Data_source")),
            }
        )
    return rows


async def afetch_trade_data(**kwargs) -> list[dict]:
    """Download and parse the all-data CSV through the ERS disk cache.

    Returns
    -------
    list[dict]
        Raw row records from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(MEDIA_PATH, product=PRODUCT_PAGE)
    return parse_rows(content.decode("utf-8-sig"))


async def distinct_field(field: str, table: str | None = None) -> list[str]:
    """List the distinct values of a field, optionally scoped to a table.

    Parameters
    ----------
    field : str
        Record field to enumerate, e.g. 'commodity' or 'country'.
    table : str | None
        Table slug, or a comma-separated list, to scope the values to. When
        None, values from every table are returned.

    Returns
    -------
    list[str]
        The distinct non-empty values, in first-seen source order.
    """
    records = await afetch_trade_data()
    tables = (
        {slug.strip() for slug in table.split(",") if slug.strip()} if table else None
    )
    seen: dict[str, None] = {}
    for record in records:
        if tables is not None and record["table"] not in tables:
            continue
        value = record.get(field)
        if value:
            seen.setdefault(value, None)
    return list(seen)
