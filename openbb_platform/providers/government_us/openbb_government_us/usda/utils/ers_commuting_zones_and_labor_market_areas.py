"""USDA ERS Commuting Zones and Labor Market Areas vintage catalog and parsers."""

import csv
import io
import math
import zipfile
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/commuting-zones-and-labor-market-areas"

DEFAULT_VINTAGE = "2020"

VINTAGE_FILES: dict[str, dict] = {
    "2020": {
        "media_path": "/media/6968/2020-commuting-zones.csv",
        "format": "csv",
        "label": "2020 Commuting Zones",
    },
    "preliminary_2020": {
        "media_path": "/media/6969/preliminary-2020-commuting-zones.zip",
        "format": "zip_csv",
        "member_prefix": "preliminary-2020-commuting-zones",
        "label": "Preliminary 2020 Commuting Zones",
    },
    "2000": {
        "media_path": "/media/5688/2000-commuting-zones.xls",
        "format": "xls",
        "sheet": "CZ00Equiv",
        "label": "2000 Commuting Zones",
    },
    "1980_1990": {
        "media_path": "/media/5687/1980-and-1990-commuting-zones"
        + "-and-labor-market-areas.xls",
        "format": "xls",
        "sheet": "CZLMA903",
        "label": "1980 and 1990 Commuting Zones and Labor Market Areas",
    },
}

STATE_FIPS: dict[str, str] = {
    "01": "Alabama",
    "02": "Alaska",
    "04": "Arizona",
    "05": "Arkansas",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "11": "District of Columbia",
    "12": "Florida",
    "13": "Georgia",
    "15": "Hawaii",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "19": "Iowa",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "23": "Maine",
    "24": "Maryland",
    "25": "Massachusetts",
    "26": "Michigan",
    "27": "Minnesota",
    "28": "Mississippi",
    "29": "Missouri",
    "30": "Montana",
    "31": "Nebraska",
    "32": "Nevada",
    "33": "New Hampshire",
    "34": "New Jersey",
    "35": "New Mexico",
    "36": "New York",
    "37": "North Carolina",
    "38": "North Dakota",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "44": "Rhode Island",
    "45": "South Carolina",
    "46": "South Dakota",
    "47": "Tennessee",
    "48": "Texas",
    "49": "Utah",
    "50": "Vermont",
    "51": "Virginia",
    "53": "Washington",
    "54": "West Virginia",
    "55": "Wisconsin",
    "56": "Wyoming",
    "72": "Puerto Rico",
}

STATE_NAMES: tuple[str, ...] = tuple(sorted(set(STATE_FIPS.values())))

RECORD_KEYS: tuple[str, ...] = (
    "fips",
    "state",
    "county_name",
    "commuting_zone",
    "commuting_zone_name",
    "cz_containment",
    "cz_avg_containment",
    "cz_1990",
    "cz_1980",
    "metro_area",
    "county_population",
    "commuting_zone_population",
    "distance",
    "beale_code",
    "msa_code",
    "msa_name",
    "place_code",
)


def state_name(fips: str) -> str | None:
    """Return the full state name for a county FIPS code.

    Parameters
    ----------
    fips : str
        Five-digit county FIPS code, e.g. '01001'.

    Returns
    -------
    str | None
        The full state name, or None when the two-digit prefix is unknown.
    """
    return STATE_FIPS.get(fips[:2])


def _is_missing(value: object) -> bool:
    """Return whether a cell is a null, blank, or NaN placeholder."""
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return isinstance(value, str) and not value.strip()


def _blank_record() -> dict:
    """Return a record with every union field initialized to None."""
    return dict.fromkeys(RECORD_KEYS)


def _text(value: object) -> str | None:
    """Return a stripped string, or None for a blank or NaN cell."""
    if _is_missing(value):
        return None
    return str(value).strip() or None


def _code(value: object) -> str | None:
    """Return an integer-like cell as a decimal-free string, or None.

    Parameters
    ----------
    value : object
        Cell holding a code as an int, a float such as 60.0, or a string.

    Returns
    -------
    str | None
        The code without a trailing '.0', or None for a blank or NaN cell.
    """
    if _is_missing(value):
        return None
    if isinstance(value, str):
        text = value.strip()
        return text[:-2] if text.endswith(".0") else text
    if isinstance(value, float):
        return str(int(value))
    return str(value)


def _padded(value: object, width: int) -> str | None:
    """Return an integer-like code left-padded with zeros to a fixed width."""
    code = _code(value)
    return None if code is None else code.zfill(width)


def _msa_code(value: object) -> str | None:
    """Return a four-digit MSA code, treating an all-zero code as no MSA."""
    code = _padded(value, 4)
    if code is None or set(code) == {"0"}:
        return None
    return code


def _beale(value: object) -> str | None:
    """Return a Beale rural-urban continuum code, coercing '.' to None."""
    if _is_missing(value):
        return None
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return None if text == "." else text or None


def _num(value: object) -> float | None:
    """Return a cell as a float, or None for a blank or non-numeric cell."""
    if _is_missing(value):
        return None
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value))


def _int(value: object) -> int | None:
    """Return a cell as an integer count, or None for a blank cell."""
    number = _num(value)
    return None if number is None else int(number)


def parse_2020(text: str) -> list[dict]:
    """Parse the 2020 commuting-zones CSV into county records.

    Parameters
    ----------
    text : str
        Decoded CSV text with columns FIPStxt, CountyName, StateName, CZ2020,
        CZName, CZContainment, and CZAvgContainment.

    Returns
    -------
    list[dict]
        One record per county, keyed by RECORD_KEYS.
    """
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        fips = (row.get("FIPStxt") or "").strip()
        if not fips:
            continue
        record = _blank_record()
        record.update(
            fips=fips,
            state=state_name(fips) or _text(row.get("StateName")),
            county_name=_text(row.get("CountyName")),
            commuting_zone=_code(row.get("CZ2020")),
            commuting_zone_name=_text(row.get("CZName")),
            cz_containment=_num(row.get("CZContainment")),
            cz_avg_containment=_num(row.get("CZAvgContainment")),
        )
        records.append(record)
    return records


def parse_preliminary_2020(text: str) -> list[dict]:
    """Parse the preliminary 2020 commuting-zones CSV into county records.

    Parameters
    ----------
    text : str
        Decoded CSV text with columns FIPStxt, State, CountyName, and
        PreliminaryCZ2020.

    Returns
    -------
    list[dict]
        One record per county, keyed by RECORD_KEYS.
    """
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        fips = (row.get("FIPStxt") or "").strip()
        if not fips:
            continue
        record = _blank_record()
        record.update(
            fips=fips,
            state=state_name(fips),
            county_name=_text(row.get("CountyName")),
            commuting_zone=_code(row.get("PreliminaryCZ2020")),
        )
        records.append(record)
    return records


def parse_2000(content: bytes) -> list[dict]:
    """Parse the 2000 commuting-zones workbook into county records.

    Parameters
    ----------
    content : bytes
        Raw legacy .xls bytes of the CZ00Equiv sheet.

    Returns
    -------
    list[dict]
        One record per county, keyed by RECORD_KEYS.
    """
    import pandas as pd

    frame = pd.read_excel(io.BytesIO(content), sheet_name="CZ00Equiv", engine="xlrd")
    records: list[dict] = []
    for rec in frame.to_dict(orient="records"):
        fips = _padded(rec.get("FIPS"), 5)
        if fips is None:
            continue
        record = _blank_record()
        record.update(
            fips=fips,
            state=state_name(fips),
            county_name=_text(rec.get("County name")),
            commuting_zone=_code(rec.get("Commuting Zone ID, 2000")),
            cz_1990=_code(rec.get("Commuting Zone ID, 1990")),
            cz_1980=_code(rec.get("Commuting Zone ID, 1980")),
            metro_area=_text(rec.get("Metropolitan area, 2003")),
            county_population=_int(rec.get("County population 2000")),
            commuting_zone_population=_int(rec.get("Commuting zone population 2000")),
        )
        records.append(record)
    return records


def parse_1980_1990(content: bytes) -> list[dict]:
    """Parse the 1980/1990 commuting-zones workbook into county records.

    Parameters
    ----------
    content : bytes
        Raw legacy .xls bytes of the CZLMA903 sheet.

    Returns
    -------
    list[dict]
        One record per county, keyed by RECORD_KEYS.
    """
    import pandas as pd

    frame = pd.read_excel(io.BytesIO(content), sheet_name="CZLMA903", engine="xlrd")
    records: list[dict] = []
    for rec in frame.to_dict(orient="records"):
        fips = _padded(rec.get("County FIPS Code"), 5)
        if fips is None:
            continue
        record = _blank_record()
        record.update(
            fips=fips,
            state=state_name(fips),
            county_name=_text(rec.get("County name")),
            commuting_zone=_code(rec.get("CZ90")),
            cz_1980=_code(rec.get("CZ80")),
            commuting_zone_name=_text(
                rec.get("Name of largest place in commuting zone")
            ),
            county_population=_int(rec.get("Population 1990")),
            distance=_num(rec.get("Distance")),
            beale_code=_beale(rec.get("Rural-urban Continuum Code 1993 (Beale Code)")),
            msa_code=_msa_code(rec.get("MSA 1993")),
            msa_name=_text(rec.get("MSA name")),
            place_code=_padded(rec.get("State place code"), 7),
        )
        records.append(record)
    return records


def extract_inner_csv(zip_bytes: bytes, prefix: str) -> str:
    """Extract and decode one CSV member from a commuting-zones zip archive.

    Parameters
    ----------
    zip_bytes : bytes
        Raw bytes of the zip archive.
    prefix : str
        Inner-file basename prefix of the CSV member to read.

    Returns
    -------
    str
        The decoded CSV text of the matching '.csv' member.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        name = next(
            member
            for member in archive.namelist()
            if member.rsplit("/", 1)[-1].startswith(prefix)
            and member.lower().endswith(".csv")
        )
        raw = archive.read(name)
    return raw.decode("utf-8-sig", errors="replace")


async def afetch_vintage(vintage: str) -> list[dict]:
    """Download and parse one vintage's county lookup through the ERS cache.

    Parameters
    ----------
    vintage : str
        Vintage key from VINTAGE_FILES.

    Returns
    -------
    list[dict]
        One record per county, keyed by RECORD_KEYS.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    config = VINTAGE_FILES[vintage]
    content = await afetch_ers_file(config["media_path"], product=PRODUCT_PAGE)
    if vintage == "2020":
        return parse_2020(content.decode("utf-8-sig", errors="replace"))
    if vintage == "preliminary_2020":
        return parse_preliminary_2020(
            extract_inner_csv(content, config["member_prefix"])
        )
    if vintage == "2000":
        return parse_2000(content)
    return parse_1980_1990(content)
