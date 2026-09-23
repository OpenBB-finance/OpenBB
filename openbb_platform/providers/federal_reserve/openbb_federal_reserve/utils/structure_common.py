"""Shared helpers for the committed financial-report structure generators."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

MDRM = re.compile(r"\b[A-Z]{4}[A-Z0-9]{4}\b")


def latest_quarter_end(today: date | None = None) -> str:
    """Return the most recent completed calendar quarter end as ``YYYYMMDD``.

    Parameters
    ----------
    today : datetime.date, optional
        The reference date; defaults to the current date.

    Returns
    -------
    str
        The latest quarter end strictly before ``today`` as ``YYYYMMDD``.
    """
    today = today or date.today()
    ends = (
        date(today.year, 3, 31),
        date(today.year, 6, 30),
        date(today.year, 9, 30),
        date(today.year, 12, 31),
        date(today.year - 1, 12, 31),
    )
    completed = sorted(end for end in ends if end < today)
    return completed[-1].strftime("%Y%m%d")


def fetch_pdf_bytes(url: str) -> bytes:
    """Download a public Reporting Central user guide PDF as raw bytes."""
    import requests

    response = requests.get(url, timeout=180)
    response.raise_for_status()
    return response.content


def fetch_report_csv(report_code: str, rssd_id: int, date_str: str) -> str:
    """Fetch a per-institution ``ReturnFinancialReportCSV`` payload as text.

    Parameters
    ----------
    report_code : str
        The ``rpt`` code understood by the endpoint (for example ``"FFIEC002"``).
    rssd_id : int
        The reporting entity's RSSD identifier.
    date_str : str
        The reporting period as ``YYYYMMDD`` (a calendar quarter-end).

    Returns
    -------
    str
        The decoded CSV payload.
    """
    from openbb_federal_reserve.utils.ffiec import _fetch_bytes

    raw = _fetch_bytes(
        "FinancialReport/ReturnFinancialReportCSV"
        f"?rpt={report_code}&id={rssd_id}&dt={date_str}",
        referer="https://www.ffiec.gov/npw/FinancialReport/FinancialDataDownload",
    )
    return raw.decode("utf-8", "replace")


def collect_schedules(items: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Return the distinct ``{schedule, name}`` pairs in first-seen order."""
    schedules: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        code = item["schedule"]
        if code and code not in seen:
            seen.add(code)
            schedules.append({"schedule": code, "name": item["schedule_name"]})
    return schedules


def asset_path(structure_dir: str) -> Path:
    """Return the committed ``assets/<dir>/structure.json`` path."""
    return (
        Path(__file__).resolve().parent.parent
        / "assets"
        / structure_dir
        / "structure.json"
    )
