"""BLS Productivity release catalog."""

from __future__ import annotations

import re
from datetime import date as dateType
from functools import lru_cache
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_bls.utils.constants import BLS_USER_AGENT

_INDEX_URL = "https://www.bls.gov/productivity/news-releases.htm"
_HEADERS = {
    "User-Agent": BLS_USER_AGENT,
    "Accept": "text/html,*/*",
}

_LP_ID = "lp"
_TFP_ID = "tfp"
_END_ID = "sch"

_NR_HREF_RE = re.compile(r"^/news\.release/(?P<code>[a-z0-9]+)\.nr0\.htm$", re.I)
_PDF_HREF_RE = re.compile(r"^/news\.release/pdf/(?P<code>[a-z0-9]+)\.pdf$", re.I)


def _decode_html(content: bytes) -> str:
    """Decode BLS page bytes, falling back to latin-1."""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1", errors="replace")


@lru_cache(maxsize=1)
def scrape_release_catalog() -> tuple[dict[str, Any], ...]:
    """Return one entry per published current Productivity news release."""
    import requests
    from bs4 import BeautifulSoup

    resp = requests.get(_INDEX_URL, headers=_HEADERS, timeout=30)
    if resp.status_code != 200:
        raise OpenBBError(
            f"BLS returned HTTP {resp.status_code} fetching {_INDEX_URL}."
        )
    text = _decode_html(resp.content)
    BeautifulSoup(text, "lxml")

    lp_start = text.find(f'id="{_LP_ID}"')
    tfp_start = text.find(f'id="{_TFP_ID}"')
    end = text.find(f'id="{_END_ID}"')
    if lp_start < 0 or tfp_start < 0 or end < 0:
        raise OpenBBError(
            "BLS productivity news-releases page layout changed — could not "
            "locate the LP/TFP/Schedule anchors."
        )

    sections = (
        ("labor_productivity", text[lp_start:tfp_start]),
        ("total_factor_productivity", text[tfp_start:end]),
    )

    out: list[dict[str, Any]] = []
    seen_codes: set[str] = set()
    for category, html_chunk in sections:
        sub = BeautifulSoup(html_chunk, "lxml")
        current_release: dict[str, Any] | None = None
        for anchor in sub.find_all("a", href=True):
            href = str(anchor["href"]).strip()
            inner = " ".join(anchor.get_text(" ", strip=True).split())
            nr_match = _NR_HREF_RE.match(href)
            if nr_match:
                code = nr_match.group("code").lower()
                if inner.upper() == "HTML":
                    continue
                if code in seen_codes:
                    current_release = None
                    continue
                seen_codes.add(code)
                current_release = {
                    "code": code,
                    "category": category,
                    "title": inner,
                    "news_release_url": _abs(href),
                    "pdf_url": _abs(f"/news.release/pdf/{code}.pdf"),
                    "toc_url": _abs(f"/news.release/{code}.toc.htm"),
                    "supplemental_toc_url": None,
                }
                out.append(current_release)
                continue
            pdf_match = _PDF_HREF_RE.match(href)
            if pdf_match and current_release is not None:
                pdf_code = pdf_match.group("code").lower()
                if pdf_code == current_release["code"]:
                    current_release["pdf_url"] = _abs(href)

    for entry in out:
        if entry["code"] == "prod2":
            entry["supplemental_toc_url"] = "https://www.bls.gov/web/prod2.supp.toc.htm"

    return tuple(out)


def _abs(href: str) -> str:
    """Promote a BLS-relative href to absolute https://www.bls.gov form."""
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return f"https://www.bls.gov{href}"
    return f"https://www.bls.gov/{href}"


@lru_cache(maxsize=8)
def scrape_supplemental_files(supp_toc_url: str) -> tuple[dict[str, Any], ...]:
    """Return every XLSX / PDF listed on a Productivity supplemental TOC page."""
    import requests
    from bs4 import BeautifulSoup

    resp = requests.get(supp_toc_url, headers=_HEADERS, timeout=30)
    if resp.status_code != 200:
        return ()
    soup = BeautifulSoup(_decode_html(resp.content), "lxml")
    base_dir = supp_toc_url.rsplit("/", 1)[0]
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"]).strip()
        inner = " ".join(anchor.get_text(" ", strip=True).split())
        if not href.lower().endswith((".xlsx", ".pdf", ".csv", ".txt")):
            continue
        url = _resolve_relative(base_dir, href)
        if url in seen:
            continue
        seen.add(url)
        filename = url.rsplit("/", 1)[-1]
        stem = filename.rsplit(".", 1)[0].replace("-", " ").replace("_", " ")
        display_name = stem.title()
        out.append(
            {
                "name": display_name,
                "url": url,
                "format": filename.rsplit(".", 1)[-1].lower(),
                "label_from_page": inner,
            }
        )
    return tuple(out)


def _resolve_relative(base_dir: str, href: str) -> str:
    """Resolve a Productivity supp-TOC ``../web/...`` relative href."""
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return f"https://www.bls.gov{href}"
    parts = base_dir.split("/")
    rel_parts = href.split("/")
    for part in rel_parts:
        if part == "..":
            if parts:
                parts.pop()
        elif part != ".":
            parts.append(part)
    return "/".join(parts)


_ARCHIVE_PAGE: dict[str, tuple[str, str | None]] = {
    "prod2": ("https://www.bls.gov/bls/news-release/prod.htm", None),
    "prin": ("https://www.bls.gov/bls/news-release/prin.htm", None),
    "prin1": ("https://www.bls.gov/bls/news-release/prin.htm", None),
    "prin2": ("https://www.bls.gov/bls/news-release/prin.htm", None),
    "prin3": (
        "https://www.bls.gov/bls/news-release/home.htm",
        "tfp-detailed-industries",
    ),
    "prin4": ("https://www.bls.gov/bls/news-release/home.htm", "PRODSTATE"),
    "prod3": ("https://www.bls.gov/bls/news-release/home.htm", "tfp"),
    "prod5": ("https://www.bls.gov/bls/news-release/home.htm", "tfp-major-industries"),
}

_ARCHIVE_HREF_RE = re.compile(
    r"/news\.release/archives/(?P<code>[a-z0-9]+)_"
    r"(?P<m>\d{2})(?P<d>\d{2})(?P<y>\d{4})\.(?P<ext>htm|html|pdf|xlsx|txt)$",
    re.IGNORECASE,
)


@lru_cache(maxsize=4)
def _scrape_archive_page(url: str) -> tuple[dict[str, Any], ...]:
    """Read one archive index page and return every dated release entry."""
    import requests
    from bs4 import BeautifulSoup

    resp = requests.get(url, headers=_HEADERS, timeout=30)
    if resp.status_code != 200:
        return ()
    soup = BeautifulSoup(_decode_html(resp.content), "lxml")
    out: list[dict[str, Any]] = []
    titles_by_url: dict[str, str] = {}
    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"]).strip()
        text = " ".join(anchor.get_text(" ", strip=True).split())
        if not text or len(text) <= 4:
            continue
        if text.upper() in ("HTML", "PDF", "XLSX", "TXT"):  # pragma: no cover
            continue  # All four labels are length<=4, already filtered above.
        match = _ARCHIVE_HREF_RE.search(href)
        if match:
            titles_by_url[match.group(0)] = text

    seen: set[tuple[str, str]] = set()
    current_section: str | None = None
    for el in soup.find_all(["h1", "h2", "h3", "h4", "a", "span", "div"]):
        if el.name != "a":
            an_id = el.get("id")
            if an_id:
                current_section = str(an_id)
            continue
        href = str(el.get("href") or "")
        if not href:
            an_id = el.get("id")
            if an_id:
                current_section = str(an_id)
            continue
        match = _ARCHIVE_HREF_RE.search(href)
        if not match:
            continue
        code = match.group("code").lower()
        month = int(match.group("m"))
        day = int(match.group("d"))
        year = int(match.group("y"))
        ext = match.group("ext").lower()
        try:
            release_date = dateType(year, month, day)
        except ValueError:
            continue
        key = (code, match.group(0))
        if key in seen:
            continue
        seen.add(key)
        url_abs = _abs(href)
        title = titles_by_url.get(match.group(0))
        out.append(
            {
                "code": code,
                "section": current_section,
                "url": url_abs,
                "format": ext if ext in ("pdf", "xlsx", "txt") else "htm",
                "date": release_date,
                "title": title,
            }
        )
    return tuple(out)


@lru_cache(maxsize=16)
def scrape_archive(code: str) -> tuple[dict[str, Any], ...]:
    """Return archived release entries for ``code``, deduped by date."""
    location = _ARCHIVE_PAGE.get(code.lower())
    if location is None:
        return ()
    url, section = location
    all_entries = _scrape_archive_page(url)
    if section is None:
        candidates = [e for e in all_entries if e["code"] == code]
    else:
        candidates = [
            e for e in all_entries if e["code"] == code and e.get("section") == section
        ]

    by_date: dict[dateType, dict[str, Any]] = {}
    for entry in candidates:
        slot = by_date.setdefault(
            entry["date"],
            {
                "code": entry["code"],
                "date": entry["date"],
                "title": entry["title"],
                "html_url": None,
                "pdf_url": None,
            },
        )
        if slot["title"] is None and entry["title"]:
            slot["title"] = entry["title"]
        if entry["format"] == "pdf":
            slot["pdf_url"] = entry["url"]
        else:
            slot["html_url"] = entry["url"]

    return tuple(sorted(by_date.values(), key=lambda e: e["date"], reverse=True))
