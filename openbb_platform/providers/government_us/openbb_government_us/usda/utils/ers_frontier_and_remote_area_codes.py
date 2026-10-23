"""USDA ERS frontier and remote area codes (ZIP) catalog and parser."""

from io import BytesIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/frontier-and-remote-area-codes"

DEFAULT_YEAR = "2020"
DEFAULT_STATE = "MT"

CANONICAL_COLUMNS: tuple[str, ...] = (
    "zip_code",
    "state",
    "po_name",
    "far_level_1",
    "far_level_2",
    "far_level_3",
    "far_level_4",
    "grid_population",
    "land_area_sq_mi",
    "population_density",
    "far_level_1_population",
    "far_level_2_population",
    "far_level_3_population",
    "far_level_4_population",
    "far_level_1_population_pct",
    "far_level_2_population_pct",
    "far_level_3_population_pct",
    "far_level_4_population_pct",
)

CANONICAL_COLUMNS_NO_NAME: tuple[str, ...] = tuple(
    name for name in CANONICAL_COLUMNS if name != "po_name"
)

FAR_ZIP_FILES: dict[str, dict] = {
    "2020": {
        "media_id": 7072,
        "slug": "2020-far-codes-zip-codes",
        "ext": "xlsx",
        "sheet": "FAR2020 ZIP Code Data",
        "data_start": 2,
        "columns": CANONICAL_COLUMNS,
    },
    "2010": {
        "media_id": 5621,
        "slug": "2010-far-codes-zip-codes",
        "ext": "xlsx",
        "sheet": "FAR ZIP Code Data",
        "data_start": 2,
        "columns": CANONICAL_COLUMNS,
    },
    "2000": {
        "media_id": 5618,
        "slug": "2000-far-codes-zip-codes",
        "ext": "xls",
        "sheet": "FAR ZIP Code Data",
        "data_start": 1,
        "columns": CANONICAL_COLUMNS_NO_NAME,
    },
}

STATES_51: tuple[str, ...] = (
    "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI",
    "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN",
    "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH",
    "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA",
    "WI", "WV", "WY",
)  # fmt: skip

STATES_49: tuple[str, ...] = tuple(
    state for state in STATES_51 if state not in ("AK", "HI")
)

FAR_STATES: dict[str, tuple[str, ...]] = {
    "2020": STATES_51,
    "2010": STATES_51,
    "2000": STATES_49,
}

ALL_STATES: frozenset[str] = frozenset(STATES_51)

_STR_FIELDS: frozenset[str] = frozenset({"zip_code", "state", "po_name"})
_INT_FIELDS: frozenset[str] = frozenset(
    {"far_level_1", "far_level_2", "far_level_3", "far_level_4"}
)


def media_path(year: str) -> str:
    """Build the media path for a vintage's ZIP-code workbook.

    Parameters
    ----------
    year : str
        Vintage key from FAR_ZIP_FILES.

    Returns
    -------
    str
        The media path, e.g. '/media/7072/2020-far-codes-zip-codes.xlsx'.
    """
    config = FAR_ZIP_FILES[year]
    return f"/media/{config['media_id']}/{config['slug']}.{config['ext']}"


def year_options() -> list[dict]:
    """Build the labeled vintage options for the widget's vintage selector.

    Returns
    -------
    list[dict]
        Label/value option dictionaries, one per published vintage.
    """
    return [{"label": year, "value": year} for year in FAR_ZIP_FILES]


def state_options(year: str) -> list[dict]:
    """Build the labeled state options a vintage publishes.

    Parameters
    ----------
    year : str
        Vintage key. Unknown vintages fall back to the default vintage.

    Returns
    -------
    list[dict]
        Label/value option dictionaries for the widget's state selector.
    """
    states = FAR_STATES.get(year) or FAR_STATES[DEFAULT_YEAR]
    return [{"label": state, "value": state} for state in states]


def _to_str(value) -> str | None:
    """Coerce a source cell to a stripped string, None when blank."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _to_int(value) -> int | None:
    """Coerce a source cell to an integer flag, None when blank or non-numeric."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _to_float(value) -> float | None:
    """Coerce a source cell to a float, None when blank or non-numeric."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _map_row(cells: list, columns: tuple[str, ...]) -> dict:
    """Map one positional source row to the canonical column dictionary.

    Parameters
    ----------
    cells : list
        Ordered cell values of one data row.
    columns : tuple[str, ...]
        Canonical column names in positional order for the vintage.

    Returns
    -------
    dict
        Canonical record with string identifiers, integer FAR flags, and float
        population and area attributes.
    """
    record: dict = {}
    for index, name in enumerate(columns):
        value = cells[index] if index < len(cells) else None
        if name in _STR_FIELDS:
            record[name] = _to_str(value)
        elif name in _INT_FIELDS:
            record[name] = _to_int(value)
        else:
            record[name] = _to_float(value)
    return record


def parse_rows(rows: list, year: str) -> list[dict]:
    """Parse a vintage's worksheet rows into canonical ZIP-code records.

    Parameters
    ----------
    rows : list
        The worksheet's value rows, each an ordered sequence of cell values,
        including the title and header rows.
    year : str
        Vintage key from FAR_ZIP_FILES, selecting the header offset and the
        per-vintage positional column map.

    Returns
    -------
    list[dict]
        One canonical record per ZIP-code row. Rows with a blank ZIP code are
        skipped; the 2000 vintage carries no area name so po_name is absent.
    """
    config = FAR_ZIP_FILES[year]
    columns = config["columns"]
    records: list[dict] = []
    for raw in rows[config["data_start"] :]:
        cells = list(raw)
        if not cells:
            continue
        first = cells[0]
        if first is None or str(first).strip() == "":
            continue
        records.append(_map_row(cells, columns))
    return records


def _read_sheet_rows(content: bytes, year: str) -> list[list]:
    """Read a vintage workbook's data sheet into a list of row lists.

    Parameters
    ----------
    content : bytes
        Raw workbook bytes, an .xlsx for 2020 and 2010 or a legacy .xls for
        2000.
    year : str
        Vintage key from FAR_ZIP_FILES.

    Returns
    -------
    list[list]
        Cell values, row by row, including the title and header rows.
    """
    config = FAR_ZIP_FILES[year]
    if config["ext"] == "xls":
        import xlrd

        sheet = xlrd.open_workbook(file_contents=content).sheet_by_name(config["sheet"])
        return [
            [sheet.cell_value(r, c) for c in range(sheet.ncols)]
            for r in range(sheet.nrows)
        ]
    import openpyxl

    workbook = openpyxl.load_workbook(BytesIO(content), read_only=True, data_only=True)
    try:
        return [
            list(row) for row in workbook[config["sheet"]].iter_rows(values_only=True)
        ]
    finally:
        workbook.close()


async def afetch_far_zip(year: str) -> list[dict]:
    """Download a vintage's ZIP-code workbook and parse it through the cache.

    Parameters
    ----------
    year : str
        Vintage key from FAR_ZIP_FILES.

    Returns
    -------
    list[dict]
        Canonical records from parse_rows for the selected vintage.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(media_path(year), product=PRODUCT_PAGE)
    return parse_rows(_read_sheet_rows(content, year), year)
