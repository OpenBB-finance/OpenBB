"""Tests for the BLS PPI Documents fetcher and index scraper."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_bls.models.ppi_documents as ppi_mod
from openbb_bls.models.ppi_documents import (
    BlsPpiDocumentsData,
    BlsPpiDocumentsFetcher,
    BlsPpiDocumentsQueryParams,
    _list_detailed_reports,
    _scrape_detailed_report_index,
)

_FIXTURES = Path(__file__).parent / "fixtures"
_INDEX_HTML = (_FIXTURES / "ppi_detailed_report_index.html").read_text()


class _FakeResponse:
    """Minimal requests.Response stand-in for HTML pages."""

    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code


class _FakeSession:
    """Minimal session stand-in with a configurable get() callback."""

    def __init__(self, text: str, status_code: int = 200):
        self._text = text
        self._status_code = status_code

    def get(self, url, headers=None, timeout=None):
        """Return the canned response without touching the network."""
        return _FakeResponse(self._text, self._status_code)


def _install_fake_session(monkeypatch, text: str, status_code: int = 200):
    """Patch get_requests_session at its source to return a fake session."""
    from openbb_core.provider.utils import helpers as helpers_mod

    monkeypatch.setattr(
        helpers_mod,
        "get_requests_session",
        lambda *a, **k: _FakeSession(text, status_code),
    )


@pytest.fixture(autouse=True)
def _clear_index_cache():
    """Drop the lru_cache on _scrape_detailed_report_index between tests."""
    _scrape_detailed_report_index.cache_clear()
    yield
    _scrape_detailed_report_index.cache_clear()


def test_query_params_year_defaults_to_none():
    """year defaults to None when not provided."""
    q = BlsPpiDocumentsQueryParams()
    assert q.year is None


def test_query_params_accepts_explicit_year():
    """year accepts an int and round-trips."""
    q = BlsPpiDocumentsQueryParams(year=2025)
    assert q.year == 2025


def test_scrape_index_parses_full_fixture(monkeypatch):
    """Index scraper yields one row per valid PDF, dedupes, drops bad months."""
    _install_fake_session(monkeypatch, _INDEX_HTML)
    docs = _scrape_detailed_report_index()
    assert isinstance(docs, tuple)
    urls = [d["url"] for d in docs]
    assert (
        "https://www.bls.gov/ppi/detailed-report/ppi-detailed-report-april-2026.pdf"
        in urls
    )
    assert (
        "https://www.bls.gov/ppi/detailed-report/ppi-detailed-report-march-2026.pdf"
        in urls
    )
    assert (
        "https://www.bls.gov/ppi/detailed-report/ppi-detailed-report-february-2026.pdf"
        in urls
    )
    assert "https://www.bls.gov/ppi/detailed-report/ppi-tables-january-2025.pdf" in urls
    assert len(urls) == len(set(urls))
    dates = [d["date"] for d in docs]
    assert dates == sorted(dates, reverse=True)
    for doc in docs:
        assert doc["category"] == "detailed_report"
        assert doc["format"] == "pdf"
        assert "PPI Detailed Report" in doc["name"]


def test_scrape_index_raises_on_non_200(monkeypatch):
    """Non-200 responses surface as OpenBBError."""
    _install_fake_session(monkeypatch, "", status_code=500)
    with pytest.raises(OpenBBError, match="HTTP 500"):
        _scrape_detailed_report_index()


def test_list_detailed_reports_no_filter_returns_copies(monkeypatch):
    """Year=None returns every cached row as an independent dict."""
    _install_fake_session(monkeypatch, _INDEX_HTML)
    rows = _list_detailed_reports(None)
    cached = _scrape_detailed_report_index()
    assert len(rows) == len(cached)
    rows[0]["name"] = "MUTATED"
    assert cached[0]["name"] != "MUTATED"


def test_list_detailed_reports_year_filter_applied(monkeypatch):
    """An explicit year filter restricts the result to that calendar year."""
    _install_fake_session(monkeypatch, _INDEX_HTML)
    rows = _list_detailed_reports(2025)
    assert rows
    assert all(r["date"].year == 2025 for r in rows)


def test_list_detailed_reports_year_filter_empty(monkeypatch):
    """A year with no PDFs returns an empty list (no exception here)."""
    _install_fake_session(monkeypatch, _INDEX_HTML)
    assert _list_detailed_reports(1999) == []


def test_fetcher_transform_query_coerces_dict():
    """transform_query produces a BlsPpiDocumentsQueryParams."""
    q = BlsPpiDocumentsFetcher.transform_query({"year": 2026})
    assert isinstance(q, BlsPpiDocumentsQueryParams)
    assert q.year == 2026


def test_fetcher_extract_data_uses_year_filter(monkeypatch):
    """extract_data delegates to _list_detailed_reports with the query year."""
    captured: list = []

    def _fake(year):
        captured.append(year)
        return [{"date": date(2025, 6, 1), "category": "detailed_report"}]

    monkeypatch.setattr(ppi_mod, "_list_detailed_reports", _fake)
    q = BlsPpiDocumentsFetcher.transform_query({"year": 2025})
    rows = BlsPpiDocumentsFetcher.extract_data(q, None)
    assert captured == [2025]
    assert rows[0]["date"] == date(2025, 6, 1)


def test_fetcher_transform_data_validates_rows(monkeypatch):
    """transform_data wraps each dict in a BlsPpiDocumentsData."""
    raw = [
        {
            "name": "PPI Detailed Report — April 2026",
            "url": "https://www.bls.gov/ppi/detailed-report/"
            "ppi-detailed-report-april-2026.pdf",
            "category": "detailed_report",
            "date": date(2026, 4, 1),
            "format": "pdf",
        }
    ]
    out = BlsPpiDocumentsFetcher.transform_data(
        BlsPpiDocumentsFetcher.transform_query({}), raw
    )
    assert len(out) == 1
    assert isinstance(out[0], BlsPpiDocumentsData)
    assert out[0].date == date(2026, 4, 1)


def test_fetcher_transform_data_raises_on_empty():
    """An empty input list raises EmptyDataError."""
    with pytest.raises(EmptyDataError):
        BlsPpiDocumentsFetcher.transform_data(
            BlsPpiDocumentsFetcher.transform_query({}), []
        )


def test_fetcher_end_to_end_no_filter(monkeypatch):
    """Full pipeline through the patched session returns validated rows."""
    _install_fake_session(monkeypatch, _INDEX_HTML)
    q = BlsPpiDocumentsFetcher.transform_query({})
    raw = BlsPpiDocumentsFetcher.extract_data(q, None)
    out = BlsPpiDocumentsFetcher.transform_data(q, raw)
    assert len(out) >= 3
    assert all(isinstance(r, BlsPpiDocumentsData) for r in out)


def test_fetcher_end_to_end_year_filter(monkeypatch):
    """Full pipeline with a year filter restricts to that calendar year."""
    _install_fake_session(monkeypatch, _INDEX_HTML)
    q = BlsPpiDocumentsFetcher.transform_query({"year": 2026})
    raw = BlsPpiDocumentsFetcher.extract_data(q, None)
    out = BlsPpiDocumentsFetcher.transform_data(q, raw)
    assert out
    assert all(r.date.year == 2026 for r in out)


def test_fetcher_end_to_end_year_filter_empty_raises(monkeypatch):
    """A year filter that matches nothing surfaces EmptyDataError."""
    _install_fake_session(monkeypatch, _INDEX_HTML)
    q = BlsPpiDocumentsFetcher.transform_query({"year": 1999})
    raw = BlsPpiDocumentsFetcher.extract_data(q, None)
    with pytest.raises(EmptyDataError):
        BlsPpiDocumentsFetcher.transform_data(q, raw)
