"""Async congress.gov search client for committee documents.

Adapted from the top-level ``congress_search.py`` for use inside the
openbb_congress_gov provider package.  Exposes only the async internals
so callers already running in an event loop can ``await`` directly.
"""

import asyncio
import json
import math
import re
from typing import Any, Literal

import httpx

_BASE_URL = "https://www.congress.gov/search"
_HOME_URL = "https://www.congress.gov/"

ALL_SOURCES = ["comreports", "committee-publications", "committee-meetings"]

_PAGE_SIZE = 250

Chamber = Literal["house", "senate", "joint"]

_CHAMBER_KEY: dict[str, str] = {
    "house": "house-committee",
    "senate": "senate-committee",
    "joint": "joint-committee",
}

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "sec-ch-ua-mobile": "?0",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}

_HTML_ENTITIES = {
    "&mdash;": "\u2014",
    "&ndash;": "\u2013",
    "&amp;": "&",
    "&nbsp;": " ",
    "&lt;": "<",
    "&gt;": ">",
    "&quot;": '"',
    "&#39;": "'",
    "&#039;": "'",
}


def _decode(text: str) -> str:
    for ent, char in _HTML_ENTITIES.items():
        text = text.replace(ent, char)
    return re.sub(r"\s+", " ", text).strip()


def _parse_page(html: str) -> list[dict[str, Any]]:
    sec = re.search(
        r'<ol[^>]*class="[^"]*results[^"]*"[^>]*>(.*?)</ol>', html, re.DOTALL
    )
    if not sec:
        return []

    raw_items = re.findall(r"<li[^>]*>(.*?)</li>", sec.group(1), re.DOTALL)
    results: list[dict[str, Any]] = []

    for item in raw_items[::2]:
        vi = re.search(r'class="visualIndicator">([^<]+)<', item)
        if not vi:
            continue
        doc_type = vi.group(1).strip()

        href_m = re.search(r'class="result-heading".*?href="(/[^"?]+)', item, re.DOTALL)
        url = f"https://www.congress.gov{href_m.group(1)}" if href_m else ""
        if not url:
            continue

        heading_m = re.search(r'class="result-heading">(.*?)</span>', item, re.DOTALL)
        heading = (
            _decode(re.sub(r"<[^>]+>", " ", heading_m.group(1))) if heading_m else ""
        )

        title_m = re.search(r'class="result-title">(.*?)</span>', item, re.DOTALL)
        title = _decode(re.sub(r"<[^>]+>", " ", title_m.group(1))) if title_m else ""

        doc: dict[str, Any] = {
            "type": doc_type,
            "url": url,
            "heading": heading,
        }
        if title:
            doc["title"] = title

        for span in re.findall(r'class="result-item">(.*?)</span>', item, re.DOTALL):
            key_m = re.search(r"<strong>([^<]+):</strong>(.*)", span, re.DOTALL)
            if key_m:
                key = key_m.group(1).strip()
                val = _decode(re.sub(r"<[^>]+>", " ", key_m.group(2)))
                doc[key] = val
            else:
                text = _decode(re.sub(r"<[^>]+>", " ", span))
                if text:
                    doc.setdefault("date", text)

        results.append(doc)

    return results


def _get_total(html: str) -> int:
    m = re.search(r"[\d,]+\s*-\s*[\d,]+\s*of\s*([\d,]+)", html)
    return int(m.group(1).replace(",", "")) if m else 0


async def _fetch_page(
    session: httpx.AsyncClient,
    q: str,
    page: int,
    sem: asyncio.Semaphore,
) -> str:
    async with sem:
        r = await session.get(
            _BASE_URL,
            params={"q": q, "pageSize": str(_PAGE_SIZE), "page": str(page)},
        )
        r.raise_for_status()
        return r.text


async def _run_q(
    q: str,
    congress: int,
    max_concurrent: int,
) -> list[dict[str, Any]]:
    sem = asyncio.Semaphore(max_concurrent)

    async with httpx.AsyncClient(
        headers=_HEADERS, follow_redirects=True, timeout=30
    ) as session:
        await session.get(_HOME_URL)
        await asyncio.sleep(0.4)

        page1_html = await _fetch_page(session, q, 1, sem)
        total = _get_total(page1_html)
        docs = _parse_page(page1_html)

        if total > _PAGE_SIZE:
            n_pages = math.ceil(total / _PAGE_SIZE)
            remaining = await asyncio.gather(
                *[_fetch_page(session, q, p, sem) for p in range(2, n_pages + 1)],
                return_exceptions=True,
            )
            for result in remaining:
                if isinstance(result, str):
                    docs.extend(_parse_page(result))

    for d in docs:
        d["congress"] = congress

    return docs


async def search_async(
    congress: int,
    sources: list[str],
    committee: str | None = None,
    chamber: Chamber | None = None,
    max_concurrent: int = 4,
) -> list[dict[str, Any]]:
    """Search congress.gov for committee documents (async).

    Parameters
    ----------
    congress
        Congress number (e.g. 119).
    sources
        Document-type keys, subset of ``ALL_SOURCES``.
    committee
        Committee display name (e.g. "Armed Services").
    chamber
        "house", "senate", or "joint".  Required when *committee* is set
        and the same name exists in multiple chambers.
    max_concurrent
        Max parallel HTTP requests.

    Returns
    -------
    list[dict]
        Each dict has ``type``, ``url``, ``heading``, and optional
        ``title``, ``Committee``, ``date``, etc.
    """
    q_dict: dict[str, Any] = {"source": sources, "congress": str(congress)}
    if committee is not None:
        if chamber is not None:
            q_dict[_CHAMBER_KEY[chamber]] = committee
        else:
            seen_urls: set[str] = set()
            merged: list[dict[str, Any]] = []
            for ch in ("house", "senate", "joint"):
                sub_q = {**q_dict, _CHAMBER_KEY[ch]: committee}
                sub_docs = await _run_q(json.dumps(sub_q), congress, max_concurrent)
                for d in sub_docs:
                    if d["url"] not in seen_urls:
                        seen_urls.add(d["url"])
                        merged.append(d)
            return merged

    return await _run_q(json.dumps(q_dict), congress, max_concurrent)
