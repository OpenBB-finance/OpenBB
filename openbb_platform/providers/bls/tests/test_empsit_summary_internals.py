"""Unit tests for ``openbb_bls.utils.empsit_summary`` + models."""

from __future__ import annotations

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_bls.models.empsit_summary as esm
from openbb_bls.utils import empsit_summary as es


class _FakeResp:
    """Minimal ``requests.Response`` stand-in."""

    def __init__(self, content: bytes = b"", status_code: int = 200):
        self.content = content
        self.status_code = status_code


_TABLE_A = """
<!DOCTYPE html><html><body>
<table class="regular" id="cps_empsit_sum">
<caption>HOUSEHOLD DATA Summary table A. Household data, seasonally adjusted</caption>
<thead><tr><th>Category</th><th>Apr. 2025</th><th>Feb. 2026</th>
<th>Mar. 2026</th><th>Apr. 2026</th><th>Change from: Mar. 2026- Apr. 2026</th></tr></thead>
<tbody>
  <tr><th>Employment status</th><td></td></tr>
  <tr><th>Civilian labor force ( 1 )</th><td>171,054</td><td>170,483</td>
      <td>170,087</td><td>169,995</td><td>-92</td></tr>
  <tr><th>Unemployment rate</th><td>4.2</td><td>4.4</td><td>4.3</td><td>4.3</td><td>0.0</td></tr>
  <tr><td></td></tr>
  <tr><th>Short row</th><td>1.0</td></tr>
</tbody>
</table>
</body></html>
"""

_TABLE_B = """
<table class="regular" id="ces_table10">
<thead><tr><th>Category</th><th>Apr. 2025</th><th>Feb. 2026</th>
<th>Mar. 2026 ( p )</th><th>Apr. 2026 ( p )</th></tr></thead>
<tbody>
  <tr><th>EMPLOYMENT BY SELECTED INDUSTRY</th><td></td></tr>
  <tr><th>Total nonfarm</th><td>108</td><td>-156</td><td>185</td><td>115</td></tr>
  <tr><th>Average hourly earnings</th><td>$36.12</td><td>$37.27</td>
      <td>$37.35</td><td>$37.41</td></tr>
</tbody>
</table>
"""


def test_fetch_summary_html_non_200_raises(monkeypatch):
    """A non-200 response raises OpenBBError."""
    import requests

    es.fetch_summary_html.cache_clear()
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResp(status_code=503))
    with pytest.raises(OpenBBError, match="HTTP 503"):
        es.fetch_summary_html("empsit.a")
    es.fetch_summary_html.cache_clear()


def test_fetch_summary_html_success_latin1(monkeypatch):
    """A 200 response decodes (latin-1 fallback) and returns the HTML."""
    import requests

    es.fetch_summary_html.cache_clear()
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResp(content="café".encode("latin-1"))
    )
    assert "caf" in es.fetch_summary_html("empsit.a")
    es.fetch_summary_html.cache_clear()


def test_clean_label_strips_footnotes():
    """Footnote markers and ``( p )`` are removed; whitespace collapses."""
    assert es._clean_label("Civilian population ( 1 )") == "Civilian population"
    assert es._clean_label("Mar. 2026 ( p )") == "Mar. 2026"
    assert es._clean_label("  Total   nonfarm ") == "Total nonfarm"


def test_to_value_branches():
    """``_to_value`` strips $, commas, % and maps blanks / junk to None."""
    assert es._to_value("171,054") == 171054.0
    assert es._to_value("$1,238.92") == 1238.92
    assert es._to_value("4.2") == 4.2
    assert es._to_value("-92") == -92.0
    assert es._to_value(None) is None
    assert es._to_value("") is None
    assert es._to_value("-") is None
    assert es._to_value("(NA)") is None
    assert es._to_value("n/a-ish") is None


def test_parse_summary_table_a_household():
    """Table A parses section + positional months + the change column."""
    res = es.parse_summary_table(_TABLE_A, "a")
    assert res["table_id"] == "cps_empsit_sum"
    assert "Household data" in res["title"]
    assert res["periods"] == ["Apr. 2025", "Feb. 2026", "Mar. 2026", "Apr. 2026"]
    rows = res["rows"]
    # Section header + blank row dropped; 3 data rows kept.
    assert len(rows) == 3
    clf = [r for r in rows if r["category"] == "Civilian labor force"][0]
    assert clf["section"] == "Employment status"
    assert clf["year_ago"] == 171054.0 and clf["latest"] == 169995.0
    assert clf["change_1_month"] == -92.0
    # Short row -> missing cells fill with None.
    short = [r for r in rows if r["category"] == "Short row"][0]
    assert short["year_ago"] == 1.0 and short["latest"] is None


def test_parse_summary_table_b_establishment():
    """Table B parses without a change column (dollar values coerced)."""
    res = es.parse_summary_table(_TABLE_B, "b")
    rows = res["rows"]
    earn = [r for r in rows if r["category"] == "Average hourly earnings"][0]
    assert earn["section"] == "EMPLOYMENT BY SELECTED INDUSTRY"
    assert earn["latest"] == 37.41
    assert earn["change_1_month"] is None


def test_parse_summary_table_missing_table_raises():
    """A page with no summary table raises OpenBBError."""
    with pytest.raises(OpenBBError, match="no data table"):
        es.parse_summary_table("<html><body><p>x</p></body></html>", "a")


def test_parse_summary_table_no_caption_or_thead_uses_label():
    """Without a caption / thead the title falls back and periods are empty."""
    html = """
    <table class="regular">
    <tbody><tr><th>Total</th><td>1.0</td><td>2.0</td><td>3.0</td><td>4.0</td><td>0.1</td></tr></tbody>
    </table>
    """
    res = es.parse_summary_table(html, "a")
    assert res["title"] == es.SUMMARY_SPECS["a"]["label"]
    assert res["periods"] == []
    assert res["table_id"] == "empsit-summary-a"
    assert res["rows"][0]["latest"] == 4.0


def test_parse_summary_table_skips_cell_less_row():
    """A ``<tr>`` with no ``th``/``td`` children is skipped."""
    html = """
    <table class="regular">
    <tbody>
      <tr></tr>
      <tr><th>Total</th><td>1.0</td><td>2.0</td><td>3.0</td><td>4.0</td></tr>
    </tbody>
    </table>
    """
    res = es.parse_summary_table(html, "a")
    assert len(res["rows"]) == 1
    assert res["rows"][0]["category"] == "Total"


def test_fetch_and_parse_dispatch(monkeypatch):
    """``fetch_and_parse`` resolves the slug and parses the fetched HTML."""
    captured = {}

    def _fake(slug):
        captured["slug"] = slug
        return _TABLE_A

    monkeypatch.setattr(es, "fetch_summary_html", _fake)
    res = es.fetch_and_parse("a")
    assert captured["slug"] == "empsit.a"
    assert res["rows"]


def test_model_empty_rows_raises():
    """A summary fetcher raises EmptyDataError when no rows are parsed."""
    fetcher = esm.EMPSIT_SUMMARY_FETCHERS[esm.empsit_summary_model_name("a")]
    query = fetcher.transform_query({})
    with pytest.raises(EmptyDataError):
        fetcher.transform_data(query, [])
