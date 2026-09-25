"""Fetchers/parsers for ECB data published outside the SDMX API."""

from __future__ import annotations

import re
from datetime import date as dateType
from typing import cast

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

_CHROME_TAGS = (
    "script",
    "style",
    "noscript",
    "form",
    "iframe",
    "nav",
    "header",
    "footer",
    "aside",
    "button",
)
_CHROME_CLASSES = {
    "print-hidden",
    "related-topics",
    "address-box",
    "breadcrumb",
    "cookieconsent",
    "ecb-shares",
    "loading",
}
_ARTICLE_CSS = (
    "body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0 auto;"
    "max-width:56rem;padding:1.5rem 2rem;background:#fff;color:#1d1d1f;"
    "line-height:1.6}"
    "h1{font-size:1.6rem;line-height:1.25}h2{font-size:1.25rem}"
    "img{max-width:100%;height:auto}figure{margin:1rem 0}"
    "table{border-collapse:collapse;width:100%}"
    "td,th{border:1px solid #d5d9e2;padding:.3rem .5rem}"
    "a{color:#003299}.title .category{color:#5c6570;font-size:.8rem}"
)


def _article_to_html(html: str, base_url: str) -> str:
    """Return an ECB release page's article content as a standalone document."""
    from urllib.parse import urljoin

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    if main is None:
        return ""
    for tag in main.find_all(_CHROME_TAGS):
        tag.decompose()
    for tag in list(main.find_all(True)):
        classes = {str(cls).lower() for cls in (tag.attrs or {}).get("class") or []}
        if classes & _CHROME_CLASSES:
            tag.decompose()
    for tag in main.find_all(href=True):
        tag["href"] = urljoin(base_url, str(tag["href"]))
        tag["target"] = "_blank"
        tag["rel"] = "noopener"
    for tag in main.find_all(src=True):
        tag["src"] = urljoin(base_url, str(tag["src"]))
    body = main.decode_contents().strip()
    if not body:
        return ""
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        f"<style>{_ARTICLE_CSS}</style></head><body>{body}</body></html>"
    )


_INFO_CSS = (
    "body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;"
    "padding:1.25rem 1.5rem;background:#0f1116;color:#e6e6e6;line-height:1.5}"
    "h1{font-size:1.35rem;margin:0 0 .25rem}"
    "h2{font-size:1.05rem;margin:1.4rem 0 .4rem;color:#8ab4ff;"
    "border-bottom:1px solid #2a2f3a;padding-bottom:.2rem}"
    ".badge{font-size:.7rem;background:#2a2f3a;color:#9aa0aa;padding:.15rem .4rem;"
    "border-radius:.3rem;vertical-align:middle;margin-left:.4rem}"
    ".meta{color:#9aa0aa;font-size:.85rem;margin:.15rem 0 .6rem}"
    "a{color:#8ab4ff}p{margin:.4rem 0}"
)


def render_dataflow_info(
    dataflow_id: str, info: dict, concepts: list[str] | None = None
) -> str:
    """Render a dataflow's cached ``data-information`` into an HTML page."""
    from html import escape

    title = info.get("title") or dataflow_id
    parts = [
        f'<h1>{escape(title)}<span class="badge">{escape(dataflow_id)}</span></h1>'
    ]
    if concepts:
        parts.append(
            '<p class="meta">Topics: ' + ", ".join(escape(c) for c in concepts) + "</p>"
        )
    catalogue = info.get("catalogue")
    if catalogue:
        parts.append(
            f'<p class="meta"><a href="{escape(catalogue)}">'
            "Download the full series catalogue (CSV, zipped)</a></p>"
        )
    for field in info.get("fields") or []:
        parts.append(f"<h2>{escape(field.get('label') or '')}</h2>")
        parts.append(f"<div>{field.get('html') or ''}</div>")
    body = "".join(parts)
    return (
        f'<!doctype html><html><head><meta charset="utf-8">'
        f"<style>{_INFO_CSS}</style></head><body><article>{body}</article></body></html>"
    )


async def fetch_release_html(url: str) -> str:
    """Fetch an ECB release page and return the full page as HTML."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.scheme != "https" or (parsed.hostname or "").lower() not in RELEASE_HOSTS:
        return ""
    if parsed.path.lower().endswith(".pdf"):
        return await _embed_pdf(url)
    try:
        html = await _aget_text(url)
    except Exception:  # noqa: BLE001
        return ""
    return _article_to_html(html, url)


async def _embed_pdf(url: str) -> str:
    """Fetch an ECB PDF and embed it as a base64 data URI."""
    import base64

    try:
        status, raw = await _aget_bytes(url)
    except Exception:  # noqa: BLE001
        return ""
    if status != 200 or not raw:
        return ""
    encoded = base64.b64encode(raw).decode("ascii")
    return (
        '<html><body style="margin:0;height:100vh">'
        f'<embed src="data:application/pdf;base64,{encoded}"'
        ' type="application/pdf" style="width:100%;height:100%;border:0"/>'
        "</body></html>"
    )


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
        link = re.sub(r"(https?://[^/]+)//+", r"\1/", _t("link"))
        items.append(
            {
                "date": stamp.isoformat() if stamp else None,
                "title": _t("title"),
                "url": link,
                "category": feed,
            }
        )
    return items


_STATSCAL_URL = "https://www.ecb.europa.eu/press/calendars/statscal/html/index.en.html"
_DT_DD_RE = re.compile(r"<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>", re.S)
_DATE_RE = re.compile(r"(\d{2})/(\d{2})/(\d{4})\s+(\d{2}):(\d{2})")
_DATASET_RE = re.compile(r"\(Dataset:\s*([^)]+)\)")
_REFPERIOD_RE = re.compile(r"Reference period:\s*([^.]+?)(?:\s*Includes|\s*$)")


def _strip_html(text: str) -> str:
    """Strip tags and collapse whitespace."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", text)).strip()


async def fetch_release_calendar() -> list[dict]:
    """Scrape the ECB statistical release calendar into calendar rows."""
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


_EA_BASE = "https://www.ecb.europa.eu/paym/coll/assets/html/dla/ea_MID"
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
    """Download the eligible marketable assets list for the nearest available day."""
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
