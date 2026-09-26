"""Unit tests for ``openbb_bls.utils.charts_common`` internals."""

from __future__ import annotations

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_bls.utils import charts_common as cc

_SPECS = {
    "ts-chart": {
        "slug": "ts",
        "label": "TS Label",
        "kind": "ts",
        "chart_type": "line",
        "fields": [["a", "A", "num"], ["b", "B", "num"]],
    },
    "xs-chart": {
        "slug": "xs",
        "label": "XS Label",
        "kind": "industry",
        "chart_type": "column",
        "fields": [["v", "V", "pct"]],
    },
}

_TS_TABLE = """
<table class="regular" id="t_test">
<caption>Trends caption</caption>
<thead><tr><th>Year</th><th>A</th><th>B</th></tr></thead>
<tbody>
  <tr><th>1987</th><td>100.0</td><td>50.0</td></tr>
  <tr></tr>
  <tr><th>1988</th><td>101.5</td><td></td></tr>
  <tr><th>not a year</th><td>9.9</td><td>1.0</td></tr>
</tbody>
</table>
"""

_XS_TABLE = """
<table class="regular" id="x_test">
<thead><tr><th>Industry</th><th>V</th></tr></thead>
<tbody>
  <tr><th>Mining</th><td>4.1</td></tr>
  <tr class="greenbar"><th>Mining</th><td>4.1</td></tr>
  <tr><th></th><td>1.0</td></tr>
  <tr><th>Utilities</th></tr>
</tbody>
</table>
"""


class _FakeResp:
    """Minimal ``requests.Response`` stand-in."""

    def __init__(self, content: bytes = b"", status_code: int = 200):
        self.content = content
        self.status_code = status_code


def test_decode_latin1_fallback():
    """``decode`` falls back to latin-1 when utf-8 fails."""
    assert "caf" in cc.decode("café".encode("latin-1"))
    assert cc.decode(b"plain") == "plain"


def test_make_html_fetcher_success_and_error(monkeypatch):
    """The shared fetcher decodes 200 responses and raises on non-200."""
    import requests

    fetch = cc.make_html_fetcher("https://example.test/base", maxsize=4)

    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResp(content="café".encode("latin-1"))
    )
    assert "caf" in fetch("ok-slug")

    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResp(status_code=500))
    with pytest.raises(OpenBBError, match="HTTP 500"):
        fetch("bad-slug")


def test_parse_month_branches():
    """``parse_month`` parses ``Mon YYYY`` and rejects junk / bad months."""
    assert cc.parse_month("Apr 2006") == date(2006, 4, 1)
    assert cc.parse_month("Sept 2006") == date(2006, 9, 1)
    assert cc.parse_month("nope") is None
    assert cc.parse_month("Xyz 2006") is None


def test_parse_quarter_branches():
    """``parse_quarter`` maps ``Qn YYYY`` to first-of-quarter; junk -> None."""
    assert cc.parse_quarter("Q1 2017") == date(2017, 1, 1)
    assert cc.parse_quarter("Q4 2017") == date(2017, 10, 1)
    assert cc.parse_quarter("nope") is None


def test_parse_year_branches():
    """``parse_year`` maps a 4-digit year to first-of-year; junk -> None."""
    assert cc.parse_year("1987") == date(1987, 1, 1)
    assert cc.parse_year("none") is None


def test_to_num_branches():
    """``to_num`` strips commas/percent and maps blanks / junk to None."""
    assert cc.to_num("100.0") == 100.0
    assert cc.to_num("4.1%") == 4.1
    assert cc.to_num("6,169.3") == 6169.3
    assert cc.to_num(None) is None
    assert cc.to_num("") is None
    assert cc.to_num("(NA)") is None
    assert cc.to_num("abc") is None


def test_parse_chart_table_timeseries():
    """Time-series parse keys by date, fills missing/short cells with None."""
    res = cc.parse_chart_table(_TS_TABLE, "ts-chart", _SPECS, "year", "test", "t-chart")
    assert res["table_id"] == "t_test"
    assert res["chart_title"] == "Trends caption"
    rows = res["rows"]
    assert len(rows) == 2  # blank <tr> + bad-year dropped
    y1987 = [r for r in rows if r["date"] == date(1987, 1, 1)][0]
    assert y1987["a"] == 100.0 and y1987["b"] == 50.0
    y1988 = [r for r in rows if r["date"] == date(1988, 1, 1)][0]
    assert y1988["b"] is None


def test_parse_chart_table_cross_section():
    """Cross-section parse keys by the spec's stub field; blank / dup / short handled."""
    res = cc.parse_chart_table(_XS_TABLE, "xs-chart", _SPECS, "year", "test", "x-chart")
    rows = res["rows"]
    # Blank-industry row dropped; the verbatim "greenbar" duplicate of Mining collapsed.
    assert len(rows) == 2
    mining = [r for r in rows if r["industry"] == "Mining"]
    assert len(mining) == 1 and mining[0]["v"] == 4.1 and "date" not in mining[0]
    # Utilities row has no value cell -> field is None.
    util = [r for r in rows if r["industry"] == "Utilities"][0]
    assert util["v"] is None


def test_parse_chart_table_missing_table_raises():
    """A page without a data table raises OpenBBError."""
    with pytest.raises(OpenBBError, match="no data table"):
        cc.parse_chart_table(
            "<html><body><p>x</p></body></html>",
            "ts-chart",
            _SPECS,
            "year",
            "test",
            "t-chart",
        )


def test_parse_chart_table_no_caption_uses_label():
    """Without a caption the chart title falls back to the spec label."""
    html = """
    <table class="regular">
    <thead><tr><th>Year</th><th>A</th><th>B</th></tr></thead>
    <tbody><tr><th>1987</th><td>100.0</td><td>50.0</td></tr></tbody>
    </table>
    """
    res = cc.parse_chart_table(html, "ts-chart", _SPECS, "year", "test", "t-chart")
    assert res["chart_title"] == "TS Label"
    assert res["table_id"] == "t-chart-ts-chart"
