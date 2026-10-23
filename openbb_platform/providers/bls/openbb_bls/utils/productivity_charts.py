"""BLS Productivity and Costs news-release chart-data scrapers.

Source: https://www.bls.gov/charts/productivity-and-costs/

Each chart page embeds its data as an HTML ``<table class="regular">`` (the
page's "Show table" content). The package mixes two shapes:

* ``ts`` — a quarterly time series: a ``Quarter`` stub column plus one column
  per plotted series (percent changes, or output/hours/productivity indexes).
* ``sector`` — a cross-section for the latest quarter: a ``measure`` stub
  column (labor productivity, output, hours worked, ...) plus one column per
  sector.
"""

from __future__ import annotations

import re
from datetime import date as dateType
from functools import lru_cache
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_bls.utils.constants import BLS_USER_AGENT

_BASE = "https://www.bls.gov/charts/productivity-and-costs"
_HEADERS = {
    "User-Agent": BLS_USER_AGENT,
    "Accept": "text/html,*/*",
}

# First-of-quarter month for "Q1".."Q4".
_QUARTER_MONTH = {1: 1, 2: 4, 3: 7, 4: 10}
_QUARTER_RE = re.compile(r"Q([1-4])\s+(\d{4})")

_PCT_CHANGE_FIELDS: tuple[tuple[str, str, str], ...] = (
    (
        "change_from_previous_quarter",
        "Percent change from previous quarter (annual rate)",
        "pct",
    ),
    (
        "change_from_year_ago",
        "Percent change from same quarter a year ago",
        "pct",
    ),
)

_INDEX_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("output", "Output", "num"),
    ("hours_worked", "Hours worked", "num"),
    ("labor_productivity", "Labor productivity (output per hour)", "num"),
)

# Per-chart spec: slug, human label, kind (ts|sector), default chart type, and
# the ordered value columns as (field_name, BLS header, role). Role drives
# column formatting: num -> plain number, pct -> greenRed percent.
CHART_SPECS: dict[str, dict[str, Any]] = {
    "by-sector": {
        "slug": "labor-productivity-by-sector-most-recent-quarter",
        "label": "Productivity and Costs by Sector",
        "kind": "sector",
        "chart_type": "bar",
        "fields": (
            ("business", "Business", "pct"),
            ("nonfarm_business", "Nonfarm business", "pct"),
            ("manufacturing", "Manufacturing", "pct"),
            ("durable_goods", "Durable goods", "pct"),
            ("nondurable_goods", "Nondurable goods", "pct"),
        ),
    },
    "nonfarm-business-productivity": {
        "slug": "nonfarm-business-sector-productivity-percent-change",
        "label": "Labor Productivity, Nonfarm Business — Percent Change",
        "kind": "ts",
        "chart_type": "line",
        "fields": _PCT_CHANGE_FIELDS,
    },
    "nonfarm-business-labor-costs": {
        "slug": "nonfarm-business-sector-labor-costs-percent-change",
        "label": "Unit Labor Costs, Nonfarm Business — Percent Change",
        "kind": "ts",
        "chart_type": "line",
        "fields": _PCT_CHANGE_FIELDS,
    },
    "manufacturing-productivity": {
        "slug": "manufacturing-productivity-percent-change",
        "label": "Labor Productivity, Manufacturing — Percent Change",
        "kind": "ts",
        "chart_type": "line",
        "fields": _PCT_CHANGE_FIELDS,
    },
    "manufacturing-labor-costs": {
        "slug": "manufacturing-labor-costs-percent-change",
        "label": "Unit Labor Costs, Manufacturing — Percent Change",
        "kind": "ts",
        "chart_type": "line",
        "fields": _PCT_CHANGE_FIELDS,
    },
    "nonfarm-business-indexes": {
        "slug": "nonfarm-business-sector-indexes",
        "label": "Productivity, Output, and Hours Indexes — Nonfarm Business (2017=100)",
        "kind": "ts",
        "chart_type": "line",
        "fields": _INDEX_FIELDS,
    },
    "manufacturing-indexes": {
        "slug": "manufacturing-sector-indexes",
        "label": "Productivity, Output, and Hours Indexes — Manufacturing (2017=100)",
        "kind": "ts",
        "chart_type": "line",
        "fields": _INDEX_FIELDS,
    },
    "nonfinancial-corporations-indexes": {
        "slug": "nonfinancial-corporations-sector-indexes",
        "label": "Productivity, Output, and Hours Indexes — Nonfinancial Corporations (2017=100)",
        "kind": "ts",
        "chart_type": "line",
        "fields": _INDEX_FIELDS,
    },
}


def _decode(content: bytes) -> str:
    """Decode HTML bytes, falling back to latin-1."""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1", errors="replace")


@lru_cache(maxsize=len(CHART_SPECS))
def fetch_chart_html(slug: str) -> str:
    """Download one productivity-and-costs chart page as decoded HTML."""
    import requests

    url = f"{_BASE}/{slug}.htm"
    resp = requests.get(url, headers=_HEADERS, timeout=30)
    if resp.status_code != 200:
        raise OpenBBError(f"BLS returned HTTP {resp.status_code} fetching {url}.")
    return _decode(resp.content)


def _parse_quarter(text: str) -> dateType | None:
    """Parse a ``Qn YYYY`` stub cell into a first-of-quarter date."""
    match = _QUARTER_RE.search(text or "")
    if match is None:
        return None
    return dateType(int(match.group(2)), _QUARTER_MONTH[int(match.group(1))], 1)


def _to_num(text: Any) -> float | None:
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


def parse_chart_table(html: str, chart_key: str) -> dict[str, Any]:
    """Parse one chart page's data table into wide rows keyed by the chart's fields.

    Time-series charts key the stub column as ``date``; the sector
    cross-section keys it as ``measure``. Either way each value column is named
    from the chart's ``CHART_SPECS`` entry so a typed model can declare and
    format it.
    """
    from bs4 import BeautifulSoup

    spec = CHART_SPECS[chart_key]
    is_ts = spec["kind"] == "ts"
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", class_="regular")
    if table is None:
        raise OpenBBError(
            f"BLS productivity-and-costs chart '{chart_key}' page has no data table."
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
    table_id = table.get("id") or f"productivity-chart-{chart_key}"

    out: list[dict[str, Any]] = []
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
            period = _parse_quarter(stub)
            if period is None:
                continue
            record["date"] = period
        else:
            measure = " ".join(stub.split())
            if not measure:
                continue
            record["measure"] = measure
        for col, (field, _label, _role) in enumerate(fields, start=1):
            record[field] = (
                _to_num(cells[col].get_text(" ", strip=True))
                if col < len(cells)
                else None
            )
        out.append(record)
    return {"rows": out, "table_id": table_id, "chart_title": chart_title}


def fetch_and_parse(chart_key: str) -> dict[str, Any]:
    """Resolve a chart key to its slug, download, and parse the data table."""
    slug = CHART_SPECS[chart_key]["slug"]
    return parse_chart_table(fetch_chart_html(slug), chart_key)
