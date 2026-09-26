"""Shared helpers for BLS news-release chart-data scrapers.

The BLS "chart" pages each embed their plotted data as an HTML
``<table class="regular">`` (the page's "Show table" content). Several survey
families publish such packages with the same table shape, differing only in
the period granularity of the stub column (month / quarter / year) and the
set of value columns. These helpers centralise the decode / parse logic so a
per-pack module only declares its ``CHART_SPECS`` and base URL.

A chart spec's ``kind`` is either ``"ts"`` (a time series — the stub column is
a period parsed into ``date``) or the name of the cross-section stub field
(e.g. ``"industry"``, ``"period"``), in which case the stub text is stored
verbatim under that key.
"""

from __future__ import annotations

import calendar
import re
from collections.abc import Callable
from datetime import date as dateType
from functools import lru_cache
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_bls.utils.constants import BLS_USER_AGENT

_MONTH_LOOKUP: dict[str, int] = {}
for _m in range(1, 13):
    _MONTH_LOOKUP[calendar.month_abbr[_m].lower()] = _m
    _MONTH_LOOKUP[calendar.month_name[_m].lower()] = _m
_MONTH_LOOKUP["sept"] = 9

_MONTH_RE = re.compile(r"([A-Za-z]{3,9})\.?\s+(\d{4})")
_QUARTER_RE = re.compile(r"Q([1-4])\s+(\d{4})")
_YEAR_RE = re.compile(r"\b(\d{4})\b")
_QUARTER_MONTH = {1: 1, 2: 4, 3: 7, 4: 10}


def decode(content: bytes) -> str:
    """Decode HTML bytes, falling back to latin-1."""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1", errors="replace")


def make_html_fetcher(base_url: str, maxsize: int = 16) -> Callable[[str], str]:
    """Build a memoised ``fetch_chart_html(slug)`` bound to one chart-pack base URL."""
    headers = {"User-Agent": BLS_USER_AGENT, "Accept": "text/html,*/*"}

    @lru_cache(maxsize=maxsize)
    def fetch_chart_html(slug: str) -> str:
        """Download one chart page as decoded HTML."""
        import requests

        url = f"{base_url}/{slug}.htm"
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            raise OpenBBError(f"BLS returned HTTP {resp.status_code} fetching {url}.")
        return decode(resp.content)

    return fetch_chart_html


def parse_month(text: str) -> dateType | None:
    """Parse a ``Mon YYYY`` stub cell into a first-of-month date."""
    match = _MONTH_RE.search(text or "")
    if match is None:
        return None
    month = _MONTH_LOOKUP.get(match.group(1).strip().lower().rstrip("."))
    if month is None:
        return None
    return dateType(int(match.group(2)), month, 1)


def parse_quarter(text: str) -> dateType | None:
    """Parse a ``Qn YYYY`` stub cell into a first-of-quarter date."""
    match = _QUARTER_RE.search(text or "")
    if match is None:
        return None
    return dateType(int(match.group(2)), _QUARTER_MONTH[int(match.group(1))], 1)


def parse_year(text: str) -> dateType | None:
    """Parse a ``YYYY`` stub cell into a first-of-year date."""
    match = _YEAR_RE.search(text or "")
    if match is None:
        return None
    return dateType(int(match.group(1)), 1, 1)


_PERIOD_PARSERS: dict[str, Callable[[str], dateType | None]] = {
    "month": parse_month,
    "quarter": parse_quarter,
    "year": parse_year,
}


def to_num(text: Any) -> float | None:
    """Coerce a numeric cell (commas, optional %) into a float; blanks -> None."""
    if text is None:
        return None
    cleaned = (
        str(text).replace("\xa0", " ").strip().rstrip("%").replace(",", "").strip()
    )
    if cleaned in ("", "(NA)", "NA", "N/A", "-", "--"):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_chart_table(
    html: str,
    chart_key: str,
    specs: dict[str, dict[str, Any]],
    period: str,
    error_label: str,
    table_id_prefix: str,
) -> dict[str, Any]:
    """Parse one chart page's data table into wide rows keyed by the chart's fields.

    Time-series charts (``kind == "ts"``) key the stub column as ``date`` using
    the ``period`` parser; cross-section charts key it as ``spec["kind"]``.
    Each value column is named from the chart's ``CHART_SPECS`` entry so a typed
    model can declare and format it.
    """
    from bs4 import BeautifulSoup

    spec = specs[chart_key]
    is_ts = spec["kind"] == "ts"
    period_parser = _PERIOD_PARSERS[period]
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", class_="regular")
    if table is None:
        raise OpenBBError(
            f"BLS {error_label} chart '{chart_key}' page has no data table."
        )
    caption = table.find("caption")
    chart_title = (
        " ".join(caption.get_text(" ", strip=True).split())
        if caption is not None
        else spec["label"]
    )
    fields = spec["fields"]
    body = table.find("tbody")
    rows = body.find_all("tr") if body is not None else []
    table_id = table.get("id") or f"{table_id_prefix}-{chart_key}"

    out: list[dict[str, Any]] = []
    seen: set[tuple] = set()
    for tr in rows:
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue
        stub = cells[0].get_text(" ", strip=True)
        record: dict[str, Any] = {
            "chart": chart_key,
            "chart_title": chart_title,
            "table_id": table_id,
        }
        if is_ts:
            period_date = period_parser(stub)
            if period_date is None:
                continue
            stub_value: Any = period_date
            record["date"] = period_date
        else:
            label = " ".join(stub.split())
            if not label:
                continue
            stub_value = label
            record[spec["kind"]] = label
        for col, (field, _label, _role) in enumerate(fields, start=1):
            record[field] = (
                to_num(cells[col].get_text(" ", strip=True))
                if col < len(cells)
                else None
            )
        # Some BLS bar-chart pages repeat a row verbatim (a styled "greenbar"
        # copy used to highlight the chart); drop byte-identical duplicates.
        signature = (stub_value, tuple(record[f] for f, _, _ in fields))
        if signature in seen:
            continue
        seen.add(signature)
        out.append(record)
    return {"rows": out, "table_id": table_id, "chart_title": chart_title}
