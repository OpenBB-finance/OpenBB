"""USDA ERS SNAP Policy Database catalog, fetch, and CSV parser."""

import csv
import io
import zipfile
from io import StringIO

PRODUCT_PAGE = "data-products/snap-policy-data-sets"
MEDIA_ZIP = "/media/6473/snap-policy-database.zip"
CSV_MEMBER = "SNAPPolicyDatabase.csv"

STATE_LABELS: dict[str, str] = {
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

STATE_CODES: tuple[str, ...] = tuple(STATE_LABELS)

POLICY_FIELDS: tuple[str, ...] = (
    "bbce",
    "bbce_asset",
    "bbce_a_amt",
    "bbce_a_veh",
    "bbce_inclmt",
    "bbce_child",
    "bbce_elddisinclmt",
    "bbce_multiple",
    "call_any",
    "cap",
    "certearn_0103",
    "certearn_0406",
    "certearn_0712",
    "certearn_1399",
    "certearnavg",
    "certearnmed",
    "certeld_0103",
    "certeld_0406",
    "certeld_0712",
    "certeld_1399",
    "certeldavg",
    "certeldmed",
    "certnonearn_0103",
    "certnonearn_0406",
    "certnonearn_0712",
    "certnonearn_1399",
    "certnonearnavg",
    "certnonearnmed",
    "ebtissuance",
    "faceini",
    "facerec",
    "fingerprint",
    "noncitadultfull",
    "noncitadultpart",
    "noncitchildfull",
    "noncitchildpart",
    "nonciteldfull",
    "nonciteldpart",
    "oapp",
    "outreach",
    "reportsimple",
    "transben",
    "vehexclall",
    "vehexclamt",
    "vehexclone",
)

BBCE_SENTINEL_FIELDS: frozenset[str] = frozenset(
    {
        "bbce_asset",
        "bbce_a_amt",
        "bbce_a_veh",
        "bbce_inclmt",
        "bbce_child",
        "bbce_elddisinclmt",
        "bbce_multiple",
    }
)

FIELD_TO_CSV: dict[str, str] = {
    "certearn_0103": "certearn0103",
    "certearn_0406": "certearn0406",
    "certearn_0712": "certearn0712",
    "certearn_1399": "certearn1399",
    "certeld_0103": "certeld0103",
    "certeld_0406": "certeld0406",
    "certeld_0712": "certeld0712",
    "certeld_1399": "certeld1399",
    "certnonearn_0103": "certnonearn0103",
    "certnonearn_0406": "certnonearn0406",
    "certnonearn_0712": "certnonearn0712",
    "certnonearn_1399": "certnonearn1399",
}


def csv_column(field: str) -> str:
    """Return the source CSV header for a model field name.

    Parameters
    ----------
    field : str
        Model field name from POLICY_FIELDS.

    Returns
    -------
    str
        The un-split CSV header, e.g. 'certearn0103' for 'certearn_0103'.
    """
    return FIELD_TO_CSV.get(field, field)


def policy_value(field: str, raw: str | None) -> str | None:
    """Normalize a raw policy cell, blanking missing and not-applicable codes.

    Parameters
    ----------
    field : str
        Model field name from POLICY_FIELDS.
    raw : str | None
        The raw CSV cell value.

    Returns
    -------
    str | None
        The stripped value, or None for a blank cell or the ``-9`` not-applicable
        sentinel on a BBCE sub-field (which means the state does not use
        broad-based categorical eligibility). The ``-8`` and ``-7`` policy codes
        are preserved.
    """
    if raw is None:
        return None
    value = raw.strip()
    if not value:
        return None
    if value == "-9" and field in BBCE_SENTINEL_FIELDS:
        return None
    return value


def state_options() -> list[dict]:
    """Build the labeled state options for the widget's state selector.

    Returns
    -------
    list[dict]
        Label/value option dictionaries for the fifty states and the
        District of Columbia.
    """
    return [{"label": STATE_LABELS[code], "value": code} for code in STATE_CODES]


def extract_csv_text(zip_bytes: bytes) -> str:
    """Extract and decode the SNAP policy CSV member from the zip bytes.

    Parameters
    ----------
    zip_bytes : bytes
        Raw bytes of the snap-policy-database zip archive.

    Returns
    -------
    str
        The decoded CSV text of the SNAPPolicyDatabase.csv member.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        raw = archive.read(CSV_MEMBER)
    return raw.decode("utf-8-sig", errors="replace")


def parse_rows(text: str, state: str) -> list[dict]:
    """Parse the wide CSV into per-month records for one state.

    Parameters
    ----------
    text : str
        Decoded CSV text of the SNAP policy database.
    state : str
        Two-letter state postal code to keep.

    Returns
    -------
    list[dict]
        Records with state (full name), yearmonth (int), and the raw string
        value of each of the forty-five policy fields, in source file order.
    """
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        if (row.get("state_pc") or "").strip().upper() != state:
            continue
        record: dict = {
            "state": (row.get("statename") or "").strip(),
            "yearmonth": int((row.get("yearmonth") or "").strip()),
        }
        for field in POLICY_FIELDS:
            record[field] = policy_value(field, row.get(csv_column(field)))
        records.append(record)
    return records


async def afetch_dataset() -> str:
    """Download and decode the SNAP policy CSV through the ERS disk cache.

    Returns
    -------
    str
        The decoded CSV text of the current release.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    content = await afetch_ers_file(MEDIA_ZIP, product=PRODUCT_PAGE)
    return extract_csv_text(content)


async def afetch_state(state: str) -> list[dict]:
    """Download the SNAP policy CSV and parse one state's monthly records.

    Parameters
    ----------
    state : str
        Two-letter state postal code.

    Returns
    -------
    list[dict]
        Row records from parse_rows for the selected state.
    """
    text = await afetch_dataset()
    return parse_rows(text, state)
