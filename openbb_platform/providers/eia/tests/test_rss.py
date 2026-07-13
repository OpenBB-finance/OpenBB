"""Tests for the EIA RSS feed widget and helpers."""

import time

import aiohttp
import feedparser
import pytest

from openbb_us_eia import rss as rss_widget
from openbb_us_eia.utils import rss

SAMPLE_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:eia="https://www.eia.gov/rss/">
  <channel>
    <title>Sample Feed</title>
    <item>
      <title>First Article</title>
      <link>https://www.eia.gov/todayinenergy/detail.php?id=1</link>
      <description>&lt;p&gt;A short summary.&lt;/p&gt;</description>
      <pubDate>Mon, 19 May 2026 13:00:00 GMT</pubDate>
      <author>Jane Doe</author>
    </item>
    <item>
      <title>Second Article</title>
      <link>detail.php?id=2</link>
      <description>Plain text summary.</description>
      <pubDate>Mon, 19 May 2026 12:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""

PRESENTATION_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:eia="https://www.eia.gov/rss/">
  <channel>
    <title>Presentations</title>
    <item>
      <title>Deck</title>
      <link>https://www.eia.gov/pressroom/index.php</link>
      <description>A talk.</description>
      <pubDate>Wed, 04 Mar 2026 13:00:00 GMT</pubDate>
      <eia:pdf>/pressroom/presentations/deck.pdf</eia:pdf>
      <eia:ppt>/pressroom/presentations/deck.pptx</eia:ppt>
      <eia:subject>Energy</eia:subject>
      <eia:presentedby>A. Person</eia:presentedby>
    </item>
    <item>
      <title>Video Talk</title>
      <link>https://www.youtube.com/watch?v=abc123</link>
      <description>Recorded.</description>
      <pubDate>Tue, 03 Mar 2026 13:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Landing Page Only</title>
      <link>https://www.eia.gov/pressroom/other.php</link>
      <description>No document.</description>
      <pubDate>Mon, 02 Mar 2026 13:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""

PRICE_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Gasoline</title>
    <item>
      <title>Prices</title>
      <link>https://www.eia.gov/petroleum/gasdiesel/</link>
      <description>Summary excerpt here&lt;br/&gt;Regular Gasoline&lt;br/&gt;3.081 .. U.S.&lt;br/&gt;2.855 .. Gulf Coast&lt;br/&gt;Diesel&lt;br/&gt;3.624 .. U.S.</description>
      <pubDate>Mon, 06 Jul 2026 13:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""


class _FakeResponse:
    def __init__(self, body=b"", status=200):
        self._body = body
        self.status = status

    async def read(self):
        return self._body

    def raise_for_status(self):
        if self.status >= 400:
            raise aiohttp.ClientError(f"HTTP {self.status}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None


class _FakeSession:
    def __init__(self, results):
        self.results = list(results)
        self.calls = 0
        self.closed = False

    async def get(self, _url, **_kwargs):
        self.calls += 1
        result = self.results.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        self.closed = True


class TestRegistry:
    def test_feed_specs_complete(self):
        assert set(rss.EIA_RSS_FEEDS) == {
            "today_in_energy",
            "whats_new",
            "press_releases",
            "congressional_testimony",
            "presentations",
            "gasoline_diesel",
            "heating_oil_propane",
        }
        for spec in rss.EIA_RSS_FEEDS.values():
            assert set(spec) == {"label", "description", "url", "base", "viewer"}
            assert spec["viewer"] in ("page", "pdf", "table")

    def test_feed_choices(self):
        choices = rss.feed_choices()
        assert choices[0] == {"label": "Today in Energy", "value": "today_in_energy"}
        assert len(choices) == len(rss.EIA_RSS_FEEDS)


class TestTextHelpers:
    def test_strip_html(self):
        assert rss.strip_html("<p>A  <b>B</b>\n C</p>") == "A B C"

    def test_strip_html_empty(self):
        assert rss.strip_html("") == ""

    def test_excerpt_short_text_unchanged(self):
        assert rss.clean_excerpt("short") == "short"

    def test_excerpt_cuts_at_word_boundary(self):
        assert rss.clean_excerpt("word " * 100, limit=22) == "word word word word…"

    def test_excerpt_keeps_whitelisted_inline_markup(self):
        out = rss.clean_excerpt("<p>Crude <strong>rose</strong> 4%</p>")
        assert out == "Crude <strong>rose</strong> 4%"

    def test_excerpt_drops_unlisted_tags_but_keeps_their_text(self):
        out = rss.clean_excerpt('<a href="/x">link</a> and <em>emphasis</em>')
        assert out == "link and <em>emphasis</em>"

    def test_excerpt_discards_script_source(self):
        assert (
            rss.clean_excerpt("<script>alert(1)</script>Prices fell") == "Prices fell"
        )

    def test_excerpt_discards_style_source(self):
        assert rss.clean_excerpt("<style>p{color:red}</style>Prices fell") == (
            "Prices fell"
        )

    def test_excerpt_decodes_entities_into_markup(self):
        out = rss.clean_excerpt("CO&lt;sub&gt;2&lt;/sub&gt; &amp; NG")
        assert out == "CO<sub>2</sub> &amp; NG"

    def test_excerpt_closes_tags_left_open_by_truncation(self):
        out = rss.clean_excerpt("<strong>very long bold text to cut</strong>", limit=20)
        assert out == "<strong>very long bold text…</strong>"

    def test_excerpt_of_empty_summary(self):
        assert rss.clean_excerpt("") == ""
        assert rss.clean_excerpt(None) == ""

    def test_excerpt_stops_once_the_budget_is_exhausted(self):
        assert rss.clean_excerpt("<b>abcd</b>efgh", limit=4) == "<b>abcd</b>"

    def test_struct_time_to_iso(self):
        value = time.gmtime(0)
        assert rss.struct_time_to_iso(value) == "1970-01-01T00:00:00+00:00"

    def test_struct_time_none_returns_now(self):
        assert rss.struct_time_to_iso(None).endswith("+00:00")

    def test_escape(self):
        assert rss._escape("<a>&") == "&lt;a&gt;&amp;"
        assert rss._escape("") == ""

    def test_youtube_embed(self):
        assert (
            rss._youtube_embed("https://www.youtube.com/watch?v=abc_1-2")
            == "https://www.youtube.com/embed/abc_1-2"
        )
        assert (
            rss._youtube_embed("https://youtu.be/xyz")
            == "https://www.youtube.com/embed/xyz"
        )
        assert rss._youtube_embed("https://www.eia.gov/page") is None


class TestFetchFeed:
    @pytest.mark.asyncio
    async def test_parses_first_success(self):
        session = _FakeSession([_FakeResponse(SAMPLE_RSS)])
        parsed = await rss.fetch_feed(session, "http://feed")
        assert len(parsed.entries) == 2
        assert session.calls == 1

    @pytest.mark.asyncio
    async def test_retries_transient_failure(self):
        session = _FakeSession([aiohttp.ClientError("boom"), _FakeResponse(SAMPLE_RSS)])
        parsed = await rss.fetch_feed(session, "http://feed")
        assert len(parsed.entries) == 2
        assert session.calls == 2

    @pytest.mark.asyncio
    async def test_exhausted_retries_return_empty(self):
        session = _FakeSession([TimeoutError(), TimeoutError(), TimeoutError()])
        parsed = await rss.fetch_feed(session, "http://feed")
        assert parsed.entries == []
        assert session.calls == 3

    @pytest.mark.asyncio
    async def test_http_error_counts_as_failure(self):
        session = _FakeSession(
            [_FakeResponse(b"", status=503), _FakeResponse(SAMPLE_RSS)]
        )
        parsed = await rss.fetch_feed(session, "http://feed")
        assert len(parsed.entries) == 2


class TestRenderPriceTable:
    def test_sections_and_rows(self):
        description = (
            "Summary excerpt ignored<br/>Regular Gasoline<br/>"
            "3.081 .. U.S.<br/>2.855 .. Gulf Coast<br/>Diesel<br/>3.624 .. U.S."
        )
        out = rss.render_price_table(description)
        assert out.count("<h4>") == 2
        assert out.count("<table") == 2
        assert "<td>U.S.</td><td class=v>3.081</td>" in out

    def test_empty_description(self):
        assert rss.render_price_table("") == ""

    def test_plain_text_without_markup(self):
        out = rss.render_price_table("Header\n1.23 .. Item")
        assert "<h4>Header</h4>" in out
        assert "1.23" in out


class TestBuildFeed:
    def test_page_feed_rewrites_src_through_proxy(self):
        parsed = feedparser.parse(SAMPLE_RSS)
        data = rss.build_feed("today_in_energy", parsed, 50, "http://t/eia_proxy")
        assert data["label"] == "Today in Energy"
        first, second = data["items"]
        assert first["title"] == "First Article"
        assert first["src"] == "http://t/eia_proxy/todayinenergy/detail.php?id=1"
        assert first["url"] == "https://www.eia.gov/todayinenergy/detail.php?id=1"
        assert first["excerpt"] == "A short summary."
        assert second["author"] == "Sample Feed"
        assert second["url"] == "https://www.eia.gov/todayinenergy/detail.php?id=2"

    def test_without_proxy_keeps_original_src(self):
        parsed = feedparser.parse(SAMPLE_RSS)
        data = rss.build_feed("today_in_energy", parsed, 50, "")
        assert data["items"][0]["src"].startswith("https://www.eia.gov/")

    def test_limit_and_sort_desc(self):
        parsed = feedparser.parse(SAMPLE_RSS)
        data = rss.build_feed("today_in_energy", parsed, 1, "")
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "First Article"

    def test_presentation_variants(self):
        parsed = feedparser.parse(PRESENTATION_RSS)
        data = rss.build_feed("presentations", parsed, 50, "http://t/eia_proxy")
        deck, video, page = data["items"]
        assert deck["viewer"] == "pdf"
        assert deck["src"] == "http://t/eia_proxy/pressroom/presentations/deck.pdf"
        assert (
            deck["ppt_url"] == "https://www.eia.gov/pressroom/presentations/deck.pptx"
        )
        assert {"label": "Subject", "value": "Energy"} in deck["meta"]
        assert video["viewer"] == "embed"
        assert video["src"] == "https://www.youtube.com/embed/abc123"
        assert page["viewer"] == "page"
        assert page["src"] == "http://t/eia_proxy/pressroom/other.php"

    def test_table_feed_renders_body_html(self):
        parsed = feedparser.parse(PRICE_RSS)
        data = rss.build_feed("gasoline_diesel", parsed, 50, "http://t/eia_proxy")
        item = data["items"][0]
        assert item["viewer"] == "table"
        assert "<table" in item["body_html"]

    def test_empty_feed(self):
        parsed = feedparser.parse(b"<rss><channel></channel></rss>")
        data = rss.build_feed("today_in_energy", parsed, 50, "")
        assert data["items"] == []
        assert data["label"] == "Today in Energy"


class TestRenderRssHtml:
    def test_escapes_blob_and_sets_theme(self):
        html = rss.render_rss_html({"feed": "x", "label": "<L>&", "items": []}, "light")
        assert "__EIA_RSS_DATA__" not in html
        assert "\\u003cL\\u003e\\u0026" in html
        assert '"theme": "light"' in html or '"light"' in html

    def test_dark_default(self):
        html = rss.render_rss_html({"feed": "x", "items": []}, "anything")
        assert '"dark"' in html


class TestRssFeedEndpoint:
    @pytest.fixture
    def stubbed(self, monkeypatch):
        session = _FakeSession([_FakeResponse(SAMPLE_RSS)])

        async def fake_get_session():
            return session

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.get_async_requests_session",
            fake_get_session,
        )
        return session

    @pytest.mark.asyncio
    async def test_renders_feed_with_proxy_base(self, stubbed):
        response = await rss_widget.rss_feed(
            "today_in_energy",
            "dark",
            {"url": "http://t/api/v1/eia/rss_feed", "query": "", "path": ""},
        )
        text = response.body.decode()
        assert "First Article" in text
        assert "eia_proxy/todayinenergy" in text
        assert stubbed.closed is True

    @pytest.mark.asyncio
    async def test_unknown_feed_falls_back(self, stubbed):
        response = await rss_widget.rss_feed(
            "bogus",
            "light",
            {"url": "http://t/api/v1/eia/rss_feed", "query": "", "path": ""},
        )
        assert '"today_in_energy"' in response.body.decode()


class TestRouterRegistration:
    def test_route_and_widget_config(self):
        routes = {route.path: route for route in rss_widget.router._api_router.routes}
        widget = routes["/rss_feed"]
        config = widget.openapi_extra["widget_config"]
        params = {p["paramName"]: p for p in config["params"]}
        assert params["theme"]["show"] is False
        assert [o["value"] for o in params["feed"]["options"]] == list(
            rss.EIA_RSS_FEEDS
        )
