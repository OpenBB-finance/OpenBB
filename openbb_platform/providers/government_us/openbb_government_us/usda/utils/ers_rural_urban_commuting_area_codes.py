"""USDA ERS Rural-Urban Commuting Area Codes catalog, fetch, and parsers."""

import csv
import io
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/rural-urban-commuting-area-codes"

TABLE_CATALOG: dict[str, tuple[str, str]] = {
    "tract_2020": (
        "/media/5443/2020-rural-urban-commuting-area-codes-census-tracts.csv",
        "csv",
    ),
    "tract_2010": (
        "/media/5438/2010-rural-urban-commuting-area-codes-revised-732019.xlsx",
        "xlsx",
    ),
    "tract_2000": (
        "/media/5437/2000-rural-urban-commuting-area-codes.xls",
        "xls",
    ),
    "tract_1990": (
        "/media/5436/1990-rural-urban-commuting-area-codes.xls",
        "xls",
    ),
    "zip_2020": (
        "/media/5444/2020-rural-urban-commuting-area-codes-zip-codes.csv",
        "csv",
    ),
    "zip_2010": (
        "/media/5440/2010-rural-urban-commuting-area-codes-zip-code-file.csv",
        "csv",
    ),
}

TABLE_LABELS: dict[str, str] = {
    "tract_2020": "Census tracts, 2020",
    "tract_2010": "Census tracts, 2010",
    "tract_2000": "Census tracts, 2000",
    "tract_1990": "Census tracts, 1990",
    "zip_2020": "ZIP codes, 2020",
    "zip_2010": "ZIP codes, 2010",
}

DEFAULT_TABLE = "tract_2020"
DEFAULT_STATE = "DE"

PRIMARY_DESCRIPTIONS: dict[str, str] = {
    "1": "Metropolitan core",
    "2": "Metropolitan high commuting",
    "3": "Metropolitan low commuting",
    "4": "Micropolitan core",
    "5": "Micropolitan high commuting",
    "6": "Micropolitan low commuting",
    "7": "Small town core",
    "8": "Small town high commuting",
    "9": "Small town low commuting",
    "10": "Rural area",
    "99": "Not coded",
}

SECONDARY_DESCRIPTIONS: dict[str, str] = {
    "1": "Metropolitan core, no addtional code",
    "1.1": "Metropolitan core, secondary flow to larger UA",
    "2": "Metropolitan high commuting, no additional code",
    "2.1": "Metropolitan high commuting, seconary flow to larger UA",
    "3": "Metropolitan low commuting, no additional code",
    "4": "Micropolitan core, no additional code",
    "4.1": "Micropolitan core, secondary flow to metro UA",
    "5": "Micropolitan high commuting, no additional code",
    "5.1": "Micropolitan high commuting, seconary flow to metro UA",
    "6": "Micropolitan low commuting, no additional code",
    "7": "Small town core, no additional code",
    "7.1": "Small town core, secondary flow to metro UA",
    "7.2": "Small town core, secondary flow to micro UA",
    "8": "Small town high commuting, no additional code",
    "8.1": "Small town high commuting, seconary flow to metro UA",
    "8.2": "Small town high commuting, secondary flow to micro UA",
    "9": "Small town low commuting, no additional code",
    "10": "Rural area, no additional code",
    "10.1": "Rural area, seconary flow to metro UA",
    "10.2": "Rural area, secondary flow to micro UA",
    "10.3": "Rural area, secondary flow to small town UA",
    "99": "Not coded",
}

FIPS_TO_STATE: dict[str, str] = {
    "01": "AL",
    "02": "AK",
    "04": "AZ",
    "05": "AR",
    "06": "CA",
    "08": "CO",
    "09": "CT",
    "10": "DE",
    "11": "DC",
    "12": "FL",
    "13": "GA",
    "15": "HI",
    "16": "ID",
    "17": "IL",
    "18": "IN",
    "19": "IA",
    "20": "KS",
    "21": "KY",
    "22": "LA",
    "23": "ME",
    "24": "MD",
    "25": "MA",
    "26": "MI",
    "27": "MN",
    "28": "MS",
    "29": "MO",
    "30": "MT",
    "31": "NE",
    "32": "NV",
    "33": "NH",
    "34": "NJ",
    "35": "NM",
    "36": "NY",
    "37": "NC",
    "38": "ND",
    "39": "OH",
    "40": "OK",
    "41": "OR",
    "42": "PA",
    "44": "RI",
    "45": "SC",
    "46": "SD",
    "47": "TN",
    "48": "TX",
    "49": "UT",
    "50": "VT",
    "51": "VA",
    "53": "WA",
    "54": "WV",
    "55": "WI",
    "56": "WY",
    "60": "AS",
    "66": "GU",
    "69": "MP",
    "72": "PR",
    "78": "VI",
}

STATE_NAMES: dict[str, str] = {
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
    "AS": "American Samoa",
    "GU": "Guam",
    "MP": "Northern Mariana Islands",
    "PR": "Puerto Rico",
    "VI": "U.S. Virgin Islands",
}

_STATES_50_DC: tuple[str, ...] = tuple(
    sorted(code for code in STATE_NAMES if code not in {"AS", "GU", "MP", "PR", "VI"})
)
_STATES_50_DC_PR: tuple[str, ...] = tuple(sorted((*_STATES_50_DC, "PR")))
_STATES_ALL: tuple[str, ...] = tuple(sorted(STATE_NAMES))

TABLE_STATES: dict[str, tuple[str, ...]] = {
    "tract_2020": _STATES_ALL,
    "zip_2020": _STATES_ALL,
    "tract_2010": _STATES_50_DC_PR,
    "zip_2010": _STATES_50_DC_PR,
    "tract_2000": _STATES_50_DC,
    "tract_1990": _STATES_50_DC,
}


def normalize_code(value) -> str | None:
    """Normalize a RUCA code to its canonical string form.

    Parameters
    ----------
    value : Any
        A code as a string, integer, or float across the source vintages,
        e.g. '1', 1, 2.0, '2.1', or '99.0'.

    Returns
    -------
    str | None
        The code with any trailing '.0' dropped, e.g. '2', '2.1', '10', or
        '99'; None for a blank or non-numeric value.
    """
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            number = float(text)
        except ValueError:
            return text
    else:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
    if number.is_integer():
        return str(int(number))
    return str(number)


def primary_description(code: str | None) -> str | None:
    """Return the canonical primary RUCA label for a normalized code."""
    if code is None:
        return None
    return PRIMARY_DESCRIPTIONS.get(code)


def secondary_description(code: str | None) -> str | None:
    """Return the secondary RUCA label for a normalized code.

    Parameters
    ----------
    code : str | None
        A normalized secondary code, e.g. '2.1' or '5.2'.

    Returns
    -------
    str | None
        The 2020 secondary label when the exact code is published, otherwise
        the primary label of the code's integer part so granular sub-codes of
        the older vintages still carry a description.
    """
    if code is None:
        return None
    if code in SECONDARY_DESCRIPTIONS:
        return SECONDARY_DESCRIPTIONS[code]
    return PRIMARY_DESCRIPTIONS.get(code.split(".")[0])


def allowed_states(table: str) -> tuple[str, ...]:
    """Return the two-letter state codes a table publishes, led alphabetically."""
    return TABLE_STATES.get(table, _STATES_ALL)


def state_options(table: str) -> list[dict]:
    """Build the labeled state options a table publishes for the selector."""
    return [
        {"label": STATE_NAMES[code], "value": code} for code in allowed_states(table)
    ]


def _to_int(value) -> int | None:
    """Parse a population count to an int, keeping the exact value."""
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return int(float(text))
        except ValueError:
            return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_float(value) -> float | None:
    """Parse a measure to a float, keeping full precision."""
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fips_str(value, width: int) -> str | None:
    """Return a zero-padded FIPS or ZIP string, preserving leading zeros.

    Parameters
    ----------
    value : Any
        The raw identifier as text or a number.
    width : int
        The fixed identifier width, 11 for a census tract or 5 for a ZIP.

    Returns
    -------
    str | None
        The identifier as a fixed-width digit string, or the stripped text
        when it is not purely numeric; None when blank.
    """
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
    else:
        number = _to_int(value)
        text = "" if number is None else str(number)
    if not text:
        return None
    if text.isdigit():
        return text.zfill(width)
    return text


def _mapped_record(
    area_fips: str | None,
    state: str | None,
    primary: str | None,
    secondary: str | None,
    *,
    county: str | None = None,
    area_name: str | None = None,
    area_type: str | None = None,
    population: int | None = None,
    land_area: float | None = None,
    population_density: float | None = None,
    primary_desc: str | None = None,
    secondary_desc: str | None = None,
) -> dict:
    """Assemble one unified lookup record with canonical descriptions."""
    return {
        "area_fips": area_fips,
        "state": state,
        "area_name": area_name,
        "county": county,
        "area_type": area_type,
        "primary_ruca": primary,
        "primary_ruca_description": (
            primary_desc if primary_desc else primary_description(primary)
        ),
        "secondary_ruca": secondary,
        "secondary_ruca_description": (
            secondary_desc if secondary_desc else secondary_description(secondary)
        ),
        "population": population,
        "land_area": land_area,
        "population_density": population_density,
    }


def parse_tract_2020(text: str, state: str | None) -> list[dict]:
    """Parse the 2020 census-tract CSV into unified lookup records."""
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        code = (row.get("StateFIPS20") or "").strip()
        row_state = FIPS_TO_STATE.get(code)
        if state is not None and row_state != state:
            continue
        records.append(
            _mapped_record(
                _fips_str(row.get("TractFIPS20"), 11),
                row_state,
                normalize_code(row.get("PrimaryRUCA")),
                normalize_code(row.get("SecondaryRUCA")),
                county=(row.get("CountyName20") or "").strip() or None,
                area_name=(row.get("TractName20") or "").strip() or None,
                population=_to_int(row.get("Population")),
                land_area=_to_float(row.get("LandArea")),
                population_density=_to_float(row.get("PopDensity")),
                primary_desc=(row.get("PrimaryRUCADescription") or "").strip() or None,
                secondary_desc=(row.get("SecondaryRUCADescription") or "").strip()
                or None,
            )
        )
    return records


def parse_zip_2020(text: str, state: str | None) -> list[dict]:
    """Parse the 2020 ZIP-code CSV into unified lookup records."""
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        row_state = (row.get("State") or "").strip().upper() or None
        if state is not None and row_state != state:
            continue
        records.append(
            _mapped_record(
                _fips_str(row.get("ZIPCode"), 5),
                row_state,
                normalize_code(row.get("PrimaryRUCA")),
                normalize_code(row.get("SecondaryRUCA")),
                area_name=(row.get("POName") or "").strip() or None,
                area_type=(row.get("ZIPCodeType") or "").strip() or None,
            )
        )
    return records


def parse_zip_2010(text: str, state: str | None) -> list[dict]:
    """Parse the 2010 ZIP-code CSV into unified lookup records."""
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        row_state = (row.get("STATE") or "").strip().upper() or None
        if state is not None and row_state != state:
            continue
        raw_zip = (row.get("''ZIP_CODE''") or "").strip().strip("'")
        records.append(
            _mapped_record(
                _fips_str(raw_zip, 5),
                row_state,
                normalize_code(row.get("RUCA1")),
                normalize_code(row.get("RUCA2")),
                area_type=(row.get("ZIP_TYPE") or "").strip() or None,
            )
        )
    return records


def _xlsx_data_rows(content: bytes) -> list[tuple]:
    """Read the 'Data' worksheet of an XLSX workbook into value rows."""
    import openpyxl

    workbook = openpyxl.load_workbook(
        io.BytesIO(content), data_only=True, read_only=True
    )
    rows = list(workbook["Data"].iter_rows(values_only=True))
    workbook.close()
    return rows


def _xls_data_rows(content: bytes) -> list[list]:
    """Read the 'Data' worksheet of a legacy XLS workbook into value rows."""
    import xlrd

    sheet = xlrd.open_workbook(file_contents=content).sheet_by_name("Data")
    return [
        [sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)
    ]


def parse_tract_2010(content: bytes, state: str | None) -> list[dict]:
    """Parse the 2010 census-tract XLSX into unified lookup records."""
    records: list[dict] = []
    for row in _xlsx_data_rows(content)[2:]:
        row_state = (str(row[1]).strip().upper() or None) if row[1] else None
        if state is not None and row_state != state:
            continue
        records.append(
            _mapped_record(
                _fips_str(row[3], 11),
                row_state,
                normalize_code(row[4]),
                normalize_code(row[5]),
                county=(str(row[2]).strip() or None) if row[2] else None,
                population=_to_int(row[6]),
                land_area=_to_float(row[7]),
                population_density=_to_float(row[8]),
            )
        )
    return records


def parse_tract_2000(content: bytes, state: str | None) -> list[dict]:
    """Parse the 2000 census-tract XLS into unified lookup records."""
    records: list[dict] = []
    for row in _xls_data_rows(content)[1:]:
        row_state = (str(row[1]).strip().upper() or None) if row[1] else None
        if state is not None and row_state != state:
            continue
        records.append(
            _mapped_record(
                _fips_str(row[3], 11),
                row_state,
                normalize_code(row[4]),
                normalize_code(row[5]),
                county=(str(row[2]).strip() or None) if row[2] else None,
                population=_to_int(row[6]),
            )
        )
    return records


def parse_tract_1990(content: bytes, state: str | None) -> list[dict]:
    """Parse the 1990 census-tract XLS into unified lookup records.

    The 1990 file carries a single combined code, so the integer part becomes
    the primary code and the full code becomes the secondary code, and the
    FIPS is reformatted from '010010201.00' to the 11-digit '01001020100'.
    """
    records: list[dict] = []
    for row in _xls_data_rows(content)[2:]:
        area_fips = _fips_str(str(row[0]).replace(".", ""), 11)
        row_state = FIPS_TO_STATE.get(area_fips[:2]) if area_fips else None
        if state is not None and row_state != state:
            continue
        secondary = normalize_code(row[1])
        primary = secondary.split(".")[0] if secondary else None
        records.append(
            _mapped_record(
                area_fips,
                row_state,
                primary,
                secondary,
                population=_to_int(row[2]),
                land_area=_to_float(row[3]),
            )
        )
    return records


CSV_PARSERS = {
    "tract_2020": parse_tract_2020,
    "zip_2020": parse_zip_2020,
    "zip_2010": parse_zip_2010,
}

BINARY_PARSERS = {
    "tract_2010": parse_tract_2010,
    "tract_2000": parse_tract_2000,
    "tract_1990": parse_tract_1990,
}


async def afetch_table(table: str, state: str | None) -> list[dict]:
    """Download one vintage file and parse it into unified lookup records.

    Parameters
    ----------
    table : str
        Table key from TABLE_CATALOG.
    state : str | None
        Two-letter state code to keep, or None for every area.

    Returns
    -------
    list[dict]
        Unified lookup records for the selected table and state filter.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    media_path, kind = TABLE_CATALOG[table]
    content = await afetch_ers_file(media_path, product=PRODUCT_PAGE)
    if kind == "csv":
        return CSV_PARSERS[table](content.decode("utf-8-sig", errors="replace"), state)
    return BINARY_PARSERS[table](content, state)
