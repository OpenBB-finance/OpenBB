"""BLS JOLTS release catalog."""

from __future__ import annotations

import re
from datetime import date as dateType
from functools import lru_cache
from typing import Any

from openbb_bls.utils.constants import BLS_USER_AGENT

_HEADERS = {
    "User-Agent": BLS_USER_AGENT,
    "Accept": "text/html,*/*",
}

_RELEASES: tuple[dict[str, Any], ...] = (
    {
        "code": "jolts",
        "category": "national",
        "title": "Job Openings and Labor Turnover Survey (JOLTS) — National",
        "frequency": "monthly",
        "news_release_url": "https://www.bls.gov/news.release/jolts.toc.htm",
        "pdf_url": "https://www.bls.gov/news.release/pdf/jolts.pdf",
        "toc_url": "https://www.bls.gov/news.release/jolts.toc.htm",
        "tech_notes_url": "https://www.bls.gov/news.release/jolts.tn.htm",
        "supplemental_toc_url": "https://www.bls.gov/web/jolts.supp.toc.htm",
        "archive_index_url": "https://www.bls.gov/bls/news-release/jolts.htm",
    },
    {
        "code": "jltst",
        "category": "state",
        "title": "JOLTS — State estimates",
        "frequency": "quarterly",
        "news_release_url": "https://www.bls.gov/news.release/jltst.toc.htm",
        "pdf_url": "https://www.bls.gov/news.release/pdf/jltst.pdf",
        "toc_url": "https://www.bls.gov/news.release/jltst.toc.htm",
        "tech_notes_url": "https://www.bls.gov/news.release/jltst.tn.htm",
        "supplemental_toc_url": "https://www.bls.gov/web/jltst.supp.toc.htm",
        "archive_index_url": "https://www.bls.gov/bls/news-release/jltst.htm",
    },
)


def _decode_html(content: bytes) -> str:
    """Decode BLS page bytes, falling back to latin-1."""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1", errors="replace")


def list_releases() -> tuple[dict[str, Any], ...]:
    """Return the two current JOLTS release entries."""
    return _RELEASES


def _abs(href: str) -> str:
    """Promote a BLS-relative href to absolute https://www.bls.gov form."""
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return f"https://www.bls.gov{href}"
    return f"https://www.bls.gov/{href}"


def _resolve_relative(base_dir: str, href: str) -> str:
    """Resolve a JOLTS supp-TOC ``../web/...`` relative href."""
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


_SUPP_LABEL_TRAILER_RE = re.compile(
    r"\s*\(?\s*(?:HTML|PDF|XLSX|TXT|CSV)\s*\)?\s*$", re.IGNORECASE
)


@lru_cache(maxsize=4)
def scrape_supplemental_files(supp_toc_url: str) -> tuple[dict[str, Any], ...]:
    """Return every file listed on a JOLTS supplemental TOC page."""
    import requests
    from bs4 import BeautifulSoup

    resp = requests.get(supp_toc_url, headers=_HEADERS, timeout=30)
    if resp.status_code != 200:
        return ()
    soup = BeautifulSoup(_decode_html(resp.content), "lxml")
    base_dir = supp_toc_url.rsplit("/", 1)[0]
    out: list[dict[str, Any]] = []
    seen: set[str] = set()

    label_for_url: dict[str, str] = {}
    for li in soup.find_all(["li", "p"]):
        full_text = " ".join(li.get_text(" ", strip=True).split())
        anchors = li.find_all("a", href=True)
        for anchor in anchors:
            href = str(anchor["href"]).strip()
            if not href.lower().endswith((".xlsx", ".pdf", ".txt", ".csv")):
                continue
            url = _resolve_relative(base_dir, href)
            link_text = " ".join(anchor.get_text(" ", strip=True).split())
            stripped = full_text
            while True:
                cleaned = _SUPP_LABEL_TRAILER_RE.sub("", stripped).rstrip(" -—:|")
                if cleaned == stripped:
                    break
                stripped = cleaned
            if link_text and stripped.endswith(link_text):
                stripped = stripped[: -len(link_text)].rstrip(" -—:|")
            label_for_url.setdefault(url, stripped or link_text)

    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"]).strip()
        if not href.lower().endswith((".xlsx", ".pdf", ".txt", ".csv")):
            continue
        url = _resolve_relative(base_dir, href)
        if url in seen:
            continue
        seen.add(url)
        filename = url.rsplit("/", 1)[-1]
        label = label_for_url.get(url)
        if not label or label.upper() in ("XLSX", "PDF", "TXT", "CSV"):
            stem = filename.rsplit(".", 1)[0].replace("-", " ").replace("_", " ")
            label = stem.title()
        out.append(
            {
                "name": label,
                "url": url,
                "format": filename.rsplit(".", 1)[-1].lower(),
            }
        )
    return tuple(out)


_ARCHIVE_HREF_RE = re.compile(
    r"/news\.release/archives/(?P<code>[a-z0-9]+)_"
    r"(?P<m>\d{2})(?P<d>\d{2})(?P<y>\d{4})\.(?P<ext>htm|html|pdf|xlsx|txt)$",
    re.IGNORECASE,
)


_LINK_LABEL_TRAILER_RE = re.compile(
    r"\s*\(\s*(?:HTML|PDF|XLSX|TXT)\s*\)\s*", re.IGNORECASE
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

    seen: set[tuple[str, str]] = set()
    out: list[dict[str, Any]] = []
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href") or "")
        match = _ARCHIVE_HREF_RE.search(href)
        if not match:
            continue
        code = match.group("code").lower()
        try:
            release_date = dateType(
                int(match.group("y")),
                int(match.group("m")),
                int(match.group("d")),
            )
        except ValueError:
            continue
        key = (code, match.group(0))
        if key in seen:
            continue
        seen.add(key)

        anchor_text = " ".join(anchor.get_text(" ", strip=True).split())
        title: str | None = None
        if anchor_text and anchor_text.upper() not in ("HTML", "PDF", "XLSX", "TXT"):
            title = anchor_text
        else:
            parent = anchor.parent
            for _ in range(3):
                if parent is None or parent.name in (None, "body", "html"):
                    break
                parent_text = " ".join(parent.get_text(" ", strip=True).split())
                stripped = _LINK_LABEL_TRAILER_RE.sub(" ", parent_text).strip()
                if stripped and stripped.upper() not in (
                    "HTML",
                    "PDF",
                    "XLSX",
                    "TXT",
                ):
                    title = stripped
                    break
                parent = parent.parent

        out.append(
            {
                "code": code,
                "url": _abs(href),
                "format": match.group("ext").lower(),
                "date": release_date,
                "title": title,
            }
        )
    return tuple(out)


_ARCHIVED_SUPP_INDEX: dict[str, str] = {
    "jolts": "https://www.bls.gov/jlt/jolts-archived-supplemental.htm",
    "jltst": "https://www.bls.gov/jlt/jltst-archived-supplemental.htm",
}

_MONTH_TOKEN_TO_NUM = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}

_ARCHIVED_SUPP_TOC_HREF_RE = re.compile(
    r"/jlt/(?:jolts|jltst)[-_]"
    r"(?P<m>[a-z]+)(?P<y>\d{4})[-_]supp[-_]toc\.htm$",
    re.IGNORECASE,
)


@lru_cache(maxsize=4)
def scrape_archived_supplemental_index(
    code: str,
) -> tuple[dict[str, Any], ...]:
    """Return the per-month archived supplemental TOC entries for ``code``."""
    code_norm = code.lower()
    index_url = _ARCHIVED_SUPP_INDEX.get(code_norm)
    if index_url is None:
        return ()

    import requests
    from bs4 import BeautifulSoup

    resp = requests.get(index_url, headers=_HEADERS, timeout=30)
    if resp.status_code != 200:
        return ()
    soup = BeautifulSoup(_decode_html(resp.content), "lxml")
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"]).strip()
        match = _ARCHIVED_SUPP_TOC_HREF_RE.search(href)
        if match is None:
            continue
        url = _abs(href)
        if url in seen:
            continue
        seen.add(url)
        month_token = match.group("m").lower()
        year = int(match.group("y"))
        month = _MONTH_TOKEN_TO_NUM.get(month_token)
        if month is None:
            continue
        label_text = " ".join(anchor.get_text(" ", strip=True).split())
        if not label_text:
            label_text = f"{month_token.title()} {year}"
        out.append(
            {
                "code": code_norm,
                "date": dateType(year, month, 1),
                "toc_url": url,
                "month_label": label_text,
            }
        )
    out.sort(key=lambda e: e["date"], reverse=True)
    return tuple(out)


@lru_cache(maxsize=4)
def scrape_archive(code: str) -> tuple[dict[str, Any], ...]:
    """Return archived release entries for ``code``, deduped by date."""
    release = next((r for r in _RELEASES if r["code"] == code.lower()), None)
    if release is None:
        return ()
    all_entries = _scrape_archive_page(release["archive_index_url"])
    matches = [e for e in all_entries if e["code"] == release["code"]]

    by_date: dict[dateType, dict[str, Any]] = {}
    for entry in matches:
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
        elif entry["format"] in ("htm", "html"):
            slot["html_url"] = entry["url"]

    return tuple(sorted(by_date.values(), key=lambda e: e["date"], reverse=True))
