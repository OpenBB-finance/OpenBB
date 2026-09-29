"""BLS U.S. Import/Export Price Index news-release chart-data scrapers.

Source: https://www.bls.gov/charts/import-export/
"""

from __future__ import annotations

import calendar
import re
from datetime import date as dateType
from functools import lru_cache
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_bls.utils.constants import BLS_USER_AGENT

_BASE = "https://www.bls.gov/charts/import-export"
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

CHART_SLUGS: dict[str, str] = {
    "import-export": "us-import-and-export-price-indexes-12-month-percent-change",
    "imports-by-category": "us-import-price-indexes-by-category-12-month-percent-change",
    "exports-by-category": "us-export-price-indexes-by-category-12-month-percent-change",
    "imports-by-origin": "us-import-price-indexes-by-origin-12-month-percent-change",
    "exports-by-grains": "us-export-price-indexes-by-selected-grains-12-month-percent-change",
    "air-passenger-fares": "air-passenger-fares-12-month-percent-change",
}

CHART_LABELS: dict[str, str] = {
    "import-export": "U.S. Import/Export Price Indexes",
    "imports-by-category": "U.S. Import Price Indexes by Category",
    "exports-by-category": "U.S. Export Price Indexes by Category",
    "imports-by-origin": "U.S. Import Price Indexes by Locality of Origin",
    "exports-by-grains": "U.S. Export Price Indexes by Selected Grains",
    "air-passenger-fares": "Air Passenger Fares (Import/Export)",
}

# Ordered (field_name, BLS column header) per chart, matching the source
# table's column order after the leading "Month" stub. Drives both the wide
# pivot and the per-chart typed Data models.
CHART_FIELDS: dict[str, tuple[tuple[str, str], ...]] = {
    "import-export": (
        ("all_imports", "All imports"),
        ("fuel_imports", "Fuel imports"),
        ("nonfuel_imports", "Nonfuel imports"),
        ("all_exports", "All exports"),
        ("agricultural_exports", "Agricultural exports"),
        ("nonagricultural_exports", "Nonagricultural exports"),
    ),
    "imports-by-category": (
        ("all_imports", "All imports"),
        ("foods_feeds_beverages", "Foods, feeds, and beverages"),
        ("industrial_supplies", "Industrial supplies and materials"),
        ("capital_goods", "Capital goods"),
        ("automotive", "Automotive vehicles, parts and engines"),
        ("consumer_goods", "Consumer goods, excluding automotives"),
    ),
    "exports-by-category": (
        ("all_exports", "All exports"),
        ("foods_feeds_beverages", "Foods, feeds, and beverages"),
        ("industrial_supplies", "Industrial supplies and materials"),
        ("capital_goods", "Capital goods"),
        ("automotive", "Automotive vehicles, parts and engines"),
        ("consumer_goods", "Consumer goods, excluding automotives"),
    ),
    "imports-by-origin": (
        ("canada", "Canada"),
        ("european_union", "European Union"),
        ("france", "France"),
        ("germany", "Germany"),
        ("united_kingdom", "United Kingdom"),
        ("latin_america", "Latin America"),
        ("mexico", "Mexico"),
        ("pacific_rim", "Pacific Rim"),
        ("china", "China"),
        ("japan", "Japan"),
    ),
    "exports-by-grains": (
        ("wheat", "Wheat"),
        ("soybeans", "Soybeans"),
        ("corn", "Corn"),
    ),
    "air-passenger-fares": (
        ("import_fares", "Import air passenger fares"),
        ("import_europe", "Import Europe"),
        ("import_asia", "Import Asia"),
        ("import_latam", "Import Latin America/Caribbean"),
        ("export_fares", "Export air passenger fares"),
        ("export_europe", "Export Europe"),
        ("export_asia", "Export Asia"),
        ("export_latam", "Export Latin America/Caribbean"),
    ),
}


def _decode(content: bytes) -> str:
    """Decode HTML bytes, falling back to latin-1."""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1", errors="replace")


@lru_cache(maxsize=len(CHART_SLUGS))
def fetch_chart_html(slug: str) -> str:
    """Download one import-export chart page as decoded HTML."""
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


def _to_pct(text: Any) -> float | None:
    """Coerce a ``"X.X%"`` cell into a float; blanks / N/A become None."""
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

    Each row is ``date`` plus one numeric column per series (named from
    ``CHART_FIELDS``), so a per-chart typed model can declare and format every
    column while the table-to-chart view plots one line per series.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", class_="regular")
    if table is None:
        raise OpenBBError(
            f"BLS import-export chart '{chart_key}' page has no data table."
        )
    caption = table.find("caption")
    chart_title = (
        " ".join(caption.get_text(" ", strip=True).split())
        if caption is not None
        else CHART_LABELS.get(chart_key, chart_key)
    )
    fields = CHART_FIELDS.get(chart_key, ())
    body = table.find("tbody")
    rows = body.find_all("tr") if body is not None else []
    table_id = table.get("id") or f"ximpim-chart-{chart_key}"

    out: list[dict[str, Any]] = []
    for tr in rows:
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue
        period = _parse_month(cells[0].get_text(" ", strip=True))
        if period is None:
            continue
        record: dict[str, Any] = {
            "date": period,
            "chart": chart_key,
            "chart_title": chart_title,
            "table_id": table_id,
        }
        for col, (field, _label) in enumerate(fields, start=1):
            record[field] = (
                _to_pct(cells[col].get_text(" ", strip=True))
                if col < len(cells)
                else None
            )
        out.append(record)
    return {"rows": out, "table_id": table_id, "chart_title": chart_title}


def fetch_and_parse(chart_key: str) -> dict[str, Any]:
    """Resolve a chart key to its slug, download, and parse the data table."""
    slug = CHART_SLUGS[chart_key]
    return parse_chart_table(fetch_chart_html(slug), chart_key)
