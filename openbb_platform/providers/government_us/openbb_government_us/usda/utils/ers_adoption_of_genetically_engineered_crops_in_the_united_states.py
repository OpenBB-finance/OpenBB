"""USDA ERS adoption of genetically engineered crops catalog and parser."""

import re
from io import BytesIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = (
    "data-products/adoption-of-genetically-engineered-crops-in-the-united-states"
)
MEDIA_PATH = (
    "/media/5685/genetically-engineered-varieties-of-corn-upland-cotton-and"
    "-soybeans-by-state-and-for-the-united-states-2000-25.xlsx"
)

DEFAULT_CROP = "corn"
DEFAULT_STATE = "United States"

CROPS: dict[str, dict] = {
    "corn": {
        "label": "Corn",
        "sheet": "Corn",
        "traits": ("Bt only", "HT only", "Stacked", "All GE"),
    },
    "cotton": {
        "label": "Upland cotton",
        "sheet": "Cotton",
        "traits": ("Bt only", "HT only", "Stacked", "All GE"),
    },
    "soybeans": {
        "label": "Soybeans",
        "sheet": "Soybeans",
        "traits": ("HT only", "All GE"),
    },
}

TRAIT_PREFIXES: tuple[tuple[str, str], ...] = (
    ("insect-resistant (bt) only", "Bt only"),
    ("herbicide-tolerant (ht) only", "HT only"),
    ("stacked gene varieties", "Stacked"),
    ("all ge varieties", "All GE"),
)

CROP_STATES: dict[str, tuple[str, ...]] = {
    "corn": (
        "Illinois",
        "Indiana",
        "Iowa",
        "Kansas",
        "Michigan",
        "Minnesota",
        "Missouri",
        "Nebraska",
        "North Dakota",
        "Ohio",
        "South Dakota",
        "Texas",
        "Wisconsin",
        "Other States",
        "United States",
    ),
    "cotton": (
        "Alabama",
        "Arkansas",
        "California",
        "Georgia",
        "Louisiana",
        "Mississippi",
        "Missouri",
        "North Carolina",
        "Tennessee",
        "Texas",
        "Other States",
        "United States",
    ),
    "soybeans": (
        "Arkansas",
        "Illinois",
        "Indiana",
        "Iowa",
        "Kansas",
        "Michigan",
        "Minnesota",
        "Mississippi",
        "Missouri",
        "Nebraska",
        "North Dakota",
        "Ohio",
        "South Dakota",
        "Wisconsin",
        "Other States",
        "United States",
    ),
}

STATE_CANON: dict[str, str] = {
    state.casefold(): state for states in CROP_STATES.values() for state in states
}

STATES_ALL: tuple[str, ...] = tuple(
    sorted({state for states in CROP_STATES.values() for state in states})
)

STATE_SUFFIX = re.compile(r"\s*\d+/\s*$")
FOOTNOTE_MARKER = re.compile(r"^\d+/")

_MISSING = object()
_TOKEN_VALUES: dict[str, float | None] = {".": None, "*": 0.0}


def crop_options() -> list[dict]:
    """Build the labeled crop options for the widget's crop selector.

    Returns
    -------
    list[dict]
        Label/value option dictionaries, one per crop.
    """
    return [{"label": config["label"], "value": key} for key, config in CROPS.items()]


def state_options(crop: str) -> list[dict]:
    """Build the labeled state options a crop is published for.

    Parameters
    ----------
    crop : str
        Crop key from CROPS. Unknown crops fall back to corn.

    Returns
    -------
    list[dict]
        Label/value option dictionaries for the widget's state selector.
    """
    states = CROP_STATES.get(crop) or CROP_STATES[DEFAULT_CROP]
    return [{"label": state, "value": state} for state in states]


def _match_trait(label: str) -> str | None:
    """Return the short trait name when a block-title label opens a trait block."""
    low = label.casefold()
    for prefix, short in TRAIT_PREFIXES:
        if low.startswith(prefix):
            return short
    return None


def _is_footnote(label: str) -> bool:
    """Return whether a first-column label is a footnote or source line."""
    low = label.casefold()
    return (
        label.startswith("*")
        or low.startswith("note:")
        or low.startswith("source:")
        or bool(FOOTNOTE_MARKER.match(label))
    )


def _clean_state(label: str) -> str:
    """Strip a state row's footnote suffix, e.g. 'North Dakota 2/' to 'North Dakota'."""
    return STATE_SUFFIX.sub("", label).strip()


def _year_columns(cells: list) -> list[tuple[int, int]]:
    """Return the (column index, year) pairs from a 'State/Year' header row."""
    columns: list[tuple[int, int]] = []
    for index, cell in enumerate(cells):
        if index == 0:
            continue
        text = str(cell).strip() if cell is not None else ""
        if len(text) == 4 and text.isdigit():
            columns.append((index, int(text)))
    return columns


def _coerce_value(cell) -> object:
    """Coerce a source cell to a percent float, None for '.', or the skip sentinel.

    Parameters
    ----------
    cell : object
        Raw worksheet cell value.

    Returns
    -------
    object
        A float percent; None for the '.' not-available token; 0.0 for the '*'
        rounds-to-less-than-half token; or the module skip sentinel for blank
        or non-numeric cells.
    """
    if cell is None or isinstance(cell, bool):
        return _MISSING
    if isinstance(cell, (int, float)):
        return float(cell)
    text = str(cell).strip()
    if not text:
        return _MISSING
    if text in _TOKEN_VALUES:
        return _TOKEN_VALUES[text]
    try:
        return float(text)
    except ValueError:
        return _MISSING


def parse_sheet(rows: list, crop: str) -> list[dict]:
    """Parse one crop sheet's stacked trait blocks into long-format records.

    Parameters
    ----------
    rows : list
        The worksheet's value rows, each an ordered sequence of cell values.
    crop : str
        Crop key from CROPS, selecting the trait vocabulary.

    Returns
    -------
    list[dict]
        Records carrying crop, state, trait short name, integer year, and the
        percent value, where '.' yields None and '*' yields 0.0. Rows outside a
        trait block, header rows, and footnote rows are skipped.
    """
    valid_traits = set(CROPS[crop]["traits"])
    records: list[dict] = []
    trait: str | None = None
    year_columns: list[tuple[int, int]] = []
    for raw in rows:
        cells = list(raw)
        first = cells[0] if cells else None
        label = str(first).strip() if first is not None else ""
        if not label:
            continue
        matched = _match_trait(label)
        if matched is not None:
            trait = matched if matched in valid_traits else None
            year_columns = []
            continue
        if label.casefold().startswith("state/year"):
            year_columns = _year_columns(cells)
            continue
        if _is_footnote(label):
            continue
        if trait is None or not year_columns:
            continue
        state = _clean_state(label)
        for index, year in year_columns:
            cell = cells[index] if index < len(cells) else None
            value = _coerce_value(cell)
            if value is _MISSING:
                continue
            records.append(
                {
                    "crop": crop,
                    "state": state,
                    "trait": trait,
                    "year": year,
                    "value": value,
                }
            )
    return records


async def afetch_crop(crop: str) -> list[dict]:
    """Download the workbook and parse one crop's sheet through the ERS cache.

    Parameters
    ----------
    crop : str
        Crop key from CROPS.

    Returns
    -------
    list[dict]
        Long-format records from parse_sheet for the selected crop.
    """
    import openpyxl

    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(MEDIA_PATH, product=PRODUCT_PAGE)
    workbook = openpyxl.load_workbook(BytesIO(content), read_only=True, data_only=True)
    try:
        rows = list(workbook[CROPS[crop]["sheet"]].iter_rows(values_only=True))
    finally:
        workbook.close()
    return parse_sheet(rows, crop)
