"""Unit tests for ``openbb_bls.utils.productivity_charts`` internals."""

from __future__ import annotations

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_bls.models.productivity_charts as pcm
from openbb_bls.utils import productivity_charts as pc


class _FakeResp:
    """Minimal ``requests.Response`` stand-in."""

    def __init__(self, content: bytes = b"", status_code: int = 200):
        self.content = content
        self.status_code = status_code


_TS_TABLE = """
<!DOCTYPE html><html><body>
<table class="regular" id="msp_rc_test">
<caption><span class="tableTitle">Output, hours, and productivity indexes</span></caption>
<thead><tr><th>Quarter</th><th>Output</th><th>Hours worked</th></tr></thead>
<tbody>
  <tr><th><p>Q1 2017</p></th><td>98.631</td><td>99.194</td></tr>
  <tr></tr>
  <tr><th><p>Q2 2017</p></th><td>99.309</td><td></td></tr>
  <tr><th><p>not a quarter</p></th><td>9.9</td><td>1.0</td></tr>
</tbody>
</table>
</body></html>
"""

_SECTOR_TABLE = """
<table class="regular" id="msp_rc_sector">
<thead><tr>
  <th>Sector</th><th>Business</th><th>Nonfarm business</th>
</tr></thead>
<tbody>
  <tr><th>Labor productivity (output per hour)</th><td>2.9</td><td>2.9</td></tr>
  <tr><th></th><td>1</td><td>2</td></tr>
  <tr><th>Output</th><td>3.4</td><td>3.3</td></tr>
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


def test_parse_quarter_branches():
    """``_parse_quarter`` maps ``Qn YYYY`` to a first-of-quarter date and rejects junk."""
    assert pc._parse_quarter("Q1 2017") == date(2017, 1, 1)
    assert pc._parse_quarter("Q2 2017") == date(2017, 4, 1)
    assert pc._parse_quarter("Q3 2017") == date(2017, 7, 1)
    assert pc._parse_quarter("Q4 2017") == date(2017, 10, 1)
    assert pc._parse_quarter("nope") is None


def test_to_num_branches():
    """``_to_num`` strips commas/percent and maps blanks / junk to None."""
    assert pc._to_num("98.631") == 98.631
    assert pc._to_num("1,234.5") == 1234.5
    assert pc._to_num("2.9%") == 2.9
    assert pc._to_num(None) is None
    assert pc._to_num("") is None
    assert pc._to_num("(NA)") is None
    assert pc._to_num("abc") is None


def test_parse_chart_table_timeseries():
    """A time-series chart keys rows by date, fills missing cells with None."""
    res = pc.parse_chart_table(_TS_TABLE, "nonfarm-business-indexes")
    assert res["table_id"] == "msp_rc_test"
    assert res["chart_title"] == "Output, hours, and productivity indexes"
    rows = res["rows"]
    # Q1 + Q2 kept; empty <tr> and bad-quarter row dropped.
    assert len(rows) == 2
    q1 = [r for r in rows if r["date"] == date(2017, 1, 1)][0]
    assert q1["output"] == 98.631
    assert q1["hours_worked"] == 99.194
    q2 = [r for r in rows if r["date"] == date(2017, 4, 1)][0]
    assert q2["hours_worked"] is None  # blank cell
    # Declared series beyond the table's columns are present and None.
    assert q1["labor_productivity"] is None


def test_parse_chart_table_sector():
    """The sector chart keys rows by measure and skips blank-measure rows."""
    res = pc.parse_chart_table(_SECTOR_TABLE, "by-sector")
    rows = res["rows"]
    # Blank-measure row dropped; two real rows kept.
    assert len(rows) == 2
    lp = [r for r in rows if r["measure"].startswith("Labor productivity")][0]
    assert lp["business"] == 2.9
    assert lp["nonfarm_business"] == 2.9
    assert "date" not in lp
    output = [r for r in rows if r["measure"] == "Output"][0]
    assert output["business"] == 3.4


def test_parse_chart_table_missing_table_raises():
    """A page without a data table raises OpenBBError."""
    with pytest.raises(OpenBBError, match="no data table"):
        pc.parse_chart_table(
            "<html><body><p>nope</p></body></html>", "nonfarm-business-indexes"
        )


def test_parse_chart_table_no_caption_uses_label():
    """Without a caption the chart title falls back to the spec label."""
    html = """
    <table class="regular">
    <thead><tr><th>Quarter</th><th>Output</th></tr></thead>
    <tbody><tr><th>Q1 2017</th><td>98.6</td></tr></tbody>
    </table>
    """
    res = pc.parse_chart_table(html, "manufacturing-indexes")
    assert res["chart_title"] == pc.CHART_SPECS["manufacturing-indexes"]["label"]
    assert res["table_id"] == "productivity-chart-manufacturing-indexes"
    assert res["rows"][0]["output"] == 98.6


def test_fetch_and_parse_dispatch(monkeypatch):
    """``fetch_and_parse`` resolves the slug and parses the fetched HTML."""
    captured = {}

    def _fake(slug):
        captured["slug"] = slug
        return _TS_TABLE

    monkeypatch.setattr(pc, "fetch_chart_html", _fake)
    res = pc.fetch_and_parse("nonfarm-business-indexes")
    assert captured["slug"] == pc.CHART_SPECS["nonfarm-business-indexes"]["slug"]
    assert res["rows"]


def test_model_empty_rows_raises():
    """A chart fetcher raises EmptyDataError when no rows are parsed."""
    fetcher = pcm.PRODUCTIVITY_CHART_FETCHERS[
        pcm.productivity_model_name("nonfarm-business-indexes")
    ]
    query = fetcher.transform_query({})
    with pytest.raises(EmptyDataError):
        fetcher.transform_data(query, [])
