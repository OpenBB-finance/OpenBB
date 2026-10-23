"""USDA ERS Urban Influence Codes catalog, fetch, and per-vintage parsers."""

import csv
import math
from io import BytesIO, StringIO
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError

PRODUCT_PAGE = "data-products/urban-influence-codes"

VINTAGES: tuple[str, ...] = ("2024", "2013", "2003", "1993")

VINTAGE_LABELS: dict[str, str] = {
    "2024": "2024 revision (9-code scheme)",
    "2013": "2013 (12-code scheme)",
    "2003": "2003 (12-code scheme)",
    "1993": "1993 (9-code scheme)",
}

MEDIA_2024_CSV = "/media/6182/2024-urban-influence-codes.csv"
MEDIA_2013_XLS = "/media/6183/2013-urban-influence-codes.xls"
MEDIA_2003_1993_XLS = (
    "/media/6184/2003-and-1993-urban-influence-codes-for-us-counties.xls"
)
MEDIA_2003_PR_XLS = "/media/6185/2003-urban-influence-codes-for-puerto-rico.xls"

SHEET_2013 = "Urban Influence Codes 2013"
SHEET_2003_1993 = "Urban Influence Codes"
SHEET_2003_PR = "pr2003UrbInf"

STATE_LABELS: dict[str, str] = {
    "AK": "Alaska",
    "AL": "Alabama",
    "AR": "Arkansas",
    "AS": "American Samoa",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "District of Columbia",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "GU": "Guam",
    "HI": "Hawaii",
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
    "MP": "Northern Mariana Islands",
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
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VI": "U.S. Virgin Islands",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
}

ALL_TERRITORIES: frozenset[str] = frozenset({"AS", "GU", "MP", "PR", "VI"})

VINTAGE_TERRITORIES: dict[str, tuple[str, ...]] = {
    "2024": ("AS", "GU", "MP", "PR", "VI"),
    "2013": ("PR",),
    "2003": ("PR",),
    "1993": (),
}


def allowed_states(vintage: str) -> tuple[str, ...]:
    """Return the state codes an Urban Influence Codes vintage is published for.

    Parameters
    ----------
    vintage : str
        Vintage key from VINTAGES.

    Returns
    -------
    tuple[str, ...]
        The fifty states and the District of Columbia, plus the territories
        carried by the vintage, in alphabetical-by-code order.
    """
    territories = set(VINTAGE_TERRITORIES.get(vintage, ()))
    return tuple(
        code
        for code in STATE_LABELS
        if code not in ALL_TERRITORIES or code in territories
    )


def state_options(vintage: str) -> list[dict]:
    """Build the labeled state options a vintage is published for.

    Parameters
    ----------
    vintage : str
        Vintage key from VINTAGES.

    Returns
    -------
    list[dict]
        Label/value option dictionaries for the widget's state selector.
    """
    return [
        {"label": STATE_LABELS[code], "value": code} for code in allowed_states(vintage)
    ]


def _fips5(value) -> str:
    """Return a FIPS code as a zero-padded five-character string."""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text.zfill(5)


def _state(value) -> str:
    """Return a two-letter state code stripped of whitespace."""
    return str(value).strip()


def _clean_text(value) -> str | None:
    """Return text with runs of whitespace collapsed, or None when empty."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    text = " ".join(str(value).split())
    return text or None


def _text_int(value) -> int | None:
    """Return a CSV integer string as an int, or None when blank."""
    text = (value or "").strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def _cell_number(value) -> int | float | None:
    """Return a spreadsheet cell as a native number, or None when blank or NaN."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return value.item() if hasattr(value, "item") else value


def _code(value) -> str | None:
    """Return an ordinal classification code as its bare string, or None."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    number = value.item() if hasattr(value, "item") else value
    if isinstance(number, float) and number.is_integer():
        number = int(number)
    return str(number)


def parse_2024_csv(text: str) -> list[dict]:
    """Pivot the long 2024 revision CSV into one record per county FIPS.

    Parameters
    ----------
    text : str
        Decoded CSV text with columns FIPS-UIC, State, County_Name, Attribute,
        and Value, where Attribute is one of Population_2020, UIC_2024, or
        Description.

    Returns
    -------
    list[dict]
        Unified records with fips, state, county_name, urban_influence_code,
        description, population, and population_density keys; population_density
        is None because the 2024 file carries no density.
    """
    grouped: dict[str, dict[str, Any]] = {}
    for row in csv.DictReader(StringIO(text)):
        fips = _fips5(row["FIPS-UIC"])
        entry = grouped.get(fips)
        if entry is None:
            entry: dict[str, Any] = {
                "fips": fips,
                "state": _state(row.get("State")),
                "county_name": _clean_text(row.get("County_Name")),
                "urban_influence_code": None,
                "description": None,
                "population": None,
                "population_density": None,
            }
            grouped[fips] = entry
        attribute = (row.get("Attribute") or "").strip()
        value = row.get("Value")
        if attribute == "UIC_2024":
            entry["urban_influence_code"] = _code(value)
        elif attribute == "Description":
            entry["description"] = _clean_text(value)
        elif attribute == "Population_2020":
            entry["population"] = _text_int(value)
    return list(grouped.values())


def parse_2013_xls(content: bytes) -> list[dict]:
    """Parse the wide 2013 workbook into unified county records.

    Parameters
    ----------
    content : bytes
        Raw legacy .xls bytes of the 2013 Urban Influence Codes workbook.

    Returns
    -------
    list[dict]
        Unified records; population is the 2010 census count and
        population_density is None because the 2013 file carries no density.
    """
    import pandas as pd

    frame = pd.read_excel(BytesIO(content), sheet_name=SHEET_2013, header=0)
    return [
        {
            "fips": _fips5(row["FIPS"]),
            "state": _state(row["State"]),
            "county_name": _clean_text(row["County_Name"]),
            "urban_influence_code": _code(row["UIC_2013"]),
            "description": _clean_text(row["Description"]),
            "population": _cell_number(row["Population_2010"]),
            "population_density": None,
        }
        for row in frame.to_dict("records")
    ]


def parse_2003_combined(content: bytes) -> list[dict]:
    """Parse the 2003 columns of the combined U.S. counties workbook.

    Parameters
    ----------
    content : bytes
        Raw legacy .xls bytes of the combined 2003-and-1993 U.S. counties
        workbook.

    Returns
    -------
    list[dict]
        Unified records using the 2003 code and description columns; population
        and population_density are the 2000 census columns.
    """
    import pandas as pd

    frame = pd.read_excel(BytesIO(content), sheet_name=SHEET_2003_1993, header=0)
    return [
        {
            "fips": _fips5(row["FIPS Code"]),
            "state": _state(row["State"]),
            "county_name": _clean_text(row["County name"]),
            "urban_influence_code": _code(row["2003 Urban Influence Code"]),
            "description": _clean_text(row["2003 Urban Influence Code description"]),
            "population": _cell_number(row["2000 Population"]),
            "population_density": _cell_number(row["2000 Persons per square mile"]),
        }
        for row in frame.to_dict("records")
    ]


def parse_2003_pr(content: bytes) -> list[dict]:
    """Parse the 2003 Puerto Rico municipios workbook into unified records.

    Parameters
    ----------
    content : bytes
        Raw legacy .xls bytes of the 2003 Puerto Rico workbook.

    Returns
    -------
    list[dict]
        Unified records for the 78 municipios; population_density is None
        because the Puerto Rico file carries no density.
    """
    import pandas as pd

    frame = pd.read_excel(BytesIO(content), sheet_name=SHEET_2003_PR, header=0)
    return [
        {
            "fips": _fips5(row["FIPS Code"]),
            "state": _state(row["State"]),
            "county_name": _clean_text(row["Municipio Name"]),
            "urban_influence_code": _code(row["Urban Influence  Code, 2003"]),
            "description": _clean_text(row["Description of the 2003 Code"]),
            "population": _cell_number(row["Population 2003 "]),
            "population_density": None,
        }
        for row in frame.to_dict("records")
    ]


def parse_1993_combined(content: bytes) -> list[dict]:
    """Parse the 1993 columns of the combined U.S. counties workbook.

    Parameters
    ----------
    content : bytes
        Raw legacy .xls bytes of the combined 2003-and-1993 U.S. counties
        workbook.

    Returns
    -------
    list[dict]
        Unified records using the 1993 code and description columns; the
        population and population_density carried by the file are the 2000
        census columns, as no 1993-vintage population is published.
    """
    import pandas as pd

    frame = pd.read_excel(BytesIO(content), sheet_name=SHEET_2003_1993, header=0)
    return [
        {
            "fips": _fips5(row["FIPS Code"]),
            "state": _state(row["State"]),
            "county_name": _clean_text(row["County name"]),
            "urban_influence_code": _code(row["1993 Urban Influence Code"]),
            "description": _clean_text(row["1993 Urban Influence Code description"]),
            "population": _cell_number(row["2000 Population"]),
            "population_density": _cell_number(row["2000 Persons per square mile"]),
        }
        for row in frame.to_dict("records")
    ]


async def afetch_vintage(vintage: str) -> list[dict]:
    """Download and parse an Urban Influence Codes vintage through the cache.

    Parameters
    ----------
    vintage : str
        Vintage key from VINTAGES.

    Returns
    -------
    list[dict]
        Unified county records for the vintage; the 2003 vintage appends the
        Puerto Rico municipios to the U.S. counties file.

    Raises
    ------
    OpenBBError
        If the vintage is not one of the published vintages.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    if vintage == "2024":
        content = await afetch_ers_file(MEDIA_2024_CSV, product=PRODUCT_PAGE)
        return parse_2024_csv(content.decode("utf-8-sig", errors="replace"))
    if vintage == "2013":
        content = await afetch_ers_file(MEDIA_2013_XLS, product=PRODUCT_PAGE)
        return parse_2013_xls(content)
    if vintage == "2003":
        us = await afetch_ers_file(MEDIA_2003_1993_XLS, product=PRODUCT_PAGE)
        pr = await afetch_ers_file(MEDIA_2003_PR_XLS, product=PRODUCT_PAGE)
        return parse_2003_combined(us) + parse_2003_pr(pr)
    if vintage == "1993":
        us = await afetch_ers_file(MEDIA_2003_1993_XLS, product=PRODUCT_PAGE)
        return parse_1993_combined(us)
    raise OpenBBError(
        f"Invalid vintage: {vintage}. Valid vintages are: " + ", ".join(VINTAGES)
    )
