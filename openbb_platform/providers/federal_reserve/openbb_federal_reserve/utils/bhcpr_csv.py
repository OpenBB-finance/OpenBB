"""Parse FFIEC BHCPR per-institution CSV into identity, period dates, and coded values."""

from __future__ import annotations

import csv
import io
import re
from typing import Any

CSV_URL = (
    "https://www.ffiec.gov/npw/FinancialReport/ReturnFinancialReportCSV"
    "?rpt=BHCPR&id={rssd}&dt={period}"
)

PERIOD_SUFFIXES = ("", "_4Q", "_1Y", "_2Y", "_3Y")
_CODE = re.compile(r"^([A-Za-z]+?)(\d+)(_\w+)?$")
_META = {
    "Institution Name": "institution_name",
    "City and State": "city_state",
    "Regulatory District": "district",
    "Total Assets": "total_assets",
    "Bank Count": "bank_count",
    "Street Address": "street_address",
    "ID_RSSD": "rssd_id",
    "PEER_GRP": "peer_group",
}


def _numeric(value: str) -> float | int | None:
    """Return the CSV cell as a number, or ``None`` when blank/non-numeric."""
    text = (value or "").strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return int(number) if number.is_integer() else number


def parse_bhcpr_csv(content: bytes) -> dict[str, Any]:
    """Parse the FFIEC BHCPR CSV into identity, period dates, and coded values.

    Parameters
    ----------
    content : bytes
        The raw ``ReturnFinancialReportCSV?rpt=BHCPR`` response bytes.

    Returns
    -------
    dict
        ``identity`` (institution name, city/state, RSSD, district, peer group,
        total assets, bank count), ``periods`` (``{suffix: YYYYMMDD}`` for every
        dated period), ``values`` (``{base-code: {suffix: value}}`` where the base
        code is prefix+id, e.g. ``BHSR028``), and ``descriptions``
        (``{base-code: description}``).
    """
    reader = csv.reader(io.StringIO(content.decode("utf-8-sig")))
    rows = list(reader)

    identity: dict[str, Any] = {}
    periods: dict[str, str] = {}
    values: dict[str, dict[str, Any]] = {}
    descriptions: dict[str, str] = {}

    for row in rows[1:]:
        if len(row) < 3:
            continue
        name, description, value = row[0], row[1], row[2]
        if name in _META:
            identity[_META[name]] = value.strip()
            continue
        if name == "DT" or name.startswith("DT_"):
            periods[name[2:]] = value.strip()
            continue
        match = _CODE.match(name)
        if not match or name.startswith(("PEER_GRP", "DT")):
            continue
        base, suffix = match.group(1) + match.group(2), match.group(3) or ""
        values.setdefault(base, {})[suffix] = _numeric(value)
        descriptions.setdefault(base, description.strip())

    return {
        "identity": identity,
        "periods": periods,
        "values": values,
        "descriptions": descriptions,
    }
