"""Unit tests for ``openbb_bls.utils.ppi_charts`` internals."""

from __future__ import annotations

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_bls.models.ppi_charts as pcm
from openbb_bls.utils import ppi_charts as pc


class _FakeResp:
    """Minimal ``requests.Response`` stand-in."""

    def __init__(self, content: bytes = b"", status_code: int = 200):
        self.content = content
        self.status_code = status_code


_TS_TABLE = """
<!DOCTYPE html><html><body>
<table class="regular" id="ppi_rc_test">
<caption><span class="tableTitle">PPI for final demand, 1-month percent change</span></caption>
<thead><tr><th>Month</th><th>Total</th><th>Total less foods, energy, and trade services</th></tr></thead>
<tbody>
  <tr><th><p>Jan 2010</p></th><td>0.9%</td><td>0.4%</td></tr>
  <tr></tr>
  <tr><th><p>Feb 2010</p></th><td>-0.2%</td><td></td></tr>
  <tr><th><p>not a month</p></th><td>9.9%</td><td>1.0%</td></tr>
</tbody>
</table>
</body></html>
"""

_COMMODITY_TABLE = """
<table class="regular" id="ppi_rc_cmdty">
<thead><tr><th>Commodity</th><th>1-month percent change</th></tr></thead>
<tbody>
  <tr><th>Goods</th><td>2.0%</td></tr>
  <tr><th></th><td>1.0%</td></tr>
  <tr><th>Foods</th><td>0.2%</td></tr>
</tbody>
</table>
"""


def test_fetch_chart_html_non_200_raises(monkeypatch):
    """A non-200 response raises OpenBBError."""
    import requests

    pc.fetch_chart_html.cache_clear()
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResp(status_code=500))
    with pytest.raises(OpenBBError, match="HTTP 500"):
        pc.fetch_chart_html("slug")
    pc.fetch_chart_html.cache_clear()


def test_fetch_chart_html_success_latin1(monkeypatch):
    """A 200 response decodes (latin-1 fallback) and returns the HTML."""
    import requests

    pc.fetch_chart_html.cache_clear()
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResp(content="café".encode("latin-1"))
    )
    assert "caf" in pc.fetch_chart_html("slug")
    pc.fetch_chart_html.cache_clear()


def test_parse_month_branches():
    """``_parse_month`` parses ``Mon YYYY`` and rejects junk / bad months."""
    assert pc._parse_month("Jan 2010") == date(2010, 1, 1)
    assert pc._parse_month("nope") is None
    assert pc._parse_month("Xyz 2010") is None


def test_to_num_branches():
    """``_to_num`` strips commas/percent and maps blanks / junk to None."""
    assert pc._to_num("0.9%") == 0.9
    assert pc._to_num("-0.2%") == -0.2
    assert pc._to_num("1,234") == 1234.0
    assert pc._to_num(None) is None
    assert pc._to_num("") is None
    assert pc._to_num("(NA)") is None
    assert pc._to_num("abc") is None


def test_parse_chart_table_timeseries():
    """A time-series chart keys rows by date, fills missing cells with None."""
    res = pc.parse_chart_table(_TS_TABLE, "final-demand-1m")
    assert res["table_id"] == "ppi_rc_test"
    assert res["chart_title"] == "PPI for final demand, 1-month percent change"
    rows = res["rows"]
    # Jan + Feb kept; empty <tr> and bad-month row dropped.
    assert len(rows) == 2
    jan = [r for r in rows if r["date"] == date(2010, 1, 1)][0]
    assert jan["total"] == 0.9
    assert jan["total_less_foods_energy_trade"] == 0.4
    feb = [r for r in rows if r["date"] == date(2010, 2, 1)][0]
    assert feb["total_less_foods_energy_trade"] is None  # blank cell
    # Declared series beyond the table's columns are present and None.
    assert jan["energy"] is None


def test_parse_chart_table_commodity():
    """The commodity chart keys rows by commodity and skips blank-commodity rows."""
    res = pc.parse_chart_table(_COMMODITY_TABLE, "final-demand-components-1m")
    rows = res["rows"]
    # Blank-commodity row dropped; two real rows kept.
    assert len(rows) == 2
    goods = [r for r in rows if r["commodity"] == "Goods"][0]
    assert goods["change_1m"] == 2.0
    assert "date" not in goods
    foods = [r for r in rows if r["commodity"] == "Foods"][0]
    assert foods["change_1m"] == 0.2


def test_parse_chart_table_missing_table_raises():
    """A page without a data table raises OpenBBError."""
    with pytest.raises(OpenBBError, match="no data table"):
        pc.parse_chart_table("<html><body><p>nope</p></body></html>", "final-demand-1m")


def test_parse_chart_table_no_caption_uses_label():
    """Without a caption the chart title falls back to the spec label."""
    html = """
    <table class="regular">
    <thead><tr><th>Month</th><th>Overall</th></tr></thead>
    <tbody><tr><th>Jan 2010</th><td>0.5%</td></tr></tbody>
    </table>
    """
    res = pc.parse_chart_table(html, "intermediate-services-1m")
    assert res["chart_title"] == pc.CHART_SPECS["intermediate-services-1m"]["label"]
    assert res["table_id"] == "ppi-chart-intermediate-services-1m"
    assert res["rows"][0]["overall"] == 0.5


def test_fetch_and_parse_dispatch(monkeypatch):
    """``fetch_and_parse`` resolves the slug and parses the fetched HTML."""
    captured = {}

    def _fake(slug):
        captured["slug"] = slug
        return _TS_TABLE

    monkeypatch.setattr(pc, "fetch_chart_html", _fake)
    res = pc.fetch_and_parse("final-demand-1m")
    assert captured["slug"] == pc.CHART_SPECS["final-demand-1m"]["slug"]
    assert res["rows"]


def test_model_empty_rows_raises():
    """A chart fetcher raises EmptyDataError when no rows are parsed."""
    fetcher = pcm.PPI_CHART_FETCHERS[pcm.ppi_model_name("final-demand-1m")]
    query = fetcher.transform_query({})
    with pytest.raises(EmptyDataError):
        fetcher.transform_data(query, [])
