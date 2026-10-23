"""Unit tests for ``openbb_sec.utils.financial_report``."""

import asyncio

from openbb_sec.utils import financial_report
from openbb_sec.utils.financial_report import render_financial_report

_DIRECTORY = "https://www.sec.gov/Archives/edgar/data/1/000123456724000077/"

_SUMMARY = (
    b"<FilingSummary><MyReports>"
    b"<Report><HtmlFileName>R1.htm</HtmlFileName>"
    b"<ShortName>Balance Sheet</ShortName></Report>"
    b"<Report><HtmlFileName>R2.htm</HtmlFileName></Report>"
    b"<Report><ShortName>No File</ShortName></Report>"
    b"<Report><HtmlFileName>   </HtmlFileName></Report>"
    b"<Report><HtmlFileName>R3.htm</HtmlFileName><ShortName>Empty</ShortName></Report>"
    b"<Report><HtmlFileName>R4.htm</HtmlFileName><ShortName>No Body</ShortName></Report>"
    b"<Report><HtmlFileName>R5.htm</HtmlFileName><ShortName>Head Only</ShortName></Report>"
    b"</MyReports></FilingSummary>"
)

_R1 = (
    b"<html><head><link rel=stylesheet href='report.css'></head><body>"
    b"<script src='Show.js'></script>"
    b"<script>toggle();</script>"
    b"<script>   </script>"
    b"<table><tr><td>Cash</td></tr></table>"
    b"</body></html>"
)
_R2 = b"<html><body><div>Operations</div></body></html>"
_R4 = b"<div>no body or head here</div>"
_R5 = b"<html><head><title>t</title></head>Head content here</html>"


def _pages(**overrides):
    """Default document map for the filing directory, with optional overrides."""
    pages = {
        "FilingSummary.xml": _SUMMARY,
        "R1.htm": _R1,
        "R2.htm": _R2,
        "R3.htm": b"",
        "R4.htm": _R4,
        "R5.htm": _R5,
        "report.css": b"table{border:1px}",
        "Show.js": b"function Show(){}",
    }
    pages.update(overrides)
    return pages


def _patch_get(monkeypatch, pages):
    """Patch ``cached_bytes`` to serve a filename-keyed document map."""

    def _cached(url, **kwargs):
        for name, content in pages.items():
            if url.endswith(name):
                return content
        return b""

    monkeypatch.setattr("openbb_sec.utils.cache.cached_bytes", _cached)


class TestExtractBody:
    """Body extraction from an R-file's HTML."""

    def test_from_body_tag(self):
        assert (
            financial_report._extract_body("<html><body>X<b>Y</b></body></html>")
            == "X<b>Y</b>"
        )

    def test_from_head_fallback(self):
        assert financial_report._extract_body("<html><head></head>Z</html>") == "Z"

    def test_none_when_neither(self):
        assert financial_report._extract_body("<div>no body</div>") is None


class TestCollectInlineScripts:
    """Inline (non-src) script collection."""

    def test_keeps_inline_skips_src_and_empty(self):
        html = (
            "<script src='a.js'></script>"
            "<script>doToggle();</script>"
            "<script>   </script>"
        )
        assert financial_report._collect_inline_scripts(html) == "doToggle();"

    def test_matches_script_end_tag_with_whitespace(self):
        html = "<script>doToggle();</script   >"
        assert financial_report._collect_inline_scripts(html) == "doToggle();"

    def test_matches_script_end_tag_with_whitespace_and_trailing_text(self):
        html = "<script>doToggle();</script\t\n bar>"
        assert financial_report._collect_inline_scripts(html) == "doToggle();"


class TestStripScripts:
    """Removing script nodes from body fragments."""

    def test_strips_inline_scripts_from_fragment(self):
        html = "<div>A</div><script>doToggle();</script\t\n bar><div>B</div>"
        assert financial_report._strip_scripts(html) == "<div>A</div><div>B</div>"

    def test_ignores_script_without_parent(self, monkeypatch):
        class _Script:
            text = "ignored()"
            tail = ""

            def getparent(self):
                return None

        class _Root:
            def iter(self, tag):
                assert tag == "script"
                return iter([_Script()])

        monkeypatch.setattr(financial_report, "_parse_fragment", lambda html: _Root())
        monkeypatch.setattr(
            financial_report, "_serialize_fragment", lambda root: "<div/>"
        )
        assert financial_report._strip_scripts("<div/>") == "<div/>"


class TestGet:
    """The cached, error-suppressing byte fetch."""

    def test_returns_bytes(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_sec.utils.cache.cached_bytes", lambda url, **k: b"hi"
        )
        assert asyncio.run(financial_report._get("u", True)) == b"hi"

    def test_suppresses_errors(self, monkeypatch):
        def _boom(url, **kwargs):
            raise RuntimeError("x")

        monkeypatch.setattr("openbb_sec.utils.cache.cached_bytes", _boom)
        assert asyncio.run(financial_report._get("u", True)) == b""


class TestRenderFinancialReport:
    """Assembling R-file statements into one section-per-report page."""

    def test_assembles_sections_styles_and_scripts(self, monkeypatch):
        _patch_get(monkeypatch, _pages())
        html = asyncio.run(render_financial_report(_DIRECTORY))
        assert html is not None
        # Stylesheet and the row-toggle scripts are inlined once.
        assert "<style>table{border:1px}</style>" in html
        assert "<script>function Show(){}" in html
        assert "toggle();" in html
        # Reports become sections; the ShortName wins, else the file name.
        assert 'data-name="Balance Sheet"' in html
        assert 'data-name="R2.htm"' in html
        assert 'data-name="Head Only"' in html
        assert "Cash" in html
        assert "Operations" in html
        assert "Head content here" in html
        assert '<section class=ob-sec data-name="Balance Sheet"><script' not in html
        # Empty and body-less reports contribute no section.
        assert 'data-name="Empty"' not in html
        assert 'data-name="No Body"' not in html

    def test_empty_summary_returns_none(self, monkeypatch):
        _patch_get(monkeypatch, _pages(**{"FilingSummary.xml": b""}))
        assert asyncio.run(render_financial_report(_DIRECTORY)) is None

    def test_no_valid_reports_returns_none(self, monkeypatch):
        summary = (
            b"<FilingSummary><Report><ShortName>x</ShortName></Report></FilingSummary>"
        )
        _patch_get(monkeypatch, _pages(**{"FilingSummary.xml": summary}))
        assert asyncio.run(render_financial_report(_DIRECTORY)) is None

    def test_no_renderable_sections_returns_none(self, monkeypatch):
        summary = (
            b"<FilingSummary><Report><HtmlFileName>R1.htm</HtmlFileName>"
            b"<ShortName>Only</ShortName></Report></FilingSummary>"
        )
        _patch_get(monkeypatch, _pages(**{"FilingSummary.xml": summary, "R1.htm": b""}))
        assert asyncio.run(render_financial_report(_DIRECTORY)) is None

    def test_without_css_js_or_inline_scripts(self, monkeypatch):
        summary = (
            b"<FilingSummary><Report><HtmlFileName>R1.htm</HtmlFileName>"
            b"<ShortName>Plain</ShortName></Report></FilingSummary>"
        )
        _patch_get(
            monkeypatch,
            _pages(
                **{
                    "FilingSummary.xml": summary,
                    "R1.htm": b"<html><body><div>X</div></body></html>",
                    "report.css": b"",
                    "Show.js": b"",
                }
            ),
        )
        html = asyncio.run(render_financial_report(_DIRECTORY))
        assert html is not None
        assert html.startswith('<div class="ob-fr">')
        assert "<style>" not in html
        assert "<script>" not in html
