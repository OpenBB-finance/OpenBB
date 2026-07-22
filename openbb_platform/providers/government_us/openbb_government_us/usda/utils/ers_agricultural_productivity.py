"""USDA ERS Agricultural Productivity file catalog and long-format parser."""

import csv
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/agricultural-productivity-in-the-united-states"

NATIONAL_STATE = "US"

AGRICULTURAL_PRODUCTIVITY_FILES: dict[str, dict] = {
    "national_indices": {
        "label": "Table 1. Farm output, input, and TFP indices (U.S., 1948-2021)",
        "media": "/media/5406/table-1-indices-of-farm-outputs-inputs-and-total-factor"
        "-productivity-for-the-united-states-1948-2021.csv",
        "geography": "national",
        "year_col": "Year",
        "series_col": "Attribute",
        "value_col": "Value",
        "state_col": None,
    },
    "national_price_quantity": {
        "label": "Table 1a. Price indices and implicit quantities (U.S., 1948-2021)",
        "media": "/media/5407/table-1a-price-indices-and-implicit-quantities-of-farm"
        "-outputs-and-inputs-for-the-united-states-1948-2021.csv",
        "geography": "national",
        "year_col": "Year",
        "series_col": "Attribute",
        "value_col": "Value",
        "state_col": None,
    },
    "state_relative_levels": {
        "label": "Table 2. Relative levels of TFP, output & input indices"
        " (48 States, 1960-2015)",
        "media": "/media/5410/table-2-relative-levels-of-agricultural-total-factor"
        "-productivity-tfp-and-price-and-quantity-indices-for-outputs-and-inputs-for"
        "-the-48-contiguous-states-for-the-years-1960-2015.csv",
        "geography": "state",
        "year_col": "Year",
        "series_col": "Variable Name",
        "value_col": "Value",
        "state_col": "State",
    },
}

STATE_LABELS: dict[str, str] = {
    "US": "United States",
    "AL": "Alabama",
    "AR": "Arkansas",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MS": "Mississippi",
    "MT": "Montana",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
}

CONTIGUOUS_STATES: tuple[str, ...] = tuple(
    code for code in STATE_LABELS if code != NATIONAL_STATE
)


def allowed_states(table: str) -> tuple[str, ...]:
    """Return the state codes a table is published for.

    Parameters
    ----------
    table : str
        Table key from AGRICULTURAL_PRODUCTIVITY_FILES.

    Returns
    -------
    tuple[str, ...]
        ('US',) for the national tables, otherwise the 48 contiguous-state
        codes for the relative-levels table.
    """
    config = AGRICULTURAL_PRODUCTIVITY_FILES.get(table)
    if config is None or config["geography"] == "national":
        return (NATIONAL_STATE,)
    return CONTIGUOUS_STATES


def state_options(table: str) -> list[dict]:
    """Build the labeled state options a table is published for.

    Parameters
    ----------
    table : str
        Table key from AGRICULTURAL_PRODUCTIVITY_FILES.

    Returns
    -------
    list[dict]
        Label/value option dictionaries for the widget's state selector.
    """
    return [
        {"label": STATE_LABELS[code], "value": code} for code in allowed_states(table)
    ]


def parse_table(text: str, table: str) -> list[dict]:
    """Parse one table's CSV text into long-format observation records.

    Parameters
    ----------
    text : str
        Decoded CSV text of the table's media file.
    table : str
        Table key from AGRICULTURAL_PRODUCTIVITY_FILES.

    Returns
    -------
    list[dict]
        Records carrying the table key, integer year, the state code (None
        for the national tables), the series header, and the numeric value.
        Rows with a blank or non-numeric value, a non-four-digit year, or a
        blank series are skipped.
    """
    config = AGRICULTURAL_PRODUCTIVITY_FILES[table]
    year_col = config["year_col"]
    series_col = config["series_col"]
    value_col = config["value_col"]
    state_col = config["state_col"]
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        raw_value = (row.get(value_col) or "").strip()
        try:
            value = float(raw_value)
        except ValueError:
            continue
        year_raw = (row.get(year_col) or "").strip()
        if not (len(year_raw) == 4 and year_raw.isdigit()):
            continue
        series = (row.get(series_col) or "").strip()
        if not series:
            continue
        records.append(
            {
                "table": table,
                "year": int(year_raw),
                "state": (
                    ((row.get(state_col) or "").strip().upper() or None)
                    if state_col
                    else None
                ),
                "series": series,
                "value": value,
            }
        )
    return records


async def afetch_table(table: str, **kwargs) -> list[dict]:
    """Download and parse one productivity table through the ERS disk cache.

    Parameters
    ----------
    table : str
        Table key from AGRICULTURAL_PRODUCTIVITY_FILES.

    Returns
    -------
    list[dict]
        Long-format records from parse_table.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = AGRICULTURAL_PRODUCTIVITY_FILES[table]
    content = await afetch_ers_file(config["media"], product=PRODUCT_PAGE)
    return parse_table(content.decode("utf-8-sig", errors="replace"), table)
