"""BLS Producer Price Index news-release chart-data scrapers.

Source: https://www.bls.gov/charts/producer-price-index/

Each chart page embeds its data as an HTML ``<table class="regular">`` (the
page's "Show table" content). The package mixes two shapes:

* ``ts`` — a monthly time series: a ``Month`` stub column plus one column per
  plotted series (final-demand / intermediate-demand 1- and 12-month percent
  changes).
* ``commodity`` — a final-demand component cross-section for the latest
  release: a ``Commodity`` stub column plus a single percent-change column.
"""

from __future__ import annotations

import calendar
import re
from datetime import date as dateType
from functools import lru_cache
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_bls.utils.constants import BLS_USER_AGENT

_BASE = "https://www.bls.gov/charts/producer-price-index"
_HEADERS = {
    "User-Agent": BLS_USER_AGENT,
    "Accept": "text/html,*/*",
}

_MONTH_LOOKUP: dict[str, int] = {}
for _m in range(1, 13):
    _MONTH_LOOKUP[calendar.month_abbr[_m].lower()] = _m
    _MONTH_LOOKUP[calendar.month_name[_m].lower()] = _m
_MONTH_LOOKUP["sept"] = 9

_MONTH_RE = re.compile(r"([A-Za-z]{3,9})\.?\s+(\d{4})")

_FINAL_DEMAND_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("total", "Total", "pct"),
    (
        "total_less_foods_energy_trade",
        "Total less foods, energy, and trade services",
        "pct",
    ),
    ("goods", "Goods", "pct"),
    ("foods", "Foods", "pct"),
    ("energy", "Energy", "pct"),
    ("goods_less_foods_energy", "Goods less foods and energy", "pct"),
    ("services", "Services", "pct"),
    ("trade", "Trade", "pct"),
    ("transportation_warehousing", "Transportation and warehousing", "pct"),
    (
        "services_less_trade_transport_warehousing",
        "Services less trade, transportation, and warehousing",
        "pct",
    ),
)

_INTERMEDIATE_GOODS_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("overall", "Overall", "pct"),
    ("food", "Food", "pct"),
    ("energy", "Energy", "pct"),
    ("goods_less_food_energy", "Goods other than food and energy", "pct"),
)

_INTERMEDIATE_SERVICES_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("overall", "Overall", "pct"),
    (
        "less_trade_transport_warehousing",
        "Less trade, transportation, and warehousing",
        "pct",
    ),
    (
        "transportation_warehousing",
        "Transportation and warehousing services",
        "pct",
    ),
    ("trade", "Trade services", "pct"),
)

# Per-chart spec: slug, human label, kind (ts|commodity), default chart type,
# and the ordered value columns as (field_name, BLS header, role). Role drives
# column formatting: num -> plain number, pct -> greenRed percent.
CHART_SPECS: dict[str, dict[str, Any]] = {
    "final-demand-1m": {
        "slug": "final-demand-1-month-percent-change",
        "label": "Final Demand — 1-Month % Change (SA)",
        "kind": "ts",
        "chart_type": "line",
        "fields": _FINAL_DEMAND_FIELDS,
    },
    "final-demand-12m": {
        "slug": "final-demand-12-month-percent-change",
        "label": "Final Demand — 12-Month % Change (NSA)",
        "kind": "ts",
        "chart_type": "line",
        "fields": _FINAL_DEMAND_FIELDS,
    },
    "final-demand-components-1m": {
        "slug": "final-demand-goods-and-services-1-month-percent-change",
        "label": "Final Demand Components — 1-Month % Change",
        "kind": "commodity",
        "chart_type": "bar",
        "fields": (("change_1m", "1-month percent change", "pct"),),
    },
    "final-demand-components-12m": {
        "slug": "final-demand-goods-and-services-12-month-percent-change",
        "label": "Final Demand Components — 12-Month % Change (NSA)",
        "kind": "commodity",
        "chart_type": "bar",
        "fields": (("change_12m", "12-month percent change", "pct"),),
    },
    "intermediate-unprocessed-1m": {
        "slug": "intermediate-demand-unprocessed-goods-1-month-percent-change",
        "label": "Intermediate Demand, Unprocessed Goods — 1-Month % Change (SA)",
        "kind": "ts",
        "chart_type": "line",
        "fields": _INTERMEDIATE_GOODS_FIELDS,
    },
    "intermediate-unprocessed-12m": {
        "slug": "intermediate-demand-unprocessed-goods-12-month-percent-change",
        "label": "Intermediate Demand, Unprocessed Goods — 12-Month % Change (NSA)",
        "kind": "ts",
        "chart_type": "line",
        "fields": _INTERMEDIATE_GOODS_FIELDS,
    },
    "intermediate-processed-1m": {
        "slug": "intermediate-demand-processed-goods-1-month-percent-change",
        "label": "Intermediate Demand, Processed Goods — 1-Month % Change (SA)",
        "kind": "ts",
        "chart_type": "line",
        "fields": _INTERMEDIATE_GOODS_FIELDS,
    },
    "intermediate-processed-12m": {
        "slug": "intermediate-demand-processed-goods-12-month-percent-change",
        "label": "Intermediate Demand, Processed Goods — 12-Month % Change (NSA)",
        "kind": "ts",
        "chart_type": "line",
        "fields": _INTERMEDIATE_GOODS_FIELDS,
    },
    "intermediate-services-1m": {
        "slug": "intermediate-demand-services-1-month-percent-change",
        "label": "Intermediate Demand, Services — 1-Month % Change (SA)",
        "kind": "ts",
        "chart_type": "line",
        "fields": _INTERMEDIATE_SERVICES_FIELDS,
    },
    "intermediate-services-12m": {
        "slug": "intermediate-demand-services-12-month-percent-change",
        "label": "Intermediate Demand, Services — 12-Month % Change (NSA)",
        "kind": "ts",
        "chart_type": "line",
        "fields": _INTERMEDIATE_SERVICES_FIELDS,
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
    """Download one producer-price-index chart page as decoded HTML."""
    import requests

    url = f"{_BASE}/{slug}.htm"
    resp = requests.get(url, headers=_HEADERS, timeout=30)
    if resp.status_code != 200:
        raise OpenBBError(f"BLS returned HTTP {resp.status_code} fetching {url}.")
    return _decode(resp.content)


def _parse_month(text: str) -> dateType | None:
    """Parse a ``Mon YYYY`` stub cell into a first-of-month date."""
    match = _MONTH_RE.search(text or "")
    if match is None:
        return None
    month = _MONTH_LOOKUP.get(match.group(1).strip().lower().rstrip("."))
    if month is None:
        return None
    return dateType(int(match.group(2)), month, 1)


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

    Time-series charts key the stub column as ``date``; the final-demand
    component cross-section keys it as ``commodity``. Either way each value
    column is named from the chart's ``CHART_SPECS`` entry so a typed model can
    declare and format it.
    """
    from bs4 import BeautifulSoup

    spec = CHART_SPECS[chart_key]
    is_ts = spec["kind"] == "ts"
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", class_="regular")
    if table is None:
        raise OpenBBError(
            f"BLS producer-price-index chart '{chart_key}' page has no data table."
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
    table_id = table.get("id") or f"ppi-chart-{chart_key}"

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
            period = _parse_month(stub)
            if period is None:
                continue
            record["date"] = period
        else:
            commodity = " ".join(stub.split())
            if not commodity:
                continue
            record["commodity"] = commodity
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
