"""Unit tests for ``openbb_sec.models.rss_litigation``."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_sec.models import rss_litigation as mod
from openbb_sec.models.rss_litigation import SecRssLitigationFetcher

_RSS = """<?xml version="1.0"?>
<rss><channel>
<item>
<title>SEC  v.  Example Corp &amp; Others</title>
<link>https://www.sec.gov/litigation/litreleases/2026/lr-26562.htm</link>
<description>The SEC charged Example Corp.</description>
<pubDate>Mon, 08 Jun 2026 10:14:13 -0400</pubDate>
<dc:creator>LR-26562</dc:creator>
</item>
</channel></rss>"""

_BODY = (
    "<html><body><script>x</script>"
    "<article><p>Full litigation text.</p></article></body></html>"
)


def test_rss_litigation_empty_feed_raises():
    """aextract_data raises OpenBBError when the feed returns nothing."""
    query = SecRssLitigationFetcher.transform_query({})
    with patch(
        "openbb_core.provider.utils.helpers.amake_request",
        AsyncMock(return_value=None),
    ):
        with pytest.raises(OpenBBError):
            asyncio.run(SecRssLitigationFetcher.aextract_data(query, None))


def test_rss_litigation_happy_path():
    """The feed is parsed, the full text is fetched, and the model validates."""

    def _amake(url, **_):
        return _RSS if str(url).endswith("/rss") else _BODY

    query = SecRssLitigationFetcher.transform_query({"limit": 1})
    with patch(
        "openbb_core.provider.utils.helpers.amake_request",
        AsyncMock(side_effect=_amake),
    ):
        rows = asyncio.run(SecRssLitigationFetcher.aextract_data(query, None))

    assert len(rows) == 1
    assert rows[0]["title"] == "SEC v. Example Corp & Others"
    assert rows[0]["id"] == "LR-26562"
    assert rows[0]["author"] is None
    assert "Full litigation text." in rows[0]["body"]

    data = SecRssLitigationFetcher.transform_data(query, rows)
    assert data[0].title == "SEC v. Example Corp & Others"
    assert str(data[0].date).startswith("2026-06-08")


def test_rss_litigation_body_failure_falls_back_to_excerpt():
    """When the release page can't be fetched, body falls back to the excerpt."""

    def _amake(url, **_):
        if str(url).endswith("/rss"):
            return _RSS
        raise RuntimeError("boom")

    query = SecRssLitigationFetcher.transform_query({"limit": 1})
    with patch(
        "openbb_core.provider.utils.helpers.amake_request",
        AsyncMock(side_effect=_amake),
    ):
        rows = asyncio.run(SecRssLitigationFetcher.aextract_data(query, None))

    assert rows[0]["body"] == rows[0]["excerpt"] == "The SEC charged Example Corp."


def test_text_callback_reads_response_text():
    """_text_callback returns the response body text."""
    response = SimpleNamespace(text=AsyncMock(return_value="hello"))
    assert asyncio.run(mod._text_callback(response, None)) == "hello"


def test_fetch_body_returns_none_when_empty():
    """_fetch_body returns None when the release page has no content."""
    with patch(
        "openbb_core.provider.utils.helpers.amake_request",
        AsyncMock(return_value=None),
    ):
        assert asyncio.run(mod._fetch_body("https://x")) is None


def test_fetch_body_returns_none_without_main_content():
    """_fetch_body returns None when no article/main/body element is present."""
    with patch(
        "openbb_core.provider.utils.helpers.amake_request",
        AsyncMock(return_value="bare text"),
    ):
        assert asyncio.run(mod._fetch_body("https://x")) is None


def test_unparseable_dates_become_none():
    """Missing or malformed pubDate values are coerced to None."""
    rss = (
        "<?xml version='1.0'?><rss><channel>"
        "<item><title>A</title><link>https://x/lr-1.htm</link>"
        "<description>d</description><pubDate>garbage</pubDate></item>"
        "<item><title>B</title><link>https://x/lr-2.htm</link>"
        "<description>d</description></item>"
        "</channel></rss>"
    )

    def _amake(url, **_):
        return rss if str(url).endswith("/rss") else None

    query = SecRssLitigationFetcher.transform_query({"limit": 2})
    with patch(
        "openbb_core.provider.utils.helpers.amake_request",
        AsyncMock(side_effect=_amake),
    ):
        rows = asyncio.run(SecRssLitigationFetcher.aextract_data(query, None))
    assert [r["date"] for r in rows] == [None, None]
