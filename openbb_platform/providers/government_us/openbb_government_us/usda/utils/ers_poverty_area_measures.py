"""USDA ERS Poverty Area Measures edition catalog and county/tract-lookup parsers."""

import csv
from collections import OrderedDict
from io import StringIO
from typing import Any

PRODUCT_PAGE = "data-products/poverty-area-measures"
DEFAULT_EDITION = "2025"

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
}

STATE_ABBRS: frozenset[str] = frozenset(STATE_NAMES)

EDITION_CATALOG: "OrderedDict[str, dict]" = OrderedDict(
    [
        (
            "2025",
            {
                "label": "September 2025",
                "media": "/media/5041/poverty-area-measures-september-2025-edition.csv",
                "flag_sep": "",
                "metro_col": "MetNonmet2023",
                "beale_col": "Beale2023",
                "ruca_col": "Ruca2020",
                "subreg_col": "Subreg3",
                "tract_fips_col": "TractFIPS23",
                "geography_note": "2023 census-tract geography; Beale 2023,"
                " RUCA 2020, and the 2023 metro definition.",
            },
        ),
        (
            "2023",
            {
                "label": "December 2023",
                "media": "/media/5043/poverty-area-measures-december-2023-edition.csv",
                "flag_sep": "_",
                "metro_col": "MetNonmet2023",
                "beale_col": "Beale2013",
                "ruca_col": "RUCA_2010",
                "subreg_col": "subreg3",
                "tract_fips_col": None,
                "geography_note": "2010 census-tract geography; Beale 2013,"
                " RUCA 2010, and the 2023 metro definition.",
            },
        ),
        (
            "2022",
            {
                "label": "November 2022",
                "media": "/media/5045/poverty-area-measures-november-2022-edition.csv",
                "flag_sep": "_",
                "metro_col": "MetNonmet2013",
                "beale_col": "Beale2013",
                "ruca_col": "RUCA_2010",
                "subreg_col": "subreg3",
                "tract_fips_col": None,
                "geography_note": "2010 census-tract geography; Beale 2013,"
                " RUCA 2010, and the 2013 metro definition.",
            },
        ),
    ]
)

EDITIONS = tuple(EDITION_CATALOG)

EDITION_OPTIONS = [
    {"label": config["label"], "value": key} for key, config in EDITION_CATALOG.items()
]

LEVELS = ("county", "tract")

LEVEL_OPTIONS = [
    {"label": "County", "value": "county"},
    {"label": "Census Tract", "value": "tract"},
]

MEASURE_PREFIX: dict[str, str] = {
    "high_poverty": "HiPov",
    "extreme_poverty": "ExtPov",
    "persistent_poverty": "PerPov",
    "enduring_poverty": "EndurePov",
}

PERIOD_TOKEN: dict[str, str] = {
    "1960": "60",
    "1970": "70",
    "1980": "80",
    "1990": "90",
    "2000": "00",
    "2007_11": "0711",
    "2015_19": "1519",
    "2017_21": "1721",
    "2018_22": "1822",
    "2019_23": "1923",
}

FLAG_FIELDS: "OrderedDict[str, tuple[str, ...]]" = OrderedDict(
    [
        (
            "high_poverty",
            (
                "1960",
                "1970",
                "1980",
                "1990",
                "2000",
                "2007_11",
                "2015_19",
                "2017_21",
                "2018_22",
                "2019_23",
            ),
        ),
        (
            "extreme_poverty",
            (
                "1960",
                "1970",
                "1980",
                "1990",
                "2000",
                "2007_11",
                "2015_19",
                "2017_21",
                "2018_22",
                "2019_23",
            ),
        ),
        (
            "persistent_poverty",
            ("1990", "2000", "2007_11", "2015_19", "2017_21"),
        ),
        (
            "enduring_poverty",
            ("2007_11", "2015_19", "2017_21"),
        ),
    ]
)


def edition_options() -> list[dict]:
    """Return the edition select options, newest edition first."""
    return list(EDITION_OPTIONS)


def state_options() -> list[dict]:
    """Return the 51-entry state filter options (50 states plus DC)."""
    return [{"label": name, "value": abbr} for abbr, name in STATE_NAMES.items()]


def cell_int(value: Any) -> int | None:
    """Coerce a source cell to an integer flag, preserving sentinel values.

    Parameters
    ----------
    value : Any
        A raw CSV string cell.

    Returns
    -------
    int | None
        The integer value, keeping the documented -1 not-available sentinel and
        the 0-3 enduring-poverty categories unchanged; None for blanks and
        placeholder tokens.
    """
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.casefold() in {"na", "n/a", "--", "-"}:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def cell_str(value: Any) -> str | None:
    """Strip a source cell to a non-empty string, or None."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def normalize_fips(value: Any) -> str | None:
    """Normalize a county FIPS to a five-digit zero-padded string."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return str(int(float(text))).zfill(5)
    except ValueError:
        return text.zfill(5)


def normalize_tract_fips(value: Any) -> str | None:
    """Normalize an eleven-digit census-tract GEOID to a zero-padded string."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return str(int(float(text))).zfill(11)
    except ValueError:
        return text.zfill(11)


def flag_column(measure: str, period: str, sep: str, letter: str) -> str:
    """Build the source flag column name for a measure, period, and level letter.

    Parameters
    ----------
    measure : str
        A canonical measure key from MEASURE_PREFIX.
    period : str
        A canonical period key from PERIOD_TOKEN.
    sep : str
        The edition's flag separator: '' for the 2025 edition, '_' otherwise.
    letter : str
        'c' for county-level flags, 't' for tract-level flags.

    Returns
    -------
    str
        The source column name, e.g. 'HiPov0711c' or 'HiPov0711_t'.
    """
    return f"{MEASURE_PREFIX[measure]}{PERIOD_TOKEN[period]}{sep}{letter}"


def tract_fips_of(config: dict, lower: dict, county_fips: str) -> str | None:
    """Resolve an eleven-digit tract FIPS from the edition's tract columns.

    Parameters
    ----------
    config : dict
        The edition config, naming the tract-FIPS source column when present.
    lower : dict
        The source row keyed by lower-cased column name.
    county_fips : str
        The row's five-digit county FIPS, used to derive the tract FIPS on
        editions that publish only the tract number.

    Returns
    -------
    str | None
        The eleven-digit tract FIPS, or None when the tract number is blank.
    """
    column = config["tract_fips_col"]
    if column:
        return normalize_tract_fips(lower.get(column.lower()))
    tract = lower.get("tract")
    if tract is None or not str(tract).strip():
        return None
    return county_fips + str(tract).strip().zfill(6)


def parse_records(text: str, edition: str, level: str) -> list[dict]:
    """Parse the combined county-and-tract CSV into one lookup record per area.

    Parameters
    ----------
    text : str
        Decoded text of the edition's combined CSV.
    edition : str
        An edition key from EDITIONS.
    level : str
        'county' to deduplicate on county FIPS and read the county ('c') flag
        columns, or 'tract' to keep one row per census tract and read the tract
        ('t') flag columns.

    Returns
    -------
    list[dict]
        One record per geographic unit, carrying the identity and geography
        columns plus the fixed union of poverty-area classification flags for
        the requested level.
    """
    config = EDITION_CATALOG[edition]
    sep = config["flag_sep"]
    letter = "c" if level == "county" else "t"
    seen: set[str] = set()
    records: list[dict] = []
    for raw in csv.DictReader(StringIO(text)):
        lower = {(key or "").strip().lower(): value for key, value in raw.items()}
        fips = normalize_fips(lower.get("fips"))
        if fips is None:
            continue
        if level == "county":
            if fips in seen:
                continue
            seen.add(fips)
            tract_fips = None
            tract = None
            tract_name = None
            ruca_code = None
            bna = None
        else:
            tract_fips = tract_fips_of(config, lower, fips)
            tract = cell_str(lower.get("tract"))
            tract_name = cell_str(lower.get("tractname"))
            ruca_code = cell_int(lower.get(config["ruca_col"].lower()))
            bna = cell_int(lower.get("bna01"))
        record: dict[str, Any] = {
            "fips": fips,
            "state": cell_str(lower.get("stusab")),
            "county_name": cell_str(lower.get("countyname")),
            "region": cell_int(lower.get("region")),
            "subregion": cell_int(lower.get(config["subreg_col"].lower())),
            "metro_nonmetro": cell_int(lower.get(config["metro_col"].lower())),
            "rucc_code": cell_int(lower.get(config["beale_col"].lower())),
            "tract_fips": tract_fips,
            "tract": tract,
            "tract_name": tract_name,
            "ruca_code": ruca_code,
            "bna": bna,
        }
        for measure, periods in FLAG_FIELDS.items():
            for period in periods:
                column = flag_column(measure, period, sep, letter).lower()
                record[f"{measure}_{period}"] = cell_int(lower.get(column))
        records.append(record)
    return records


async def afetch_edition(edition: str, level: str) -> list[dict]:
    """Download and parse one edition into lookup records through the disk cache.

    Parameters
    ----------
    edition : str
        An edition key from EDITIONS.
    level : str
        'county' or 'tract'.

    Returns
    -------
    list[dict]
        Lookup records for the edition at the requested geographic level.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = EDITION_CATALOG[edition]
    content = await afetch_ers_file(config["media"], product=PRODUCT_PAGE)
    return parse_records(content.decode("utf-8-sig", errors="replace"), edition, level)


async def afetch_states(edition: str) -> list[dict]:
    """List an edition's states as label/value options in sorted code order.

    Parameters
    ----------
    edition : str
        An edition key from EDITIONS.

    Returns
    -------
    list[dict]
        One option per distinct state code present in the edition, labeled with
        the full state name.
    """
    records = await afetch_edition(edition, "county")
    codes = sorted({record["state"] for record in records if record["state"]})
    return [{"label": STATE_NAMES.get(code, code), "value": code} for code in codes]
