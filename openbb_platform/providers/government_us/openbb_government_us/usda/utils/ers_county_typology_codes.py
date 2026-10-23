"""USDA ERS County Typology Codes file catalog and per-vintage parsers."""

import csv
import math
from io import BytesIO, StringIO
from typing import Any

PRODUCT_PAGE = "data-products/county-typology-codes"
DEFAULT_VINTAGE = "2025"

VINTAGES: dict[str, dict] = {
    "2025": {
        "label": "2025 Edition",
        "media_path": "/media/6174/ers-county-typology-codes-2025-edition.csv",
        "format": "long_2025",
    },
    "2015": {
        "label": "2015 Edition",
        "media_path": "/media/6176/ers-county-typology-codes-2015-edition.csv",
        "format": "wide_2015",
    },
    "2004": {
        "label": "2004 Edition",
        "media_path": "/media/6177/2004-county-typology-codes.xls",
        "format": "wide_2004",
        "sheet": "all_final_codes",
    },
    "1989": {
        "label": "1989 Edition",
        "media_path": "/media/6178/1989-county-typology-codes.xls",
        "format": "wide_1989",
        "sheet": "Data",
    },
    "1979_1986_1983def": {
        "label": "1979 and 1986 (1983 nonmetro definition)",
        "media_path": "/media/6179/1979-and-1986-county-typology-codes-uses-the"
        + "-1983-nonmetro-definition.xls",
        "format": "wide_1979",
        "sheet": "Data",
        "rucc_col": "RURALURB83",
    },
    "1979_1986_1974def": {
        "label": "1979 and 1986 (1974 nonmetro definition)",
        "media_path": "/media/6180/1979-and-1986-county-typology-codes-uses-the"
        + "-1974-nonmetro-definition.xls",
        "format": "wide_1979",
        "sheet": "Data",
        "rucc_col": "RURALURB74",
    },
}

STATE_FIPS_ABBR: dict[str, str] = {
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
}

STATE_ABBRS: frozenset[str] = frozenset(STATE_NAMES)

ECON_2025: dict[int, str] = {
    0: "Nonspecialized",
    1: "Farming",
    2: "Mining",
    3: "Manufacturing",
    4: "Government",
    5: "Recreation",
}

ECON_2015: dict[int, str] = {
    0: "Nonspecialized",
    1: "Farming",
    2: "Mining",
    3: "Manufacturing",
    4: "Federal/State Government",
    5: "Recreation",
}

ECON_2004: dict[int, str] = {
    1: "Farming",
    2: "Mining",
    3: "Manufacturing",
    4: "Federal/State Government",
    5: "Services",
    6: "Nonspecialized",
}

ECON_FLAGS_1989: tuple[tuple[str, str], ...] = (
    ("FM", "Farming"),
    ("MI", "Mining"),
    ("MF", "Manufacturing"),
    ("GV", "Government"),
    ("TS", "Services"),
    ("NS", "Nonspecialized"),
)

ECON_FLAGS_1979: tuple[tuple[str, str], ...] = (
    ("AGTP79R", "Farming"),
    ("MINTP79R", "Mining"),
    ("MFGTP79R", "Manufacturing"),
    ("GVTTP79R", "Government"),
    ("UNCL79", "Nonspecialized"),
)

CANONICAL_FIELDS: tuple[str, ...] = (
    "fips",
    "state",
    "county_name",
    "metro",
    "economic_type",
    "economic_type_code",
    "economic_type_label",
    "farming",
    "mining",
    "manufacturing",
    "government",
    "recreation",
    "services",
    "nonspecialized",
    "low_education",
    "low_employment",
    "population_loss",
    "housing_stress",
    "retirement_destination",
    "persistent_poverty",
    "persistent_child_poverty",
    "federal_lands",
    "commuting",
    "transfers_dependent",
    "rural_urban_continuum_code",
    "urban_influence_code",
    "farming_1986",
    "mining_1986",
    "manufacturing_1986",
    "government_1986",
    "nonspecialized_1986",
)


def state_options() -> list[dict]:
    """Return the 51-entry state filter options (50 states plus DC)."""
    return [{"label": name, "value": abbr} for abbr, name in STATE_NAMES.items()]


def vintage_options() -> list[dict]:
    """Return the vintage select options, newest edition first."""
    return [
        {"label": config["label"], "value": key} for key, config in VINTAGES.items()
    ]


def cell_int(value: Any) -> int | None:
    """Coerce a source cell to an integer code, preserving sentinel values.

    Parameters
    ----------
    value : Any
        A raw CSV string or Excel cell value.

    Returns
    -------
    int | None
        The integer value, keeping documented sentinels such as 8, 9, 99, and
        -1 unchanged; None for blanks and placeholder tokens.
    """
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
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
    if isinstance(value, float) and math.isnan(value):
        return None
    text = str(value).strip()
    return text or None


def normalize_fips(value: Any) -> str | None:
    """Normalize a county FIPS to a five-digit zero-padded string."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return str(int(float(text))).zfill(5)
    except ValueError:
        return text.zfill(5)


def state_of(fips: str) -> str | None:
    """Return the postal abbreviation for a county FIPS's state prefix."""
    return STATE_FIPS_ABBR.get(fips[:2])


def _blank_record() -> dict:
    """Return a canonical record with every field defaulted to None."""
    return {field: None for field in CANONICAL_FIELDS}


def _flag_economic_type(row: dict, flags: tuple[tuple[str, str], ...]) -> str | None:
    """Derive an economic-type label from a flag-based vintage's set flags."""
    labels = [label for column, label in flags if cell_int(row.get(column)) == 1]
    return " / ".join(labels) if labels else None


def parse_2025(text: str) -> list[dict]:
    """Parse the 2025 long CSV into one canonical record per county.

    Parameters
    ----------
    text : str
        Decoded text of the 2025-edition long CSV.

    Returns
    -------
    list[dict]
        Canonical records keyed by CANONICAL_FIELDS, in source county order.
    """
    county_name: dict[str, str | None] = {}
    metro: dict[str, int | None] = {}
    attrs_by_fips: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for row in csv.DictReader(StringIO(text)):
        fips = normalize_fips(row.get("FIPStxt"))
        if fips is None:
            continue
        attrs = attrs_by_fips.get(fips)
        if attrs is None:
            attrs = {}
            attrs_by_fips[fips] = attrs
            county_name[fips] = cell_str(row.get("County_Name"))
            metro[fips] = cell_int(row.get("Metro2023"))
            order.append(fips)
        attrs[(row.get("Attribute") or "").strip()] = row.get("Value")
    records: list[dict] = []
    for fips in order:
        attrs = attrs_by_fips[fips]
        code = cell_int(attrs.get("Industry_Dependence_2025"))
        record = _blank_record()
        record.update(
            fips=fips,
            state=state_of(fips),
            county_name=county_name[fips],
            metro=metro[fips],
            economic_type=ECON_2025.get(code) if code is not None else None,
            economic_type_code=code,
            farming=cell_int(attrs.get("High_Farming_2025")),
            mining=cell_int(attrs.get("High_Mining_2025")),
            manufacturing=cell_int(attrs.get("High_Manufacturing_2025")),
            government=cell_int(attrs.get("High_Government_2025")),
            recreation=cell_int(attrs.get("High_Recreation_2025")),
            nonspecialized=cell_int(attrs.get("Nonspecialized_2025")),
            low_education=cell_int(attrs.get("Low_PostSecondary_Ed_2025")),
            low_employment=cell_int(attrs.get("Low_Employment_2025")),
            population_loss=cell_int(attrs.get("Population_Loss_2025")),
            housing_stress=cell_int(attrs.get("Housing_Stress_2025")),
            retirement_destination=cell_int(attrs.get("Retirement_Destination_2025")),
            persistent_poverty=cell_int(attrs.get("Persistent_Poverty_1721")),
        )
        records.append(record)
    return records


def parse_2015(text: str) -> list[dict]:
    """Parse the 2015 wide CSV into one canonical record per county."""
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        fips = normalize_fips(row.get("FIPStxt"))
        if fips is None:
            continue
        code = cell_int(row.get("Economic Types Type_2015_Update non-overlapping"))
        record = _blank_record()
        record.update(
            fips=fips,
            state=state_of(fips),
            county_name=cell_str(row.get("County_name")),
            metro=cell_int(row.get("Metro-nonmetro status, 2013 0=Nonmetro 1=Metro")),
            economic_type=ECON_2015.get(code) if code is not None else None,
            economic_type_code=code,
            economic_type_label=cell_str(row.get("Economic_Type_Label")),
            farming=cell_int(row.get("Farming_2015_Update")),
            mining=cell_int(row.get("Mining_2015-Update")),
            manufacturing=cell_int(row.get("Manufacturing_2015_Update")),
            government=cell_int(row.get("Government_2015_Update")),
            recreation=cell_int(row.get("Recreation_2015_Update")),
            nonspecialized=cell_int(row.get("Nonspecialized_2015_Update")),
            low_education=cell_int(row.get("Low_Education_2015_Update")),
            low_employment=cell_int(row.get("Low_Employment_Cnty_2008_2012_25_64")),
            population_loss=cell_int(row.get("Pop_Loss_2010")),
            retirement_destination=cell_int(row.get("Retirement_Dest_2015_Update")),
            persistent_poverty=cell_int(row.get("Persistent_Poverty_2013")),
            persistent_child_poverty=cell_int(
                row.get("Persistent_Related_Child_Poverty_2013")
            ),
        )
        records.append(record)
    return records


def parse_2004(rows: list[dict]) -> list[dict]:
    """Parse the 2004 workbook rows into one canonical record per county."""
    records: list[dict] = []
    for row in rows:
        fips = normalize_fips(row.get("FIPSTXT"))
        if fips is None:
            continue
        code = cell_int(row.get("econdep"))
        record = _blank_record()
        record.update(
            fips=fips,
            state=state_of(fips),
            county_name=cell_str(row.get("County")),
            metro=cell_int(row.get("metro")),
            economic_type=ECON_2004.get(code) if code is not None else None,
            economic_type_code=code,
            farming=cell_int(row.get("farm")),
            mining=cell_int(row.get("mine")),
            manufacturing=cell_int(row.get("manf")),
            government=cell_int(row.get("fsgov")),
            services=cell_int(row.get("serv")),
            nonspecialized=cell_int(row.get("nonsp")),
            recreation=cell_int(row.get("rec")),
            low_education=cell_int(row.get("loweduc")),
            low_employment=cell_int(row.get("lowemp")),
            population_loss=cell_int(row.get("poploss")),
            housing_stress=cell_int(row.get("house")),
            retirement_destination=cell_int(row.get("retire")),
            persistent_poverty=cell_int(row.get("perpov")),
            persistent_child_poverty=cell_int(row.get("perchldpov")),
            rural_urban_continuum_code=cell_int(row.get("rururb2003")),
            urban_influence_code=cell_int(row.get("urbinf2003")),
        )
        records.append(record)
    return records


def parse_1989(rows: list[dict]) -> list[dict]:
    """Parse the 1989 workbook rows into one canonical record per county."""
    records: list[dict] = []
    for row in rows:
        fips = normalize_fips(row.get("FIPS"))
        if fips is None:
            continue
        rucc = cell_int(row.get("RuralUrb93"))
        record = _blank_record()
        record.update(
            fips=fips,
            state=state_of(fips),
            county_name=cell_str(row.get("County name")),
            metro=(1 if rucc is not None and rucc <= 3 else 0)
            if rucc is not None
            else None,
            economic_type=_flag_economic_type(row, ECON_FLAGS_1989),
            farming=cell_int(row.get("FM")),
            mining=cell_int(row.get("MI")),
            manufacturing=cell_int(row.get("MF")),
            government=cell_int(row.get("GV")),
            services=cell_int(row.get("TS")),
            nonspecialized=cell_int(row.get("NS")),
            retirement_destination=cell_int(row.get("RT")),
            federal_lands=cell_int(row.get("FL")),
            commuting=cell_int(row.get("CM")),
            persistent_poverty=cell_int(row.get("PV")),
            transfers_dependent=cell_int(row.get("TP")),
            rural_urban_continuum_code=rucc,
        )
        records.append(record)
    return records


def parse_1979(rows: list[dict], rucc_col: str) -> list[dict]:
    """Parse a 1979/1986 workbook's rows into one canonical record per county.

    Parameters
    ----------
    rows : list[dict]
        Row dictionaries from the workbook's 'Data' sheet.
    rucc_col : str
        Rural-urban continuum column name for the file's nonmetro definition.

    Returns
    -------
    list[dict]
        Canonical records; the unsuffixed flags carry the 1979 revised
        classification and the ``*_1986`` flags carry the 1986 update.
    """
    records: list[dict] = []
    for row in rows:
        fips = normalize_fips(row.get("FIPS"))
        if fips is None:
            continue
        record = _blank_record()
        record.update(
            fips=fips,
            state=state_of(fips),
            county_name=cell_str(row.get("County")),
            metro=cell_int(row.get("NMET")),
            economic_type=_flag_economic_type(row, ECON_FLAGS_1979),
            farming=cell_int(row.get("AGTP79R")),
            mining=cell_int(row.get("MINTP79R")),
            manufacturing=cell_int(row.get("MFGTP79R")),
            government=cell_int(row.get("GVTTP79R")),
            nonspecialized=cell_int(row.get("UNCL79")),
            federal_lands=cell_int(row.get("FEDTP79")),
            retirement_destination=cell_int(row.get("RETTP79")),
            persistent_poverty=cell_int(row.get("POVTP79")),
            rural_urban_continuum_code=cell_int(row.get(rucc_col)),
            farming_1986=cell_int(row.get("AGTP86")),
            mining_1986=cell_int(row.get("MINTP86")),
            manufacturing_1986=cell_int(row.get("MFGTP86")),
            government_1986=cell_int(row.get("GVTTP86")),
            nonspecialized_1986=cell_int(row.get("UNCL86")),
        )
        records.append(record)
    return records


def _read_sheet(content: bytes, sheet: str) -> list[dict]:
    """Read one Excel sheet into a list of row dictionaries."""
    import pandas as pd

    frame = pd.read_excel(BytesIO(content), sheet_name=sheet, header=0, dtype=object)
    return frame.to_dict("records")


def parse_vintage(vintage: str, content: bytes) -> list[dict]:
    """Parse a vintage's raw file content into canonical county records.

    Parameters
    ----------
    vintage : str
        Vintage key from VINTAGES.
    content : bytes
        Raw downloaded file content.

    Returns
    -------
    list[dict]
        Canonical records keyed by CANONICAL_FIELDS.
    """
    config = VINTAGES[vintage]
    fmt = config["format"]
    if fmt == "long_2025":
        return parse_2025(content.decode("utf-8-sig", errors="replace"))
    if fmt == "wide_2015":
        return parse_2015(content.decode("utf-8-sig", errors="replace"))
    rows = _read_sheet(content, config["sheet"])
    if fmt == "wide_2004":
        return parse_2004(rows)
    if fmt == "wide_1989":
        return parse_1989(rows)
    return parse_1979(rows, config["rucc_col"])


async def afetch_vintage(vintage: str) -> list[dict]:
    """Download and parse one vintage's file through the ERS disk cache.

    Parameters
    ----------
    vintage : str
        Vintage key from VINTAGES.

    Returns
    -------
    list[dict]
        Canonical county records for the vintage.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = VINTAGES[vintage]
    content = await afetch_ers_file(config["media_path"], product=PRODUCT_PAGE)
    return parse_vintage(vintage, content)
