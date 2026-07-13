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
    assert non_sdmx._strip_html("<b>a   b</b>\n c") == "a b c"


def test_parse_ea_date():
    assert non_sdmx._parse_ea_date("15/12/2026 00:00:00") == "2026-12-15"
    assert non_sdmx._parse_ea_date("bad") is None


def test_article_to_html():
    base = "https://www.ecb.europa.eu/press/blog/x.en.html"
    html = (
        "<html><head>"
        '<link rel="stylesheet" href="/shared/style.css">'
        "</head><body>"
        "<header>site banner</header>"
        "<nav>site menu</nav>"
        "<main>"
        "<header></header>"
        '<div class="pub print-hidden">Publications Loading…</div>'
        '<nav class="pub-side-nav">toc</nav>'
        "<script>window.x=1</script>"
        "<form>search</form>"
        '<div class="title"><h1>Article title</h1></div>'
        '<div class="section">'
        "<h2>Chart 1</h2><p>Some body text here, long enough to read.</p>"
        '<img src="img/chart.png">'
        '<a href="/more">link</a>'
        '<table class="table-chart-duo"><tbody><tr><td>'
        '<img src="img/panel0.png"></td></tr></tbody></table>'
        "</div>"
        '<div class="related-topics"><a class="tag" href="/topics">Related topics</a></div>'
        '<div class="address-box"><p class="line">CONTACT</p></div>'
        "</main>"
        "<footer>site footer</footer>"
        "</body></html>"
    )
    out = non_sdmx._article_to_html(html, base)
    assert "Article title" in out and "table-chart-duo" in out
    assert "site banner" not in out
    assert "site menu" not in out
    assert "site footer" not in out
    assert "Loading" not in out
    assert "toc" not in out
    assert "window.x" not in out
    assert "search" not in out
    assert "Related topics" not in out
    assert "CONTACT" not in out
    assert 'rel="stylesheet"' not in out
    assert "<base" not in out
    assert 'src="https://www.ecb.europa.eu/press/blog/img/chart.png"' in out
    assert 'src="https://www.ecb.europa.eu/press/blog/img/panel0.png"' in out
    assert 'href="https://www.ecb.europa.eu/more"' in out
    assert 'target="_blank"' in out
    assert non_sdmx._article_to_html("<html><body>no main</body></html>", base) == ""
    assert (
        non_sdmx._article_to_html(
            "<html><body><main><nav>only chrome</nav></main></body></html>", base
        )
        == ""
    )


def test_fetch_release_html(monkeypatch):

    async def _text(url):
        return (
            "<html><body><main><p>Body content paragraph.</p>"
            '<img src="a.png"></main></body></html>'
        )

    monkeypatch.setattr(non_sdmx, "_aget_text", _text)
    out = asyncio.run(
        non_sdmx.fetch_release_html("https://www.ecb.europa.eu/press/x.en.html")
    )
    assert "Body content" in out
    assert 'src="https://www.ecb.europa.eu/press/a.png"' in out

    for bad in ("https://evil.example.com/x", "http://www.ecb.europa.eu/x"):
        assert asyncio.run(non_sdmx.fetch_release_html(bad)) == ""

    async def _boom(url):
        raise RuntimeError("network")

    monkeypatch.setattr(non_sdmx, "_aget_text", _boom)
    assert asyncio.run(non_sdmx.fetch_release_html("https://www.ecb.europa.eu/x")) == ""


def test_fetch_release_html_pdf(monkeypatch):
    pdf_url = "https://www.ecb.europa.eu/pub/pdf/other/report.en.pdf"

    async def _ok(url):
        return 200, b"%PDF-1.4 fake bytes"

    monkeypatch.setattr(non_sdmx, "_aget_bytes", _ok)
    out = asyncio.run(non_sdmx.fetch_release_html(pdf_url))
    assert "<embed" in out and "data:application/pdf;base64," in out

    async def _missing(url):
        return 404, b""

    monkeypatch.setattr(non_sdmx, "_aget_bytes", _missing)
    assert asyncio.run(non_sdmx.fetch_release_html(pdf_url)) == ""

    async def _boom(url):
        raise RuntimeError("network")

    monkeypatch.setattr(non_sdmx, "_aget_bytes", _boom)
    assert asyncio.run(non_sdmx.fetch_release_html(pdf_url)) == ""


def test_parse_eligible_assets_csv():
    header = (
        "ISIN_CODE\tTYPE\tDENOMINATION\tMATURITY_DATE\t"
        "COUPON_RATE (%)\tHAIRCUT\tCLIMATE_FACTOR"
    )
    rows = [
        "XS1\tAT01\tEUR\t15/12/2026 00:00:00\t1.5\tbad\t1",
        "XS2\tAT02\tUSD\t\t\t2.0\t",
        "\tAT03\tEUR\t\t\t\t",
    ]
    raw = ("\n".join([header, *rows])).encode("utf-16")
    records = non_sdmx._parse_eligible_assets_csv(raw)
    assert [r["isin"] for r in records] == ["XS1", "XS2"]
    assert records[0]["coupon_rate"] == 1.5
    assert records[0]["haircut"] is None
    assert records[0]["maturity_date"] == "2026-12-15"


def test_fetch_rss_items(monkeypatch):
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
    assert items[1]["date"] is None
    assert items[2]["date"] is None


def test_fetch_release_calendar(monkeypatch):
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
    raw = ("ISIN_CODE\tTYPE\nXS9\tAT01").encode("utf-16")

    async def fake(url, headers=None, response_callback=None, **kwargs):
        return await response_callback(_FakeResp(status=200, raw=raw), None)

    monkeypatch.setattr(core_helpers, "amake_request", fake)
    _, rows = asyncio.run(non_sdmx.fetch_eligible_assets(None))
    assert rows[0]["isin"] == "XS9"


def test_fetch_eligible_assets_not_found(monkeypatch):

    async def fake(url, headers=None, response_callback=None, **kwargs):
        return await response_callback(_FakeResp(status=404), None)

    monkeypatch.setattr(core_helpers, "amake_request", fake)
    with pytest.raises(OpenBBError):
        asyncio.run(non_sdmx.fetch_eligible_assets(date(2026, 6, 24)))


def test_render_dataflow_info():
    info = {
        "title": "MFI Rates - MIR",
        "catalogue": "https://data.ecb.europa.eu/data/datasets/mir/download",
        "fields": [{"label": "Scope", "html": "<p>Hi</p>"}],
    }
    html = non_sdmx.render_dataflow_info("MIR", info, ["Bank interest rates"])
    assert "<h1>MFI Rates - MIR" in html and "MIR</span>" in html
    assert "<h2>Scope</h2>" in html and "<p>Hi</p>" in html
    assert "Bank interest rates" in html
    assert 'href="https://data.ecb.europa.eu/data/datasets/mir/download"' in html
    bare = non_sdmx.render_dataflow_info("ZZZ", {"fields": []})
    assert "<h1>ZZZ" in bare
    assert "Topics:" not in bare and "series catalogue" not in bare
