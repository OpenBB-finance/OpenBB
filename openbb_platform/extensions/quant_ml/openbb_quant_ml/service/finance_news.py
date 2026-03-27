"""Finance news service — Yahoo Finance RSS + fallback scraping.

Uses the public Yahoo Finance RSS feed which does not require API keys
and has much more lenient rate limits than the REST API that yfinance uses.
"""

from __future__ import annotations

import logging
import threading
import xml.etree.ElementTree as ET  # noqa: N817
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.request import Request, urlopen

from cachetools import TTLCache

LOGGER = logging.getLogger(__name__)

_NEWS_CACHE: TTLCache[str, dict[str, Any]] = TTLCache(maxsize=300, ttl=600)
_CACHE_LOCK = threading.RLock()

_YF_RSS_URL = "https://finance.yahoo.com/rss/headline?s={symbol}"
_YF_MARKET_RSS_URL = "https://finance.yahoo.com/rss/topstories"
_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def _fetch_rss(url: str, timeout: int = 10) -> list[dict[str, Any]]:
    """Fetch and parse a Yahoo Finance RSS feed URL."""
    req = Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310
            raw = resp.read()
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("RSS fetch failed for %s: %s", url, exc)
        return []

    try:
        root = ET.fromstring(raw)  # noqa: S314
    except ET.ParseError as exc:
        LOGGER.warning("RSS parse failed for %s: %s", url, exc)
        return []

    items: list[dict[str, Any]] = []
    for item_el in root.iter("item"):
        title = (item_el.findtext("title") or "").strip()
        link = (item_el.findtext("link") or "").strip()
        description = (item_el.findtext("description") or "").strip()
        pub_date_str = (item_el.findtext("pubDate") or "").strip()
        source = (item_el.findtext("source") or "Yahoo Finance").strip()

        published_at = ""
        if pub_date_str:
            try:
                dt = parsedate_to_datetime(pub_date_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                published_at = dt.isoformat()
            except Exception:  # noqa: BLE001
                published_at = pub_date_str

        if not title:
            continue

        items.append({
            "id": link or title,
            "title": title,
            "summary": description if description != title else "",
            "published_at": published_at,
            "source": source,
            "url": link,
            "thumbnail": "",
            "is_breaking": False,
        })

    return items


def get_stock_news(
    symbol: str,
    days: int = 7,
    limit: int = 30,
) -> dict[str, Any]:
    """Fetch news for a single stock symbol via Yahoo Finance RSS.

    Results are cached for 10 minutes per symbol.
    """
    symbol = symbol.upper().strip()
    cache_key = f"stock_news:{symbol}:{days}"
    with _CACHE_LOCK:
        cached = _NEWS_CACHE.get(cache_key)
        if cached is not None:
            return cached

    url = _YF_RSS_URL.format(symbol=symbol)
    items = _fetch_rss(url)

    # Filter by days
    now = datetime.now(tz=timezone.utc)
    filtered: list[dict[str, Any]] = []
    for item in items:
        if not item["published_at"]:
            filtered.append(item)
            continue
        try:
            pub_dt = datetime.fromisoformat(item["published_at"])
            if pub_dt.tzinfo is None:
                pub_dt = pub_dt.replace(tzinfo=timezone.utc)
            delta = now - pub_dt
            if delta.days <= days:
                filtered.append(item)
        except ValueError:
            filtered.append(item)

    filtered = filtered[:limit]

    result: dict[str, Any] = {
        "symbol": symbol,
        "news_items": filtered,
        "total": len(filtered),
    }
    with _CACHE_LOCK:
        _NEWS_CACHE[cache_key] = result
    return result


def get_market_news(limit: int = 20) -> dict[str, Any]:
    """Fetch broad market news via Yahoo Finance top stories RSS.

    Results are cached for 10 minutes.
    """
    cache_key = "market_news:all"
    with _CACHE_LOCK:
        cached = _NEWS_CACHE.get(cache_key)
        if cached is not None:
            return cached

    items = _fetch_rss(_YF_MARKET_RSS_URL)

    # Mark breaking-style headlines
    for item in items[:5]:
        title_upper = item["title"].upper()
        if any(kw in title_upper for kw in ("SURGES", "PLUNGES", "CRASHES", "SOARS", "HALTED", "BREAKING")):
            item["is_breaking"] = True

    capped = items[:limit]

    result: dict[str, Any] = {"news_items": capped, "total": len(capped)}
    with _CACHE_LOCK:
        _NEWS_CACHE[cache_key] = result
    return result
