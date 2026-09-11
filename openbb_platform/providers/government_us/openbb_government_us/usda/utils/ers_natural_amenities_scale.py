"""USDA ERS natural amenities scale catalog and county-lookup parser."""

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/natural-amenities-scale"
MEDIA_PATH = (
    "/media/6172/natural-amenities-scale-including-the-6-components-for-us-counties.xls"
)
SHEET = "NATAMENF"
DATA_START = 105

COLUMN_SPECS: tuple[tuple[str, str], ...] = (
    ("fips", "text"),
    ("fips_used_for_measures", "text"),
    ("state", "text"),
    ("county_name", "text"),
    ("census_division", "code"),
    ("rural_urban_continuum_code", "code"),
    ("urban_influence_code", "code"),
    ("mean_january_temperature", "num"),
    ("mean_january_sunlight", "num"),
    ("mean_july_temperature", "num"),
    ("mean_july_humidity", "num"),
    ("topography_code", "code"),
    ("percent_water_area", "num"),
    ("log_water_area", "num"),
    ("january_temperature_z", "num"),
    ("january_sunlight_z", "num"),
    ("july_temperature_z", "num"),
    ("july_humidity_z", "num"),
    ("topography_z", "num"),
    ("log_water_area_z", "num"),
    ("natural_amenity_scale", "num"),
    ("natural_amenity_rank", "code"),
)

CANONICAL_COLUMNS: tuple[str, ...] = tuple(name for name, _ in COLUMN_SPECS)

STATE_NAMES: dict[str, str] = {
    "AL": "Alabama",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
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
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}

STATES: tuple[str, ...] = tuple(sorted(STATE_NAMES))
ALL_STATES: frozenset[str] = frozenset(STATE_NAMES)


def state_options() -> list[dict]:
    """Build the labeled state options for the widget's state selector.

    Returns
    -------
    list[dict]
        Label/value option dictionaries, one per state or DC, in code order.
    """
    return [{"label": STATE_NAMES[code], "value": code} for code in STATES]


def _to_text(value) -> str | None:
    """Coerce a source cell to a stripped string, None when blank."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _to_code(value) -> str | None:
    """Coerce an integer-valued source cell to a code string, None when blank.

    Parameters
    ----------
    value : object
        A raw classification cell, stored as an integer-valued float such as
        6.0, or a blank cell.

    Returns
    -------
    str | None
        The integer code as a string, e.g. '6', or None when blank; a
        non-numeric cell is returned as its stripped text.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        return str(int(float(value)))
    except (TypeError, ValueError):
        return str(value).strip() or None


def _to_num(value) -> float | None:
    """Coerce a source cell to a float, None when blank or non-numeric."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_rows(rows: list, data_start: int = DATA_START) -> list[dict]:
    """Parse the worksheet rows into canonical county-lookup records.

    Parameters
    ----------
    rows : list
        The worksheet's value rows, each an ordered sequence of cell values,
        including the leading legend, notes, and header band.
    data_start : int
        Zero-indexed row where county data begins, after the header band.

    Returns
    -------
    list[dict]
        One canonical record per county row, keyed by CANONICAL_COLUMNS. Rows
        with a blank first cell are skipped.
    """
    records: list[dict] = []
    for raw in rows[data_start:]:
        cells = list(raw)
        if not cells:
            continue
        first = cells[0]
        if first is None or str(first).strip() == "":
            continue
        record: dict = {}
        for index, (name, kind) in enumerate(COLUMN_SPECS):
            cell = cells[index] if index < len(cells) else None
            if kind == "text":
                record[name] = _to_text(cell)
            elif kind == "code":
                record[name] = _to_code(cell)
            else:
                record[name] = _to_num(cell)
        records.append(record)
    return records


def _read_sheet_rows(content: bytes) -> list[list]:
    """Read the legacy .xls data sheet into a list of row lists via xlrd.

    Parameters
    ----------
    content : bytes
        Raw legacy .xls bytes of the natural amenities workbook.

    Returns
    -------
    list[list]
        Cell values, row by row, including the legend, notes, and header band.
    """
    import xlrd

    sheet = xlrd.open_workbook(file_contents=content).sheet_by_name(SHEET)
    return [
        [sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)
    ]


async def afetch_records() -> list[dict]:
    """Download and parse the natural amenities workbook through the cache.

    Returns
    -------
    list[dict]
        One canonical record per county from parse_rows.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(MEDIA_PATH, product=PRODUCT_PAGE)
    return parse_rows(_read_sheet_rows(content))
