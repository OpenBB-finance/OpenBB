"""BLS Employment Situation news-release Summary Tables A and B scrapers.

Source: https://www.bls.gov/news.release/empsit.a.htm (Summary table A,
household data) and empsit.b.htm (Summary table B, establishment data).

Both are ``<table class="regular">`` snapshots: a ``Category`` stub, four
seasonally-adjusted month columns (same month a year ago, two prior months,
the latest month — the labels shift each release), and — for table A — a
1-month change column. Rows are grouped under section headers (a label row
whose value cells are empty), which we carry onto each data row.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_bls.utils.constants import BLS_USER_AGENT

_BASE = "https://www.bls.gov/news.release"
_HEADERS = {"User-Agent": BLS_USER_AGENT, "Accept": "text/html,*/*"}

# Per-table spec: news-release slug, human label, and whether the table carries
# the trailing over-the-month change column (table A does, table B does not).
SUMMARY_SPECS: dict[str, dict[str, Any]] = {
    "a": {
        "slug": "empsit.a",
        "label": "Summary Table A — Household Data (Seasonally Adjusted)",
        "has_change": True,
    },
    "b": {
        "slug": "empsit.b",
        "label": "Summary Table B — Establishment Data (Seasonally Adjusted)",
        "has_change": False,
    },
}

_FOOTNOTE_RE = re.compile(r"\(\s*[0-9p]+\s*\)", re.IGNORECASE)


def _decode(content: bytes) -> str:
    """Decode HTML bytes, falling back to latin-1."""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1", errors="replace")


@lru_cache(maxsize=len(SUMMARY_SPECS))
def fetch_summary_html(slug: str) -> str:
    """Download one Employment Situation summary-table page as decoded HTML."""
    import requests

    url = f"{_BASE}/{slug}.htm"
    resp = requests.get(url, headers=_HEADERS, timeout=30)
    if resp.status_code != 200:
        raise OpenBBError(f"BLS returned HTTP {resp.status_code} fetching {url}.")
    return _decode(resp.content)


def _clean_label(text: str) -> str:
    """Strip footnote markers like ``( 1 )`` / ``( p )`` and collapse whitespace."""
    return " ".join(_FOOTNOTE_RE.sub("", text or "").split())


def _to_value(text: Any) -> float | None:
    """Coerce a summary cell (``$``, commas, ``%``) into a float; blanks -> None."""
    if text is None:
        return None
    cleaned = (
        str(text)
        .replace("\xa0", " ")
        .replace("$", "")
        .replace(",", "")
        .replace("%", "")
        .strip()
    )
    if cleaned in ("", "-", "--", "(NA)", "NA", "N/A"):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_summary_table(html: str, key: str) -> dict[str, Any]:
    """Parse a summary table into section-tagged rows with positional months.

    Each data row yields the four month values (oldest -> latest) plus the
    over-the-month change when present. Section-header rows set the ``section``
    carried by the rows beneath them.
    """
    from bs4 import BeautifulSoup

    spec = SUMMARY_SPECS[key]
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", class_="regular")
    if table is None:
        raise OpenBBError(
            f"BLS Employment Situation summary table '{key}' page has no data table."
        )
    caption = table.find("caption")
    title = (
        " ".join(caption.get_text(" ", strip=True).split())
        if caption is not None
        else spec["label"]
    )
    table_id = table.get("id") or f"empsit-summary-{key}"

    head = table.find("thead")
    periods: list[str] = []
    if head is not None:
        header_cells = [
            _clean_label(c.get_text(" ", strip=True))
            for c in head.find_all(["th", "td"])
        ]
        # Drop the stub header and (table A) the trailing change header.
        value_headers = header_cells[1:]
        periods = value_headers[:4]

    body = table.find("tbody") or table
    rows = body.find_all("tr")
    out: list[dict[str, Any]] = []
    section: str | None = None
    for tr in rows:
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
        if not cells:
            continue
        label = _clean_label(cells[0])
        values = cells[1:]
        has_values = any(v.strip() for v in values)
        if not has_values:
            # A label with no values is a section header; a fully blank row is
            # a separator we skip.
            if label:
                section = label
            continue
        out.append(
            {
                "section": section,
                "category": label,
                "year_ago": _to_value(values[0]) if len(values) > 0 else None,
                "two_months_prior": _to_value(values[1]) if len(values) > 1 else None,
                "prior_month": _to_value(values[2]) if len(values) > 2 else None,
                "latest": _to_value(values[3]) if len(values) > 3 else None,
                "change_1_month": (
                    _to_value(values[4])
                    if spec["has_change"] and len(values) > 4
                    else None
                ),
            }
        )
    return {"rows": out, "title": title, "periods": periods, "table_id": table_id}


def fetch_and_parse(key: str) -> dict[str, Any]:
    """Resolve a summary-table key to its slug, download, and parse it."""
    slug = SUMMARY_SPECS[key]["slug"]
    return parse_summary_table(fetch_summary_html(slug), key)
