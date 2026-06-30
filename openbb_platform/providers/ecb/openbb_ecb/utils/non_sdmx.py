"""Fetchers/parsers for ECB data published outside the SDMX API.

Three sources, each isolated here so a website change is a one-file fix:
  * RSS feeds (press releases, publications, blog) — stable XML.
  * The statistical release calendar (statscal) — HTML scrape (fragile).
  * Eurosystem eligible marketable assets (collateral) — MID bulk CSV.
"""

from __future__ import annotations

import re
from datetime import date as dateType
from typing import cast

# --- RSS feeds (releases / documents) --------------------------------------

RSS_FEEDS: dict[str, str] = {
    "press_releases": "https://www.ecb.europa.eu/rss/press.html",
    "publications": "https://www.ecb.europa.eu/rss/pub.html",
    "blog": "https://www.ecb.europa.eu/rss/blog.html",
}


async def _aget_text(url: str) -> str:
    """GET a URL and return decoded text."""
    from openbb_core.provider.utils.helpers import amake_request

    async def _cb(response, _):
        return await response.text()

    return cast(
        str,
        await amake_request(
            url, headers={"User-Agent": "OpenBB Platform - ECB"}, response_callback=_cb
        ),
    )


async def _aget_bytes(url: str) -> tuple[int, bytes]:
    """GET a URL and return ``(status, raw bytes)``."""
    from openbb_core.provider.utils.helpers import amake_request

    async def _cb(response, _):
        return response.status, await response.read()

    return cast(
        "tuple[int, bytes]",
        await amake_request(
            url, headers={"User-Agent": "OpenBB Platform - ECB"}, response_callback=_cb
        ),
    )


RELEASE_HOSTS = {"www.ecb.europa.eu", "ecb.europa.eu"}


def _article_to_markdown(html: str, base_url: str) -> str:
    """Render an ECB article page's ``<main>`` content as markdown.

    Image and link URLs are resolved to **absolute** against the page URL — a
    page-relative chart ``src`` (e.g. ``blog.../img1.jpeg``) resolves to the
    page's folder, a root-relative ``/shared/...`` to the origin — so the images
    render inline in the newsfeed. Returns "" when there is no article body.
    """
    from urllib.parse import urljoin

    from bs4 import BeautifulSoup
    from markdownify import markdownify

    main = BeautifulSoup(html, "html.parser").find("main")
    if main is None:
        return ""
    for tag in main.select("script, style, nav, header, footer, form, button, svg"):
        tag.decompose()
    for img in main.find_all("img"):
        src = img.get("src")
        if src:
            img["src"] = urljoin(base_url, str(src))
    for anchor in main.find_all("a"):
        href = anchor.get("href")
        if href:
            anchor["href"] = urljoin(base_url, str(href))
    markdown = markdownify(str(main), heading_style="ATX", strip=["svg"])
    return re.sub(r"\n{3,}", "\n\n", markdown).strip()


async def fetch_release_body(url: str) -> str:
    """Fetch an ECB release page and return its article body as markdown.

    Validated to ecb.europa.eu (SSRF guard). Returns "" for any non-ECB URL or
    when the page can't be fetched/parsed, so one bad article never empties the
    feed.
    """
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.scheme != "https" or (parsed.hostname or "").lower() not in RELEASE_HOSTS:
        return ""
    try:
        html = await _aget_text(url)
    except Exception:  # noqa: BLE001 - a bad page shouldn't break the feed
        return ""
    return _article_to_markdown(html, url)


def release_excerpt(body: str, limit: int = 280) -> str:
    """Return the first substantial paragraph of a markdown body, truncated.

    Skips the page's preamble — nav bullets, the title/section headings, the date,
    the byline, images and tables — to land on the first real sentence.
    """
    skip = ("![", "#", "|", "*", "-", ">", "By ")
    for line in body.splitlines():
        text = line.strip()
        if len(text) >= 80 and not text.startswith(skip):
            if len(text) <= limit:
                return text
            return text[:limit].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
    return ""


async def fetch_rss_items(feed: str) -> list[dict]:
    """Fetch and parse an ECB RSS feed into ``[{date, title, url}]``."""
    from email.utils import parsedate_to_datetime

    from defusedxml import ElementTree as DET

    url = RSS_FEEDS.get(feed, feed)
    text = await _aget_text(url)
    root = DET.fromstring(text.encode("utf-8") if isinstance(text, str) else text)
    items: list[dict] = []
    for item in root.findall(".//item"):

        def _t(tag: str) -> str:
            el = item.find(tag)
            return (el.text or "").strip() if el is not None else ""

        pub = _t("pubDate")
        try:
            stamp = parsedate_to_datetime(pub) if pub else None
        except (TypeError, ValueError):
            stamp = None
        items.append(
            {
                "date": stamp.isoformat() if stamp else None,
                "title": _t("title"),
                "url": _t("link"),
                "category": feed,
            }
        )
    return items


# --- Statistical release calendar (statscal) -------------------------------

_STATSCAL_URL = "https://www.ecb.europa.eu/press/calendars/statscal/html/index.en.html"
_DT_DD_RE = re.compile(r"<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>", re.S)
_DATE_RE = re.compile(r"(\d{2})/(\d{2})/(\d{4})\s+(\d{2}):(\d{2})")
_DATASET_RE = re.compile(r"\(Dataset:\s*([^)]+)\)")
_REFPERIOD_RE = re.compile(r"Reference period:\s*([^.]+?)(?:\s*Includes|\s*$)")


def _strip_html(text: str) -> str:
    """Strip tags and collapse whitespace."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", text)).strip()


async def fetch_release_calendar() -> list[dict]:
    """Scrape the ECB statistical release calendar into calendar rows.

    Fragile by nature (HTML scrape); the parsing is confined to this function.
    """
    html = await _aget_text(_STATSCAL_URL)
    rows: list[dict] = []
    for dt_raw, dd_raw in _DT_DD_RE.findall(html):
        dt_text = _strip_html(dt_raw)
        dd_text = _strip_html(dd_raw)
        m = _DATE_RE.search(dt_text)
        if not m:
            continue
        day, month, year, hour, minute = m.groups()
        dataset = _DATASET_RE.search(dd_text)
        ref = _REFPERIOD_RE.search(dd_text)
        event = _DATASET_RE.split(dd_text)[0].strip().rstrip("(").strip()
        rows.append(
            {
                "date": f"{year}-{month}-{day}T{hour}:{minute}:00",
                "country": "Euro Area",
                "category": dataset.group(1).strip() if dataset else None,
                "event": event or dd_text,
                "reference_period": ref.group(1).strip() if ref else None,
                "source": "European Central Bank",
            }
        )
    return rows


# --- Eurosystem eligible assets (collateral) -------------------------------

_EA_BASE = "https://www.ecb.europa.eu/paym/coll/assets/html/dla/ea_MID"
# CSV column -> standardized field name.
_EA_FIELDS: dict[str, str] = {
    "ISIN_CODE": "isin",
    "HAIRCUT_CATEGORY": "haircut_category",
    "TYPE": "asset_type",
    "REFERENCE_MARKET": "reference_market",
    "DENOMINATION": "currency",
    "ISSUANCE_DATE": "issuance_date",
    "MATURITY_DATE": "maturity_date",
    "COUPON_RATE (%)": "coupon_rate",
    "COUPON_DEFINITION": "coupon_definition",
    "ISSUER_NAME": "issuer_name",
    "ISSUER_RESIDENCE": "issuer_residence",
    "ISSUER_GROUP": "issuer_group",
    "GUARANTOR_NAME": "guarantor_name",
    "GUARANTOR_RESIDENCE": "guarantor_residence",
    "HAIRCUT": "haircut",
    "HAIRCUT_OWN_USE": "haircut_own_use",
    "POTENTIALLY_OWN_USABLE_COVERED_BOND": "covered_bond",
    "CLIMATE_FACTOR": "climate_factor",
}


def _parse_ea_date(value: str) -> str | None:
    """Parse a ``DD/MM/YYYY HH:MM:SS`` date to ISO ``YYYY-MM-DD``."""
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", value or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def _parse_eligible_assets_csv(raw: bytes) -> list[dict]:
    """Parse the UTF-16, tab-delimited eligible-assets CSV into records."""
    import csv

    text = raw.decode("utf-16", errors="replace")
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    rows: list[dict] = []
    for row in reader:
        record: dict = {}
        for col, field in _EA_FIELDS.items():
            value = (row.get(col) or "").strip()
            if not value:
                continue
            if field in ("issuance_date", "maturity_date"):
                record[field] = _parse_ea_date(value)
            elif field in (
                "coupon_rate",
                "haircut",
                "haircut_own_use",
                "climate_factor",
            ):
                try:
                    record[field] = float(value)
                except ValueError:
                    record[field] = None
            else:
                record[field] = value
        if record.get("isin"):
            rows.append(record)
    return rows


async def fetch_eligible_assets(
    snapshot_date: dateType | None,
) -> tuple[str, list[dict]]:
    """Download the eligible marketable assets list for the nearest available day.

    Returns ``(file_date_iso, records)``. Walks back up to 7 days from
    ``snapshot_date`` (or today) to skip non-TARGET days.
    """
    import contextlib
    import gzip
    from datetime import timedelta

    from openbb_core.app.model.abstract.error import OpenBBError

    base_date = snapshot_date or dateType.today()
    for back in range(8):
        day = base_date - timedelta(days=back)
        stamp = day.strftime("%y%m%d")
        url = f"{_EA_BASE}/ea_csv_{stamp}.csv.gz"
        status, raw = await _aget_bytes(url)
        if status == 200 and raw:
            with contextlib.suppress(OSError, EOFError):
                raw = gzip.decompress(raw)
            return day.isoformat(), _parse_eligible_assets_csv(raw)
    raise OpenBBError(
        "No eligible-assets file found near "
        f"{base_date.isoformat()} (checked the prior 7 days)."
    )
