"""BLS Real Earnings (REALER) news-release archive scraper."""

from __future__ import annotations

import re
from datetime import date as dateType
from functools import lru_cache
from typing import Any, cast

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_bls.utils.constants import BLS_USER_AGENT

_ARCHIVE_URL = "https://www.bls.gov/bls/news-release/realer.htm"
_CURRENT_PDF = "https://www.bls.gov/news.release/pdf/realer.pdf"
_CURRENT_HTML = "https://www.bls.gov/news.release/realer.nr0.htm"
_HEADERS = {
    "User-Agent": BLS_USER_AGENT,
    "Accept": "text/html,*/*",
}

_ARCHIVE_HREF_RE = re.compile(
    r"^/news\.release/archives/realer_(?P<m>\d{2})(?P<d>\d{2})(?P<y>\d{4})\.pdf$",
    re.IGNORECASE,
)


def _decode(content: bytes) -> str:
    """Decode HTML bytes, falling back to latin-1."""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1", errors="replace")


@lru_cache(maxsize=1)
def scrape_archive() -> tuple[dict[str, Any], ...]:
    """Return one entry per archived Real Earnings release PDF, sorted newest-first."""
    import requests
    from bs4 import BeautifulSoup

    resp = requests.get(_ARCHIVE_URL, headers=_HEADERS, timeout=30)
    if resp.status_code != 200:
        raise OpenBBError(
            f"BLS returned HTTP {resp.status_code} fetching {_ARCHIVE_URL}."
        )
    soup = BeautifulSoup(_decode(resp.content), "lxml")
    titles_by_pdf: dict[str, str] = {}
    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"]).strip()
        if not _ARCHIVE_HREF_RE.match(href):
            continue
        # Prefer the visible <li> list text; BLS aria-labels are sometimes
        # stale while the list text carries the correct reference month.
        title = ""
        li = anchor.find_parent("li")
        if li is not None:
            li_text = " ".join(li.get_text(" ", strip=True).split())
            li_text = re.sub(r"\(\s*(?:TXT|PDF|HTM|HTML)\s*\)", "", li_text, flags=re.I)
            title = li_text.strip(" -—")
        if title.upper() in ("", "TXT", "PDF", "HTM", "HTML"):
            aria = anchor.get("aria-label")
            if aria:
                aria_clean = str(aria).strip()
                for suffix in (" PDF", " HTM", " HTML"):
                    if aria_clean.upper().endswith(suffix.upper()):
                        aria_clean = aria_clean[: -len(suffix)].strip()
                        break
                title = aria_clean
        if title.upper() in ("", "TXT", "PDF", "HTM", "HTML"):
            title = " ".join(anchor.get_text(" ", strip=True).split())
        # When multiple anchors point at one PDF, keep the descriptive title
        # rather than letting a bare "PDF" link clobber it.
        existing = titles_by_pdf.get(href)
        if existing is None or existing.upper() in ("", "TXT", "PDF", "HTM", "HTML"):
            titles_by_pdf[href] = title

    out: list[dict[str, Any]] = []
    for href, title in titles_by_pdf.items():
        # titles_by_pdf is built from regex-matched hrefs and dict keys are
        # unique, so we know match succeeds and href is not a duplicate.
        match = cast("re.Match[str]", _ARCHIVE_HREF_RE.match(href))
        try:
            release_date = dateType(
                int(match.group("y")), int(match.group("m")), int(match.group("d"))
            )
        except ValueError:
            continue
        out.append(
            {
                "date": release_date,
                "title": title or f"Real Earnings release {release_date.isoformat()}",
                "url": f"https://www.bls.gov{href}",
            }
        )
    out.sort(key=lambda e: e["date"], reverse=True)
    return tuple(out)


def current_release() -> dict[str, Any]:
    """Return the always-current Real Earnings release entry (stable URL)."""
    return {
        "title": "Real Earnings — current release",
        "url": _CURRENT_PDF,
        "html_url": _CURRENT_HTML,
    }
