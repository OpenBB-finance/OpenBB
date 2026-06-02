"""Unit tests for ``openbb_bls.utils.ximpim_charts`` internals."""

from __future__ import annotations

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_bls.utils import ximpim_charts as xc


class _FakeResp:
    """Minimal ``requests.Response`` stand-in."""

    def __init__(self, content: bytes = b"", status_code: int = 200):
        self.content = content
        self.status_code = status_code


_TABLE = """
<!DOCTYPE html><html><body>
<table class="regular" id="ipp_rc_test">
<caption><span class="tableTitle">Test chart title</span></caption>
<thead><tr>
  <th>Month</th><th>All imports</th><th>Fuel imports</th>
</tr></thead>
<tbody>
  <tr><th><p>Apr 2006</p></th><td>5.8%</td><td>27.8%</td></tr>
  <tr></tr>
  <tr><th><p>May 2006</p></th><td>-0.1%</td><td>(NA)</td></tr>
  <tr><th><p>not a month</p></th><td>9.9%</td><td>1.0%</td></tr>
</tbody>
</table>
</body></html>
"""


def test_fetch_chart_html_non_200_raises(monkeypatch):
    """A non-200 response raises OpenBBError."""
    import requests

    xc.fetch_chart_html.cache_clear()
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResp(status_code=404))
    with pytest.raises(OpenBBError, match="HTTP 404"):
        xc.fetch_chart_html("some-slug")
    xc.fetch_chart_html.cache_clear()


def test_fetch_chart_html_success_and_latin1(monkeypatch):
    """A 200 response decodes (latin-1 fallback) and returns the HTML."""
    import requests

    xc.fetch_chart_html.cache_clear()
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResp(content="café".encode("latin-1"))
    )
    out = xc.fetch_chart_html("another-slug")
    assert "caf" in out
    xc.fetch_chart_html.cache_clear()


def test_parse_month_branches():
    """``_parse_month`` parses ``Mon YYYY`` and rejects junk / bad months."""
    assert xc._parse_month("Apr 2006") == date(2006, 4, 1)
    assert xc._parse_month("September 2020") == date(2020, 9, 1)
    assert xc._parse_month("nope") is None
    assert xc._parse_month("Xyz 2020") is None


def test_to_pct_branches():
    """``_to_pct`` strips %/commas and maps blanks / N/A / junk to None."""
    assert xc._to_pct("5.8%") == 5.8
    assert xc._to_pct("-0.1%") == -0.1
    assert xc._to_pct("1,234.5%") == 1234.5
    assert xc._to_pct(None) is None
    assert xc._to_pct("(NA)") is None
    assert xc._to_pct("-") is None
    assert xc._to_pct("") is None
    assert xc._to_pct("abc") is None


def test_parse_chart_table_full():
    """Parser yields wide rows keyed by chart fields; N/A -> None, bad months dropped."""
    res = xc.parse_chart_table(_TABLE, "import-export")
    assert res["table_id"] == "ipp_rc_test"
    assert res["chart_title"] == "Test chart title"
    rows = res["rows"]
    # Apr + May rows kept; empty <tr> and the bad-month row dropped.
    assert len(rows) == 2
    apr = [r for r in rows if r["date"] == date(2006, 4, 1)][0]
    # Columns are named from CHART_FIELDS["import-export"] by position.
    assert apr["all_imports"] == 5.8
    assert apr["fuel_imports"] == 27.8
    may = [r for r in rows if r["date"] == date(2006, 5, 1)][0]
    assert may["all_imports"] == -0.1
    # "(NA)" cell becomes None but the column is still present.
    assert may["fuel_imports"] is None
    # Columns beyond the table's two are still declared (None).
    assert apr["nonagricultural_exports"] is None


def test_parse_chart_table_missing_table_raises():
    """A page without a data table raises OpenBBError."""
    with pytest.raises(OpenBBError, match="no data table"):
        xc.parse_chart_table(
            "<html><body><p>nothing</p></body></html>", "import-export"
        )


def test_parse_chart_table_short_row_fills_missing_with_none():
    """A data row shorter than the chart's field list fills absent columns with None."""
    html = """
    <table class="regular" id="t">
    <thead><tr><th>Month</th><th>Wheat</th><th>Soybeans</th><th>Corn</th></tr></thead>
    <tbody><tr><th>Apr 2006</th><td>1.0%</td></tr></tbody>
    </table>
    """
    res = xc.parse_chart_table(html, "exports-by-grains")
    assert len(res["rows"]) == 1
    row = res["rows"][0]
    assert row["wheat"] == 1.0
    # Soybeans / corn columns are present but None.
    assert row["soybeans"] is None
    assert row["corn"] is None


def test_parse_chart_table_no_caption_uses_label():
    """Without a caption, the chart title falls back to the registry label."""
    html = """
    <table class="regular">
    <thead><tr><th>Month</th><th>Wheat</th></tr></thead>
    <tbody><tr><th>Apr 2006</th><td>10.4%</td></tr></tbody>
    </table>
    """
    res = xc.parse_chart_table(html, "exports-by-grains")
    assert res["chart_title"] == xc.CHART_LABELS["exports-by-grains"]
    assert res["table_id"] == "ximpim-chart-exports-by-grains"
    assert res["rows"][0]["wheat"] == 10.4


def test_fetch_and_parse_dispatch(monkeypatch):
    """``fetch_and_parse`` resolves the slug and parses the fetched HTML."""
    captured = {}

    def _fake_fetch(slug):
        captured["slug"] = slug
        return _TABLE

    monkeypatch.setattr(xc, "fetch_chart_html", _fake_fetch)
    res = xc.fetch_and_parse("import-export")
    assert captured["slug"] == xc.CHART_SLUGS["import-export"]
    assert res["rows"]
