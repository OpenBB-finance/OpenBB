"""Unit tests for ``openbb_bls.utils.cpi_charts`` internals."""

from __future__ import annotations

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_bls.models.cpi_charts as ccm
from openbb_bls.utils import cpi_charts as cc


class _FakeResp:
    """Minimal ``requests.Response`` stand-in."""

    def __init__(self, content: bytes = b"", status_code: int = 200):
        self.content = content
        self.status_code = status_code


_TS_TABLE = """
<!DOCTYPE html><html><body>
<table class="regular" id="cpi_rc_test">
<caption><span class="tableTitle">12-month percentage change, selected categories</span></caption>
<thead><tr><th>Month</th><th>All items</th><th>Food</th></tr></thead>
<tbody>
  <tr><th><p>Apr 2006</p></th><td>3.5%</td><td>1.8%</td></tr>
  <tr></tr>
  <tr><th><p>May 2006</p></th><td>4.2%</td><td></td></tr>
  <tr><th><p>not a month</p></th><td>9.9%</td><td>1.0%</td></tr>
</tbody>
</table>
</body></html>
"""

_CATEGORY_TABLE = """
<table class="regular" id="cpi_rc_cat">
<thead><tr><th>Category</th><th>12-month percent change</th></tr></thead>
<tbody>
  <tr><th>All items</th><td>3.8%</td></tr>
  <tr><th></th><td>1.0%</td></tr>
  <tr><th>Food</th><td>3.2%</td></tr>
</tbody>
</table>
"""


def test_fetch_chart_html_non_200_raises(monkeypatch):
    """A non-200 response raises OpenBBError."""
    import requests

    cc.fetch_chart_html.cache_clear()
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResp(status_code=500))
    with pytest.raises(OpenBBError, match="HTTP 500"):
        cc.fetch_chart_html("slug")
    cc.fetch_chart_html.cache_clear()


def test_fetch_chart_html_success_latin1(monkeypatch):
    """A 200 response decodes (latin-1 fallback) and returns the HTML."""
    import requests

    cc.fetch_chart_html.cache_clear()
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResp(content="café".encode("latin-1"))
    )
    assert "caf" in cc.fetch_chart_html("slug")
    cc.fetch_chart_html.cache_clear()


def test_parse_month_branches():
    """``_parse_month`` parses ``Mon YYYY`` and rejects junk / bad months."""
    assert cc._parse_month("Apr 2006") == date(2006, 4, 1)
    assert cc._parse_month("nope") is None
    assert cc._parse_month("Xyz 2006") is None


def test_to_num_branches():
    """``_to_num`` strips commas/percent and maps blanks / junk to None."""
    assert cc._to_num("3.5%") == 3.5
    assert cc._to_num("1,234") == 1234.0
    assert cc._to_num("0.654") == 0.654
    assert cc._to_num(None) is None
    assert cc._to_num("") is None
    assert cc._to_num("(NA)") is None
    assert cc._to_num("abc") is None


def test_parse_chart_table_timeseries():
    """A time-series chart keys rows by date, fills missing cells with None."""
    res = cc.parse_chart_table(_TS_TABLE, "by-category-line")
    assert res["table_id"] == "cpi_rc_test"
    assert res["chart_title"] == "12-month percentage change, selected categories"
    rows = res["rows"]
    # Apr + May kept; empty <tr> and bad-month row dropped.
    assert len(rows) == 2
    apr = [r for r in rows if r["date"] == date(2006, 4, 1)][0]
    assert apr["all_items"] == 3.5
    assert apr["food"] == 1.8
    may = [r for r in rows if r["date"] == date(2006, 5, 1)][0]
    assert may["food"] is None  # blank cell
    # Declared series beyond the table's columns are present and None.
    assert apr["shelter"] is None


def test_parse_chart_table_category():
    """The category chart keys rows by category and skips blank-category rows."""
    res = cc.parse_chart_table(_CATEGORY_TABLE, "by-category")
    rows = res["rows"]
    # Blank-category row dropped; two real rows kept.
    assert len(rows) == 2
    all_items = [r for r in rows if r["category"] == "All items"][0]
    assert all_items["change_12m"] == 3.8
    assert "date" not in all_items
    food = [r for r in rows if r["category"] == "Food"][0]
    assert food["change_12m"] == 3.2


def test_parse_chart_table_missing_table_raises():
    """A page without a data table raises OpenBBError."""
    with pytest.raises(OpenBBError, match="no data table"):
        cc.parse_chart_table(
            "<html><body><p>nope</p></body></html>", "by-category-line"
        )


def test_parse_chart_table_no_caption_uses_label():
    """Without a caption the chart title falls back to the spec label."""
    html = """
    <table class="regular">
    <thead><tr><th>Month</th><th>All items</th></tr></thead>
    <tbody><tr><th>Apr 2006</th><td>3.5%</td></tr></tbody>
    </table>
    """
    res = cc.parse_chart_table(html, "by-region")
    assert res["chart_title"] == cc.CHART_SPECS["by-region"]["label"]
    assert res["table_id"] == "cpi-chart-by-region"


def test_fetch_and_parse_dispatch(monkeypatch):
    """``fetch_and_parse`` resolves the slug and parses the fetched HTML."""
    captured = {}

    def _fake(slug):
        captured["slug"] = slug
        return _TS_TABLE

    monkeypatch.setattr(cc, "fetch_chart_html", _fake)
    res = cc.fetch_and_parse("by-category-line")
    assert captured["slug"] == cc.CHART_SPECS["by-category-line"]["slug"]
    assert res["rows"]


def test_model_empty_rows_raises():
    """A chart fetcher raises EmptyDataError when no rows are parsed."""
    fetcher = ccm.CPI_CHART_FETCHERS[ccm.cpi_model_name("by-category-line")]
    query = fetcher.transform_query({})
    with pytest.raises(EmptyDataError):
        fetcher.transform_data(query, [])
