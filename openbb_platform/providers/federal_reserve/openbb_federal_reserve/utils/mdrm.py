"""Federal Reserve Micro Data Reference Manual (MDRM) helpers."""

from __future__ import annotations

from datetime import date as dateType
from functools import cache
from typing import Any

MDRM_URL = "https://www.federalreserve.gov/apps/mdrm/pdf/MDRM.zip"


def _clean_text(value: str) -> str:
    """Unescape HTML entities and collapse whitespace in an MDRM field."""
    import html
    import re

    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def fetch_mdrm_records() -> list[dict[str, Any]]:
    """Download and parse the MDRM, returning one record per code revision."""
    import csv
    import io
    import zipfile
    from datetime import datetime

    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _parse_date(value: str) -> dateType | None:
        """Parse an MDRM ``MM/DD/YYYY ...`` timestamp to a date."""
        text = (value or "").strip()
        if not text:
            return None
        try:
            return datetime.strptime(text.split(" ", 1)[0], "%m/%d/%Y").date()
        except ValueError:
            return None

    def _producer() -> list[dict[str, Any]]:
        """Fetch the MDRM archive and parse the CSV member to records."""
        response = make_request(MDRM_URL)
        response.raise_for_status()
        archive = zipfile.ZipFile(io.BytesIO(response.content))
        member = next(n for n in archive.namelist() if n.lower().endswith(".csv"))
        rows = list(
            csv.reader(io.StringIO(archive.read(member).decode("utf-8", "ignore")))
        )
        header_index = next(
            index
            for index, row in enumerate(rows)
            if any("nemonic" in (cell or "").lower() for cell in row)
        )
        column = {name.strip(): index for index, name in enumerate(rows[header_index])}
        records: list[dict[str, Any]] = []
        for row in rows[header_index + 1 :]:
            if len(row) <= column["Item Name"] or not row[column["Mnemonic"]].strip():
                continue
            code = (
                row[column["Mnemonic"]].strip() + row[column["Item Code"]].strip()
            ).upper()
            description_index = column.get("Description")
            description = (
                _clean_text(row[description_index])
                if description_index is not None and len(row) > description_index
                else ""
            )
            records.append(
                {
                    "code": code,
                    "name": row[column["Item Name"]].strip(),
                    "description": description,
                    "form": row[column["Reporting Form"]].strip(),
                    "start": _parse_date(row[column["Start Date"]]),
                    "end": _parse_date(row[column["End Date"]]),
                }
            )
        return records

    return cached(
        "mdrm_records", lambda: seconds_until_next_release("quarterly"), _producer
    )


def fetch_mdrm_item_types() -> dict[str, str]:
    """Return an MDRM item-code to ItemType map."""
    import csv
    import io
    import zipfile

    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> dict[str, str]:
        """Fetch the MDRM archive and map each code to its ItemType."""
        response = make_request(MDRM_URL)
        response.raise_for_status()
        archive = zipfile.ZipFile(io.BytesIO(response.content))
        member = next(n for n in archive.namelist() if n.lower().endswith(".csv"))
        rows = list(
            csv.reader(io.StringIO(archive.read(member).decode("utf-8", "ignore")))
        )
        header_index = next(
            index
            for index, row in enumerate(rows)
            if any("nemonic" in (cell or "").lower() for cell in row)
        )
        column = {name.strip(): index for index, name in enumerate(rows[header_index])}
        item_type_index = column["ItemType"]
        item_types: dict[str, str] = {}
        for row in rows[header_index + 1 :]:
            if len(row) <= item_type_index or not row[column["Mnemonic"]].strip():
                continue
            code = (
                row[column["Mnemonic"]].strip() + row[column["Item Code"]].strip()
            ).upper()
            item_types[code] = row[item_type_index].strip().upper()
        return item_types

    return cached(
        "mdrm_item_types", lambda: seconds_until_next_release("quarterly"), _producer
    )


def _monetary_classification() -> dict[str, Any]:
    """Load the committed Reporting Central monetary classification asset."""
    import json
    from pathlib import Path

    asset = (
        Path(__file__).resolve().parent.parent
        / "assets"
        / "ffiec"
        / "monetary_classification.json"
    )
    return json.loads(asset.read_text(encoding="utf-8"))


@cache
def fetch_monetary_codes() -> tuple[frozenset[str], frozenset[str]]:
    """Return the non-monetary code set and FFIEC 101 non-monetary column prefixes.

    Returns
    -------
    tuple[frozenset[str], frozenset[str]]
        The set of MDRM codes whose ``F``/``D`` ItemType is non-monetary, and the
        set of four-character FFIEC 101 Schedule B/C column prefixes whose ``D``
        items are percents or years rather than dollars.
    """
    classification = _monetary_classification()
    codes = frozenset(classification["nonmonetary_codes"])
    prefixes = frozenset(classification["ffiec101_nonmonetary_columns"])
    return codes, prefixes


def is_monetary(code: str, item_type: str | None) -> bool:
    """Return whether a Reporting Central code's value is a dollar amount.

    A dollar amount is filed in thousands and must be scaled to whole dollars; any
    other value (percent, ratio, rate, years, count, factor) is already the true
    value. The determination is per code, never inferred from the filed value:
    string and percentage ItemTypes are never monetary; an ``F``/``D`` code is
    monetary unless it is named in the committed non-monetary set or sits in an
    FFIEC 101 Schedule B/C column that holds a percent or maturity in years.

    Parameters
    ----------
    code : str
        The MDRM item code.
    item_type : str | None
        The code's MDRM ItemType (``F``, ``D``, ``P``, ``S``), or ``None`` when
        the code is absent from the MDRM.
    """
    if item_type not in ("F", "D"):
        return False
    nonmonetary_codes, nonmonetary_prefixes = fetch_monetary_codes()
    if code in nonmonetary_codes:
        return False
    return not (item_type == "D" and code[:4] in nonmonetary_prefixes)


def _resolve_revisions(
    as_of: dateType | None, prefix: str | None
) -> dict[str, dict[str, Any]]:
    """Pick one MDRM revision per code, preferring the window covering ``as_of``."""
    records = fetch_mdrm_records()
    if prefix:
        upper = prefix.upper()
        records = [record for record in records if record["code"].startswith(upper)]

    revisions: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        revisions.setdefault(record["code"], []).append(record)

    resolved: dict[str, dict[str, Any]] = {}
    for code, code_revisions in revisions.items():
        chosen: dict[str, Any] | None = None
        if as_of is not None:
            covering = [
                revision
                for revision in code_revisions
                if (revision["start"] or dateType.min)
                <= as_of
                <= (revision["end"] or dateType.max)
            ]
            if covering:
                chosen = max(covering, key=lambda r: r["start"] or dateType.min)
        if chosen is None:
            chosen = max(code_revisions, key=lambda r: r["end"] or dateType.min)
        resolved[code] = chosen
    return resolved


def fetch_mdrm_dictionary(
    as_of: dateType | None = None, prefix: str | None = None
) -> dict[str, str]:
    """Return an MDRM item-code to line-item-name map, resolved as-of a date.

    Parameters
    ----------
    as_of : date | None
        The report period; the revision whose effective window covers this date
        is preferred. When ``None`` or uncovered, the most recently-ended
        revision is used.
    prefix : str | None
        Restrict to codes beginning with this mnemonic (e.g. ``RISK``).
    """
    return {
        code: record["name"]
        for code, record in _resolve_revisions(as_of, prefix).items()
    }


def fetch_mdrm_definitions(
    as_of: dateType | None = None, prefix: str | None = None
) -> dict[str, str]:
    """Return an MDRM item-code to definition (narrative) map, resolved as-of a date.

    Parameters
    ----------
    as_of : date | None
        The report period; the revision whose effective window covers this date
        is preferred. When ``None`` or uncovered, the most recently-ended
        revision is used.
    prefix : str | None
        Restrict to codes beginning with this mnemonic (e.g. ``UBPR``).
    """
    return {
        code: record["description"]
        for code, record in _resolve_revisions(as_of, prefix).items()
        if record.get("description")
    }
