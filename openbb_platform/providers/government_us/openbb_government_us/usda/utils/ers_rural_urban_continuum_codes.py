"""USDA ERS Rural-Urban Continuum Codes vintage catalog and county-lookup parsers."""

import csv
from collections import OrderedDict
from io import BytesIO, StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/rural-urban-continuum-codes"

DEFAULT_VINTAGE = "2023"

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
    "PR": "Puerto Rico",
    "AS": "American Samoa",
    "GU": "Guam",
    "MP": "Northern Mariana Islands",
    "VI": "U.S. Virgin Islands",
}

VINTAGE_CATALOG: "OrderedDict[str, dict]" = OrderedDict(
    [
        (
            "2023",
            {
                "label": "2023",
                "format": "csv",
                "media": "/media/5768/2023-rural-urban-continuum-codes.csv",
                "code_attr": "RUCC_2023",
                "description_attr": "Description",
                "population_attr": "Population_2020",
            },
        ),
        (
            "2013",
            {
                "label": "2013",
                "format": "xls",
                "parts": [
                    {
                        "media": "/media/5769/2013-rural-urban-continuum-codes.xls",
                        "sheet": "Rural-urban Continuum Code 2013",
                        "fips": "FIPS",
                        "state": "State",
                        "name": "County_Name",
                        "code": "RUCC_2013",
                        "description": "Description",
                        "population": "Population_2010",
                    }
                ],
            },
        ),
        (
            "2003",
            {
                "label": "2003",
                "format": "xls",
                "parts": [
                    {
                        "media": "/media/5770/2003-rural-urban-continuum-codes.xls",
                        "sheet": "beale03",
                        "fips": "FIPS Code",
                        "state": "State",
                        "name": "County Name",
                        "code": "2003 Rural-urban Continuum Code",
                        "description": "Description for 2003 codes",
                        "population": "2000 Population",
                    },
                    {
                        "media": "/media/5771/2003-rural-urban-continuum-codes"
                        "-codes-for-puerto-rico.xls",
                        "sheet": "pr2003",
                        "fips": "FIPS Code",
                        "state": "State",
                        "name": "Municipio Name",
                        "code": "Rural-urban Continuum Code, 2003",
                        "description": "Description of the 2003 Code",
                        "population": "Population 2003",
                    },
                ],
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
        A raw source cell, which may be None, a pandas missing marker rendered
        as 'nan', or a string carrying stray leading or trailing whitespace.

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


def parse_population(value: object) -> int | None:
    """Parse a population cell into an integer count, or None when unavailable.

    Parameters
    ----------
    value : object
        A raw population cell, which may be None, blank, a missing marker, or a
        digit string with optional thousands separators.

    Returns
    -------
    int | None
        The full integer population, or None when the cell is empty or
        non-numeric.
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


def parse_csv_records(text: str, config: dict, vintage: str) -> list[dict]:
    """Pivot the 2023 melted CSV into one county-lookup record per FIPS.

    Parameters
    ----------
    text : str
        Decoded CSV text with columns FIPS, State, County_Name, Attribute,
        Value, one row per county and attribute.
    config : dict
        The vintage config, naming the code, description, and population
        attribute tokens.
    vintage : str
        The vintage key carried onto each record.

    Returns
    -------
    list[dict]
        One record per FIPS in first-seen order, with vintage, fips, state,
        county_name, rucc_code, description, and population keys.
    """
    code_attr = config["code_attr"]
    description_attr = config["description_attr"]
    population_attr = config["population_attr"]
    rows: OrderedDict[str, dict] = OrderedDict()
    for row in csv.DictReader(StringIO(text)):
        fips = (row.get("FIPS") or "").strip()
        if not fips:
            continue
        entry = rows.get(fips)
        if entry is None:
            entry = {
                "vintage": vintage,
                "fips": fips,
                "state": clean_text(row.get("State")),
                "county_name": clean_text(row.get("County_Name")),
                "rucc_code": None,
                "description": None,
                "population": None,
            }
            rows[fips] = entry
        attribute = (row.get("Attribute") or "").strip()
        value = (row.get("Value") or "").strip()
        if attribute == code_attr:
            entry["rucc_code"] = value or None
        elif attribute == description_attr:
            entry["description"] = value or None
        elif attribute == population_attr:
            entry["population"] = parse_population(value)
    return list(rows.values())


def parse_xls_records(content: bytes, part: dict, vintage: str) -> list[dict]:
    """Parse one vintage workbook sheet into county-lookup records.

    Parameters
    ----------
    content : bytes
        Raw legacy .xls bytes of the vintage file.
    part : dict
        The part config, naming the sheet and the source columns for fips,
        state, name, code, description, and population.
    vintage : str
        The vintage key carried onto each record.

    Returns
    -------
    list[dict]
        One record per county row, with vintage, fips, state, county_name,
        rucc_code, description, and population keys. Description and population
        are None on the code-only vintages that omit those columns.
    """
    import pandas as pd

    frame = pd.read_excel(
        BytesIO(content), sheet_name=part["sheet"], engine="xlrd", dtype=str
    )
    frame.columns = [str(column).strip() for column in frame.columns]
    description_column = part["description"]
    population_column = part["population"]
    records: list[dict] = []
    for raw in frame.to_dict("records"):
        fips = clean_text(raw.get(part["fips"]))
        if not fips:
            continue
        records.append(
            {
                "vintage": vintage,
                "fips": fips,
                "state": clean_text(raw.get(part["state"])),
                "county_name": clean_text(raw.get(part["name"])),
                "rucc_code": clean_text(raw.get(part["code"])),
                "description": (
                    clean_text(raw.get(description_column))
                    if description_column
                    else None
                ),
                "population": (
                    parse_population(raw.get(population_column))
                    if population_column
                    else None
                ),
            }
        )
    return records


async def afetch_vintage(vintage: str) -> list[dict]:
    """Download and parse one vintage into county-lookup records through the cache.

    Parameters
    ----------
    vintage : str
        A vintage key from VINTAGES.

    Returns
    -------
    list[dict]
        County-lookup records for the vintage; the 2003 vintage merges the
        mainland file with the separate Puerto Rico file.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = VINTAGE_CATALOG[vintage]
    if config["format"] == "csv":
        content = await afetch_ers_file(config["media"], product=PRODUCT_PAGE)
        return parse_csv_records(
            content.decode("utf-8-sig", errors="replace"), config, vintage
        )
    records: list[dict] = []
    for part in config["parts"]:
        content = await afetch_ers_file(part["media"], product=PRODUCT_PAGE)
        records.extend(parse_xls_records(content, part, vintage))
    return records


async def afetch_states(vintage: str) -> list[dict]:
    """List a vintage's states as label/value options in sorted code order.

    Parameters
    ----------
    vintage : str
        A vintage key from VINTAGES.

    Returns
    -------
    list[dict]
        One option per distinct state code present in the vintage, its label
        the full state or territory name.
    """
    records = await afetch_vintage(vintage)
    codes = sorted({record["state"] for record in records if record["state"]})
    return [{"label": STATE_NAMES.get(code, code), "value": code} for code in codes]
