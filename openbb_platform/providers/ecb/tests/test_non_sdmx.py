"""Unit tests for ``openbb_ecb.utils.non_sdmx`` (mocked HTTP)."""

import asyncio
import gzip
from datetime import date

import openbb_core.provider.utils.helpers as core_helpers
import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_ecb.utils import non_sdmx


class _FakeResp:
    def __init__(self, status=200, text="", raw=b""):
        self.status = status
        self._text = text
        self._raw = raw

    async def text(self):
        return self._text

    async def read(self):
        return self._raw


def test_strip_html():
    """Tags are removed and whitespace collapsed."""
    assert non_sdmx._strip_html("<b>a   b</b>\n c") == "a b c"


def test_parse_ea_date():
    """DD/MM/YYYY dates parse; bad input is None."""
    assert non_sdmx._parse_ea_date("15/12/2026 00:00:00") == "2026-12-15"
    assert non_sdmx._parse_ea_date("bad") is None


def test_article_to_markdown():
    """``<main>`` renders to markdown; image/link URLs become absolute; no main -> ''."""
    base = "https://www.ecb.europa.eu/press/blog/x.en.html"
    html = (
        "<html><body><main>"
        "<nav>sitemenu</nav>"
        "<h2>Chart 1</h2><p>Some body text here, long enough to read.</p>"
        '<img src="img/chart.png" alt="c">'
        '<img alt="no-src">'  # image without src -> left untouched
        '<a href="/more">link</a>'
        "<a>no-href</a>"  # anchor without href -> left untouched
        "</main></body></html>"
    )
    md = non_sdmx._article_to_markdown(html, base)
    assert "Chart 1" in md and "Some body text" in md
    assert "sitemenu" not in md  # chrome inside <main> is stripped
    # page-relative image -> page folder; root-relative link -> origin
    assert "https://www.ecb.europa.eu/press/blog/img/chart.png" in md
    assert "https://www.ecb.europa.eu/more" in md
    assert (
        non_sdmx._article_to_markdown("<html><body>no main</body></html>", base) == ""
    )


def test_fetch_release_body(monkeypatch):
    """Fetches + converts an ECB page; non-ECB URL or fetch error -> '' (SSRF guard)."""

    async def _text(url):
        return (
            "<html><body><main><p>Body content paragraph.</p>"
            '<img src="a.png"></main></body></html>'
        )

    monkeypatch.setattr(non_sdmx, "_aget_text", _text)
    md = asyncio.run(
        non_sdmx.fetch_release_body("https://www.ecb.europa.eu/press/x.en.html")
    )
    assert "Body content" in md
    assert "https://www.ecb.europa.eu/press/a.png" in md

    for bad in ("https://evil.example.com/x", "http://www.ecb.europa.eu/x"):
        assert asyncio.run(non_sdmx.fetch_release_body(bad)) == ""

    async def _boom(url):
        raise RuntimeError("network")

    monkeypatch.setattr(non_sdmx, "_aget_text", _boom)
    assert asyncio.run(non_sdmx.fetch_release_body("https://www.ecb.europa.eu/x")) == ""


def test_release_excerpt():
    """Excerpt is the first substantial paragraph, truncated; preamble is skipped."""
    body = "\n".join(
        [
            "* THE ECB BLOG",  # nav bullet
            "# A title heading",  # heading
            "29 May 2026",  # short
            "By Jane Doe, John Roe",  # byline
            "![](https://x/img.png)",  # image
            "This is the first real summary paragraph here, and it is comfortably"
            " long enough to qualify as the excerpt.",
        ]
    )
    assert non_sdmx.release_excerpt(body).startswith("This is the first real summary")
    # long paragraph is truncated at a word boundary with an ellipsis
    out = non_sdmx.release_excerpt("word " * 100, limit=40)
    assert out.endswith("…") and len(out) <= 41
    # a heading over the length threshold is still skipped -> nothing substantial
    assert non_sdmx.release_excerpt("# " + "x" * 90) == ""


def test_parse_eligible_assets_csv():
    """UTF-16 tab-delimited collateral CSV parses; bad floats become None."""
    header = (
        "ISIN_CODE\tTYPE\tDENOMINATION\tMATURITY_DATE\t"
        "COUPON_RATE (%)\tHAIRCUT\tCLIMATE_FACTOR"
    )
    rows = [
        "XS1\tAT01\tEUR\t15/12/2026 00:00:00\t1.5\tbad\t1",
        "XS2\tAT02\tUSD\t\t\t2.0\t",
        "\tAT03\tEUR\t\t\t\t",  # no ISIN -> dropped
    ]
    raw = ("\n".join([header, *rows])).encode("utf-16")
    records = non_sdmx._parse_eligible_assets_csv(raw)
    assert [r["isin"] for r in records] == ["XS1", "XS2"]
    assert records[0]["coupon_rate"] == 1.5
    assert records[0]["haircut"] is None  # bad float coerced to None
    assert records[0]["maturity_date"] == "2026-12-15"


def test_fetch_rss_items(monkeypatch):
    """RSS items parse; a missing pubDate yields a None date."""
    xml = (
        '<?xml version="1.0"?><rss><channel>'
        "<item><title>T</title><link>http://x</link>"
        "<pubDate>Wed, 24 Jun 2026 12:00:00 +0200</pubDate></item>"
        "<item><title>NoDate</title><link>http://y</link></item>"
        "<item><title>Bad</title><link>http://z</link>"
        "<pubDate>not a valid date</pubDate></item>"
        "</channel></rss>"
    )

    async def fake(url, headers=None, response_callback=None, **kwargs):
        return await response_callback(_FakeResp(text=xml), None)

    monkeypatch.setattr(core_helpers, "amake_request", fake)
    items = asyncio.run(non_sdmx.fetch_rss_items("press_releases"))
    assert items[0]["title"] == "T" and items[0]["date"]
    assert items[0]["category"] == "press_releases"
    assert items[1]["date"] is None  # missing pubDate
    assert items[2]["date"] is None  # unparseable pubDate


def test_fetch_release_calendar(monkeypatch):
    """The statscal dt/dd pairs parse into calendar rows; bad dates are skipped."""
    html = (
        "<dt>24/06/2026 10:00 CET</dt>"
        "<dd>Some statistic (Dataset: BSI) Reference period: May-2026 "
        "Includes press release</dd>"
        "<dt>no date here</dt><dd>ignored</dd>"
    )

    async def fake(url, headers=None, response_callback=None, **kwargs):
        return await response_callback(_FakeResp(text=html), None)

    monkeypatch.setattr(core_helpers, "amake_request", fake)
    rows = asyncio.run(non_sdmx.fetch_release_calendar())
    assert len(rows) == 1
    assert rows[0]["category"] == "BSI"
    assert rows[0]["reference_period"] == "May-2026"
    assert rows[0]["date"] == "2026-06-24T10:00:00"
    assert rows[0]["country"] == "Euro Area"


def test_fetch_eligible_assets_walks_back(monkeypatch):
    """A missing first day is skipped; the gz file on the prior day is used."""
    raw = ("ISIN_CODE\tTYPE\tDENOMINATION\nXS1\tAT01\tEUR").encode("utf-16")
    gz = gzip.compress(raw)
    calls = {"n": 0}

    async def fake(url, headers=None, response_callback=None, **kwargs):
        calls["n"] += 1
        status = 404 if calls["n"] == 1 else 200
        return await response_callback(
            _FakeResp(status=status, raw=(gz if status == 200 else b"")), None
        )

    monkeypatch.setattr(core_helpers, "amake_request", fake)
    file_date, rows = asyncio.run(non_sdmx.fetch_eligible_assets(date(2026, 6, 24)))
    assert rows[0]["isin"] == "XS1"
    assert file_date == "2026-06-23"


def test_fetch_eligible_assets_uncompressed(monkeypatch):
    """A non-gzip 200 payload falls through to raw decoding (default date)."""
    raw = ("ISIN_CODE\tTYPE\nXS9\tAT01").encode("utf-16")

    async def fake(url, headers=None, response_callback=None, **kwargs):
        return await response_callback(_FakeResp(status=200, raw=raw), None)

    monkeypatch.setattr(core_helpers, "amake_request", fake)
    _, rows = asyncio.run(non_sdmx.fetch_eligible_assets(None))
    assert rows[0]["isin"] == "XS9"


def test_fetch_eligible_assets_not_found(monkeypatch):
    """All days missing raises an error."""

    async def fake(url, headers=None, response_callback=None, **kwargs):
        return await response_callback(_FakeResp(status=404), None)

    monkeypatch.setattr(core_helpers, "amake_request", fake)
    with pytest.raises(OpenBBError):
        asyncio.run(non_sdmx.fetch_eligible_assets(date(2026, 6, 24)))
