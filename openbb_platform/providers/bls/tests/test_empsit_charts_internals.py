"""Unit tests for ``openbb_bls.utils.empsit_charts`` internals."""

from __future__ import annotations

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_bls.models.empsit_charts as ecm
from openbb_bls.utils import empsit_charts as ec


class _FakeResp:
    """Minimal ``requests.Response`` stand-in."""

    def __init__(self, content: bytes = b"", status_code: int = 200):
        self.content = content
        self.status_code = status_code


_TS_TABLE = """
<!DOCTYPE html><html><body>
<table class="regular" id="cps_rc_test">
<caption><span class="tableTitle">Civilian unemployment rate</span></caption>
<thead><tr><th>Month</th><th>Total</th><th>Men, 20 years and over</th></tr></thead>
<tbody>
  <tr><th><p>Apr 2006</p></th><td>4.7</td><td>4.2</td></tr>
  <tr></tr>
  <tr><th><p>May 2006</p></th><td>4.6</td><td></td></tr>
  <tr><th><p>not a month</p></th><td>9.9</td><td>1.0</td></tr>
</tbody>
</table>
</body></html>
"""

_INDUSTRY_TABLE = """
<table class="regular" id="ces_rc_test">
<thead><tr>
  <th>Industry</th><th>Employed (thousands)</th><th>1-month net change (thousands)</th>
</tr></thead>
<tbody>
  <tr><th>Mining and logging</th><td>606</td><td>3</td></tr>
  <tr><th></th><td>1</td><td>2</td></tr>
  <tr><th>Construction</th><td>8,300</td><td>-5</td></tr>
</tbody>
</table>
"""


def test_fetch_chart_html_non_200_raises(monkeypatch):
    """A non-200 response raises OpenBBError."""
    import requests

    ec.fetch_chart_html.cache_clear()
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResp(status_code=500))
    with pytest.raises(OpenBBError, match="HTTP 500"):
        ec.fetch_chart_html("slug")
    ec.fetch_chart_html.cache_clear()


def test_fetch_chart_html_success_latin1(monkeypatch):
    """A 200 response decodes (latin-1 fallback) and returns the HTML."""
    import requests

    ec.fetch_chart_html.cache_clear()
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResp(content="café".encode("latin-1"))
    )
    assert "caf" in ec.fetch_chart_html("slug")
    ec.fetch_chart_html.cache_clear()


def test_parse_month_branches():
    """``_parse_month`` parses ``Mon YYYY`` and rejects junk / bad months."""
    assert ec._parse_month("Apr 2006") == date(2006, 4, 1)
    assert ec._parse_month("nope") is None
    assert ec._parse_month("Xyz 2006") is None


def test_to_num_branches():
    """``_to_num`` strips commas/percent and maps blanks / junk to None."""
    assert ec._to_num("4.7") == 4.7
    assert ec._to_num("8,300") == 8300.0
    assert ec._to_num("0.5%") == 0.5
    assert ec._to_num(None) is None
    assert ec._to_num("") is None
    assert ec._to_num("(NA)") is None
    assert ec._to_num("abc") is None


def test_parse_chart_table_timeseries():
    """A time-series chart keys rows by date, fills missing cells with None."""
    res = ec.parse_chart_table(_TS_TABLE, "civilian-unemployment-rate")
    assert res["table_id"] == "cps_rc_test"
    assert res["chart_title"] == "Civilian unemployment rate"
    rows = res["rows"]
    # Apr + May kept; empty <tr> and bad-month row dropped.
    assert len(rows) == 2
    apr = [r for r in rows if r["date"] == date(2006, 4, 1)][0]
    assert apr["total"] == 4.7
    assert apr["men_20_over"] == 4.2
    may = [r for r in rows if r["date"] == date(2006, 5, 1)][0]
    assert may["total"] == 4.6
    assert may["men_20_over"] is None  # blank cell
    # Declared series beyond the table's two columns are present and None.
    assert apr["hispanic"] is None


def test_parse_chart_table_industry():
    """An industry chart keys rows by industry and skips blank-industry rows."""
    res = ec.parse_chart_table(
        _INDUSTRY_TABLE, "employment-by-industry-monthly-changes"
    )
    rows = res["rows"]
    # Blank-industry row dropped; two real rows kept.
    assert len(rows) == 2
    mining = [r for r in rows if r["industry"] == "Mining and logging"][0]
    assert mining["employed"] == 606.0
    assert mining["net_change_1month"] == 3.0
    assert "date" not in mining
    construction = [r for r in rows if r["industry"] == "Construction"][0]
    assert construction["employed"] == 8300.0
    assert construction["net_change_1month"] == -5.0


def test_parse_chart_table_missing_table_raises():
    """A page without a data table raises OpenBBError."""
    with pytest.raises(OpenBBError, match="no data table"):
        ec.parse_chart_table(
            "<html><body><p>nope</p></body></html>", "civilian-unemployment-rate"
        )


def test_parse_chart_table_no_caption_uses_label():
    """Without a caption the chart title falls back to the spec label."""
    html = """
    <table class="regular">
    <thead><tr><th>Month</th><th>Percent</th></tr></thead>
    <tbody><tr><th>Apr 2006</th><td>18.6</td></tr></tbody>
    </table>
    """
    res = ec.parse_chart_table(html, "long-term-unemployed-share")
    assert res["chart_title"] == ec.CHART_SPECS["long-term-unemployed-share"]["label"]
    assert res["table_id"] == "empsit-chart-long-term-unemployed-share"
    assert res["rows"][0]["percent"] == 18.6


def test_fetch_and_parse_dispatch(monkeypatch):
    """``fetch_and_parse`` resolves the slug and parses the fetched HTML."""
    captured = {}

    def _fake(slug):
        captured["slug"] = slug
        return _TS_TABLE

    monkeypatch.setattr(ec, "fetch_chart_html", _fake)
    res = ec.fetch_and_parse("civilian-unemployment-rate")
    assert captured["slug"] == ec.CHART_SPECS["civilian-unemployment-rate"]["slug"]
    assert res["rows"]


def test_model_empty_rows_raises():
    """A chart fetcher raises EmptyDataError when no rows are parsed."""
    fetcher = ecm.EMPSIT_CHART_FETCHERS[
        ecm.empsit_model_name("civilian-unemployment-rate")
    ]
    query = fetcher.transform_query({})
    with pytest.raises(EmptyDataError):
        fetcher.transform_data(query, [])
