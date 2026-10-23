"""BLS Consumer Price Index news-release chart-data scrapers.

Source: https://www.bls.gov/charts/consumer-price-index/

Each chart page embeds its data as an HTML ``<table class="regular">`` (the
page's "Show table" content). The package mixes two shapes:

* ``ts`` — a monthly time series: a ``Month`` stub column plus one column per
  plotted series (category / region / metro 12-month percent changes, or the
  selected-item average prices).
* ``category`` — a category cross-section for the latest release: a
  ``Category`` stub column plus a single 12-month percent-change column.
"""

from __future__ import annotations

import calendar
import re
from datetime import date as dateType
from functools import lru_cache
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_bls.utils.constants import BLS_USER_AGENT

_BASE = "https://www.bls.gov/charts/consumer-price-index"
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

_CATEGORY_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("all_items", "All items", "pct"),
    ("food", "Food", "pct"),
    ("food_at_home", "Food at home", "pct"),
    ("food_away_from_home", "Food away from home", "pct"),
    ("energy", "Energy", "pct"),
    ("gasoline", "Gasoline (all types)", "pct"),
    ("electricity", "Electricity", "pct"),
    ("natural_gas", "Natural gas (piped)", "pct"),
    ("all_items_less_food_energy", "All items less food and energy", "pct"),
    (
        "commodities_less_food_energy",
        "Commodities less food and energy commodities",
        "pct",
    ),
    ("apparel", "Apparel", "pct"),
    ("new_vehicles", "New vehicles", "pct"),
    ("medical_care_commodities", "Medical care commodities", "pct"),
    ("services_less_energy", "Services less energy services", "pct"),
    ("shelter", "Shelter", "pct"),
    ("medical_care_services", "Medical care services", "pct"),
    ("education_and_communication", "Education and communication", "pct"),
)

_REGION_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("south", "South", "pct"),
    ("west", "West", "pct"),
    ("midwest", "Midwest", "pct"),
    ("northeast", "Northeast", "pct"),
    ("south_atlantic", "South Atlantic", "pct"),
    ("mountain", "Mountain", "pct"),
    ("east_north_central", "East North Central", "pct"),
    ("new_england", "New England", "pct"),
    ("east_south_central", "East South Central", "pct"),
    ("pacific", "Pacific", "pct"),
    ("west_north_central", "West North Central", "pct"),
    ("middle_atlantic", "Middle Atlantic", "pct"),
    ("west_south_central", "West South Central", "pct"),
)

_METRO_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("atlanta", "Atlanta-Sandy Springs-Roswell, GA", "pct"),
    ("baltimore", "Baltimore-Columbia-Towson, MD", "pct"),
    ("boston", "Boston-Cambridge-Newton, MA-NH", "pct"),
    ("chicago", "Chicago-Naperville-Elgin, IL-IN-WI", "pct"),
    ("dallas", "Dallas-Fort Worth-Arlington, TX", "pct"),
    ("denver", "Denver-Aurora-Lakewood, CO", "pct"),
    ("detroit", "Detroit-Warren-Dearborn, MI", "pct"),
    ("houston", "Houston-The Woodlands-Sugar Land, TX", "pct"),
    ("los_angeles", "Los Angeles-Long Beach-Anaheim, CA", "pct"),
    ("miami", "Miami-Fort Lauderdale-West Palm Beach, FL", "pct"),
    ("minneapolis", "Minneapolis-St. Paul-Bloomington, MN-WI", "pct"),
    ("new_york", "New York-Newark-Jersey City, NY-NJ-PA", "pct"),
    ("philadelphia", "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD", "pct"),
    ("phoenix", "Phoenix-Mesa-Scottsdale, AZ", "pct"),
    ("riverside", "Riverside-San Bernardino-Ontario, CA", "pct"),
    ("san_diego", "San Diego-Carlsbad, CA", "pct"),
    ("san_francisco", "San Francisco-Oakland-Hayward, CA", "pct"),
    ("seattle", "Seattle-Tacoma-Bellevue, WA", "pct"),
    ("st_louis", "St. Louis, MO-IL", "pct"),
    ("tampa", "Tampa-St. Petersburg-Clearwater, FL", "pct"),
    ("urban_alaska", "Urban Alaska", "pct"),
    ("urban_hawaii", "Urban Hawaii", "pct"),
    ("washington_dc", "Washington-Arlington-Alexandria, DC-VA-MD-WV", "pct"),
)

_AVERAGE_PRICE_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("bananas", "Bananas, per lb.", "num"),
    ("oranges", "Oranges, Navel, per lb.", "num"),
    ("bread", "Bread, white, pan, per lb.", "num"),
    ("tomatoes", "Tomatoes, field grown, per lb.", "num"),
    ("chicken", "Chicken, fresh, whole, per lb.", "num"),
    ("electricity_kwh", "Electricity per KWH", "num"),
    ("eggs", "Eggs, grade A, large, per doz.", "num"),
    ("gasoline", "Gasoline, unleaded regular, per gallon", "num"),
    ("ground_chuck", "Ground chuck, 100% beef, per lb.", "num"),
    ("utility_gas", "Utility (piped) gas per therm", "num"),
    ("milk", "Milk, fresh, whole, fortified, per gal.", "num"),
)

# Per-chart spec: slug, human label, kind (ts|category), default chart type,
# and the ordered value columns as (field_name, BLS header, role). Role drives
# column formatting: num -> plain number, pct -> greenRed percent.
CHART_SPECS: dict[str, dict[str, Any]] = {
    "by-category": {
        "slug": "consumer-price-index-by-category",
        "label": "Consumer Price Index by Category — Latest 12-Month % Change",
        "kind": "category",
        "chart_type": "bar",
        "fields": (("change_12m", "12-month percent change", "pct"),),
    },
    "by-category-line": {
        "slug": "consumer-price-index-by-category-line-chart",
        "label": "Consumer Price Index by Category — 12-Month % Change History",
        "kind": "ts",
        "chart_type": "line",
        "fields": _CATEGORY_FIELDS,
    },
    "by-region": {
        "slug": "consumer-price-index-by-region",
        "label": "Consumer Price Index by Region and Division — 12-Month % Change",
        "kind": "ts",
        "chart_type": "line",
        "fields": _REGION_FIELDS,
    },
    "by-metro": {
        "slug": "consumer-price-index-by-metro-area",
        "label": "Consumer Price Index by Metropolitan Area — 12-Month % Change",
        "kind": "ts",
        "chart_type": "line",
        "fields": _METRO_FIELDS,
    },
    "average-prices": {
        "slug": "consumer-price-index-average-price-data",
        "label": "Average Price Data, Selected Items",
        "kind": "ts",
        "chart_type": "line",
        "fields": _AVERAGE_PRICE_FIELDS,
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
    """Download one consumer-price-index chart page as decoded HTML."""
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

    Time-series charts key the stub column as ``date``; the category
    cross-section keys it as ``category``. Either way each value column is
    named from the chart's ``CHART_SPECS`` entry so a typed model can declare
    and format it.
    """
    from bs4 import BeautifulSoup

    spec = CHART_SPECS[chart_key]
    is_ts = spec["kind"] == "ts"
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", class_="regular")
    if table is None:
        raise OpenBBError(
            f"BLS consumer-price-index chart '{chart_key}' page has no data table."
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
    table_id = table.get("id") or f"cpi-chart-{chart_key}"

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
            category = " ".join(stub.split())
            if not category:
                continue
            record["category"] = category
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
