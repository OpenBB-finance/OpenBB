"""USDA ERS Area and Road Ruggedness Scales vintage catalog and census-tract lookup parsers."""

import csv
from collections import OrderedDict
from io import StringIO

from openbb_government_us.usda.utils.ers_rural_urban_continuum_codes import STATE_NAMES

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/area-and-road-ruggedness-scales"

DEFAULT_VINTAGE = "2020"
DEFAULT_STATE = "WV"

STATE_NAMES_BY_NAME: dict[str, str] = {name: code for code, name in STATE_NAMES.items()}

STATES: tuple[str, ...] = (
    "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI",
    "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN",
    "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH",
    "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA",
    "WI", "WV", "WY",
)  # fmt: skip

ALL_STATES: frozenset[str] = frozenset(STATES)

STATES_BY_VINTAGE: dict[str, tuple[str, ...]] = {"2020": STATES, "2010": STATES}

CANONICAL_COLUMNS: tuple[str, ...] = (
    "tract_fips",
    "tract_name",
    "county_fips",
    "county_name",
    "state_fips",
    "state",
    "state_name",
    "rs_region",
    "rs_region_name",
    "primary_ruca",
    "rurality_code",
    "rurality_name",
    "population",
    "land_area",
    "pop_density",
    "area_tri_count",
    "area_tri_mean",
    "area_tri_std_dev",
    "area_tri_median",
    "area_tri_min",
    "area_tri_max",
    "area_tri_range",
    "ars",
    "ars_description",
    "road_tri_count",
    "road_tri_mean",
    "road_tri_std_dev",
    "road_tri_median",
    "road_tri_min",
    "road_tri_max",
    "road_tri_range",
    "rrs",
    "rrs_description",
)

STR_COLUMNS: dict[str, str] = {
    "rs_region": "RSRegion",
    "rs_region_name": "RSRegionName",
    "primary_ruca": "PrimaryRUCA",
    "rurality_code": "RuralityCode",
    "ars": "ARS",
    "rrs": "RRS",
}

CAPITALIZED_COLUMNS: dict[str, str] = {
    "rurality_name": "RuralityName",
    "ars_description": "ARSDescription",
    "rrs_description": "RRSDescription",
}

INT_COLUMNS: dict[str, str] = {
    "population": "Population",
    "area_tri_count": "AreaTRI_Count",
    "road_tri_count": "RoadTRI_Count",
}

FLOAT_COLUMNS: dict[str, str] = {
    "land_area": "LandArea",
    "pop_density": "PopDensity",
    "area_tri_mean": "AreaTRI_Mean",
    "area_tri_std_dev": "AreaTRI_StdDev",
    "area_tri_median": "AreaTRI_Median",
    "area_tri_min": "AreaTRI_Min",
    "area_tri_max": "AreaTRI_Max",
    "area_tri_range": "AreaTRI_Range",
    "road_tri_mean": "RoadTRI_Mean",
    "road_tri_std_dev": "RoadTRI_StdDev",
    "road_tri_median": "RoadTRI_Median",
    "road_tri_min": "RoadTRI_Min",
    "road_tri_max": "RoadTRI_Max",
    "road_tri_range": "RoadTRI_Range",
}

VINTAGE_CATALOG: "OrderedDict[str, dict]" = OrderedDict(
    [
        (
            "2020",
            {
                "label": "2020",
                "media": "/media/5414/2020-area-and-road-ruggedness-scales.csv",
                "identifiers": {
                    "tract_fips": "TractFIPS20",
                    "tract_name": "TractName20",
                    "county_fips": "CountyFIPS20",
                    "county_name": "CountyName20",
                    "state_fips": "StateFIPS20",
                },
                "state_column": "StateName20",
                "state_kind": "name",
            },
        ),
        (
            "2010",
            {
                "label": "2010",
                "media": "/media/5412/area-and-road-ruggedness-scales.csv",
                "identifiers": {
                    "tract_fips": "TractFIPS",
                    "tract_name": "TractName",
                    "county_fips": "CountyFIPS",
                    "county_name": "CountyName",
                    "state_fips": "StateFIPS",
                },
                "state_column": "State",
                "state_kind": "postal",
            },
        ),
    ]
)

VINTAGES = tuple(VINTAGE_CATALOG)

VINTAGE_OPTIONS = [
    {"label": config["label"], "value": key} for key, config in VINTAGE_CATALOG.items()
]


def clean_text(value: object) -> str | None:
    """Strip a source cell to a non-empty string, or None when blank.

    Parameters
    ----------
    value : object
        A raw source cell, which may be None, a missing marker rendered as
        'nan', or a string carrying stray leading or trailing whitespace.

    Returns
    -------
    str | None
        The stripped text, or None when the cell is empty or a missing marker.
    """
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.casefold() == "nan":
        return None
    return text


def capitalize_text(value: object) -> str | None:
    """Sentence-case a source label so the two vintages share one casing.

    Parameters
    ----------
    value : object
        A raw label cell whose casing differs between vintages, lowercase in
        the 2010 edition and title case in the 2020 edition.

    Returns
    -------
    str | None
        The label capitalized to a single leading uppercase, or None when the
        cell is blank.
    """
    text = clean_text(value)
    return text.capitalize() if text else None


def parse_population(value: object) -> int | None:
    """Parse an integer count cell, or None when unavailable.

    Parameters
    ----------
    value : object
        A raw count cell, which may be None, blank, a missing marker, or a
        digit string with optional thousands separators.

    Returns
    -------
    int | None
        The full integer count, or None when the cell is empty or non-numeric.
    """
    if value is None:
        return None
    text = str(value).replace(",", "").strip()
    if not text or text.casefold() in {"nan", "na", "n/a"}:
        return None
    try:
        return int(text)
    except ValueError:
        try:
            return int(float(text))
        except ValueError:
            return None


def parse_float(value: object) -> float | None:
    """Parse a float cell at full precision, or None when unavailable.

    Parameters
    ----------
    value : object
        A raw numeric cell, which may be None, blank, a missing marker, or a
        decimal string.

    Returns
    -------
    float | None
        The full-precision float, or None when the cell is empty or
        non-numeric.
    """
    if value is None:
        return None
    text = str(value).replace(",", "").strip()
    if not text or text.casefold() in {"nan", "na", "n/a"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_csv_records(text: str, vintage: str) -> list[dict]:
    """Normalize a vintage's wide census-tract CSV into canonical records.

    Parameters
    ----------
    text : str
        Decoded CSV text, one row per census tract, with the vintage's source
        column headers.
    vintage : str
        A vintage key from VINTAGES, selecting the identifier column map and
        the state column and its kind.

    Returns
    -------
    list[dict]
        One canonical record per census tract, each carrying the fixed
        CANONICAL_COLUMNS keys. Rows with a blank tract FIPS are skipped.
    """
    config = VINTAGE_CATALOG[vintage]
    identifiers = config["identifiers"]
    state_column = config["state_column"]
    state_kind = config["state_kind"]
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        tract_fips = clean_text(row.get(identifiers["tract_fips"]))
        if not tract_fips:
            continue
        record: dict = {}
        for canonical, source in identifiers.items():
            record[canonical] = clean_text(row.get(source))
        if state_kind == "name":
            state_name = clean_text(row.get(state_column))
            record["state"] = (
                STATE_NAMES_BY_NAME.get(state_name) if state_name else None
            )
            record["state_name"] = state_name
        else:
            state = clean_text(row.get(state_column))
            record["state"] = state
            record["state_name"] = STATE_NAMES.get(state) if state else None
        for canonical, source in STR_COLUMNS.items():
            record[canonical] = clean_text(row.get(source))
        for canonical, source in CAPITALIZED_COLUMNS.items():
            record[canonical] = capitalize_text(row.get(source))
        for canonical, source in INT_COLUMNS.items():
            record[canonical] = parse_population(row.get(source))
        for canonical, source in FLOAT_COLUMNS.items():
            record[canonical] = parse_float(row.get(source))
        records.append(record)
    return records


def vintage_options() -> list[dict]:
    """Build the labeled vintage options for the widget's vintage selector.

    Returns
    -------
    list[dict]
        Label/value option dictionaries, one per published vintage.
    """
    return list(VINTAGE_OPTIONS)


def state_options(vintage: str) -> list[dict]:
    """Build the labeled state options a vintage publishes.

    Parameters
    ----------
    vintage : str
        Vintage key. Unknown vintages fall back to the default vintage.

    Returns
    -------
    list[dict]
        Label/value option dictionaries for the widget's state selector, the
        label the full state or district name.
    """
    states = STATES_BY_VINTAGE.get(vintage) or STATES_BY_VINTAGE[DEFAULT_VINTAGE]
    return [{"label": STATE_NAMES.get(code, code), "value": code} for code in states]


async def afetch_vintage(vintage: str) -> list[dict]:
    """Download and parse one vintage into canonical records through the cache.

    Parameters
    ----------
    vintage : str
        A vintage key from VINTAGES.

    Returns
    -------
    list[dict]
        Canonical census-tract records for the vintage.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = VINTAGE_CATALOG[vintage]
    content = await afetch_ers_file(config["media"], product=PRODUCT_PAGE)
    return parse_csv_records(content.decode("utf-8-sig", errors="replace"), vintage)
