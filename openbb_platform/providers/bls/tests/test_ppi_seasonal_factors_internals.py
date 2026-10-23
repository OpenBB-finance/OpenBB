"""Unit tests for BLS PPI Seasonal Factors parser internals."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

import openbb_bls.models.ppi_seasonal_factors as psf

_FIXTURES = Path(__file__).parent / "fixtures"


class _FakeResponse:
    """Minimal ``requests.Response`` stand-in for HTML pages."""

    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code
        self.text = content.decode("utf-8", errors="replace")


class _FakeSession:
    """Session whose ``get`` always returns one canned response."""

    def __init__(self, response: _FakeResponse):
        self._response = response

    def get(self, url, *args, **kwargs) -> _FakeResponse:
        """Return the canned response regardless of URL."""
        return self._response


@pytest.fixture(autouse=True)
def _clear_wps_titles_cache():
    """Reset the _wps_titles memo so each test starts fresh."""
    psf._wps_titles.cache_clear()
    yield
    psf._wps_titles.cache_clear()


def _patch_session(monkeypatch, response: _FakeResponse) -> None:
    """Patch get_requests_session so _fetch_html_table uses a fake session."""
    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.get_requests_session",
        lambda *a, **k: _FakeSession(response),
    )


def test_cell_text_strips_nbsp():
    """_cell_text collapses NBSP and whitespace; None node yields empty string."""
    soup = BeautifulSoup("<td>\xa0 99.1 \xa0</td>", "lxml")
    assert psf._cell_text(soup.td) == "99.1"
    assert psf._cell_text(None) == ""


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("", None),
        ("-", None),
        ("(NA)", None),
        ("not-a-number", None),
        ("100.5", 100.5),
        ("-1.2", -1.2),
    ],
)
def test_to_float(raw, expected):
    """_to_float coerces numerics and maps BLS sentinels / junk to None."""
    assert psf._to_float(raw) == expected


def test_parse_5yr_rows_full():
    """_parse_5yr_rows extracts code/title blocks with 12 monthly factors each."""
    html = (_FIXTURES / "ppi_fdidsf.html").read_bytes()
    soup = BeautifulSoup(html, "lxml")
    data_table = soup.find_all("table")[1]
    rows = psf._parse_5yr_rows(data_table)

    # WPSFD4 has 2 valid 12-month years (the 3-cell year row is skipped),
    # WPSFD41 has 1 → (2 + 1) * 12 = 36 rows.
    assert len(rows) == 36
    first = rows[0]
    assert first["code"] == "WPSFD4"
    assert first["label"] == "Final demand"
    assert first["date"] == date(2024, 1, 1)
    assert first["seasonal_factor"] == 99.1

    # The dash cell in WPSFD41 May coerces to None.
    fd41 = [r for r in rows if r["code"] == "WPSFD41"]
    may = [r for r in fd41 if r["date"] == date(2025, 5, 1)][0]
    assert may["seasonal_factor"] is None


def test_fetch_html_table_5yr(monkeypatch):
    """_fetch_html_table dispatches non-seafac tables to the 5-year parser."""
    html = (_FIXTURES / "ppi_fdidsf.html").read_bytes()
    _patch_session(monkeypatch, _FakeResponse(html))
    result = psf._fetch_html_table(
        "ppi-fdidsf", "https://www.bls.gov/web/ppi/ppi-fdidsf.htm", "FD-ID label"
    )
    assert result["table_id"] == "ppi-fdidsf"
    assert result["table_name"] == "FD-ID label"
    assert len(result["rows"]) == 36
    assert all(r["table_id"] == "ppi-fdidsf" for r in result["rows"])


def test_fetch_html_table_non_200_raises(monkeypatch):
    """A non-200 response surfaces as OpenBBError."""
    from openbb_core.app.model.abstract.error import OpenBBError

    _patch_session(monkeypatch, _FakeResponse(b"", status_code=500))
    with pytest.raises(OpenBBError, match="HTTP 500"):
        psf._fetch_html_table("ppi-fdidsf", "https://x", "label")


def test_fetch_html_table_too_few_tables(monkeypatch):
    """A page with fewer than 2 tables yields an empty row set."""
    _patch_session(
        monkeypatch, _FakeResponse(b"<html><body><table></table></body></html>")
    )
    result = psf._fetch_html_table("ppi-fdidsf", "https://x", "label")
    assert result == {"rows": [], "table_id": "ppi-fdidsf", "table_name": "label"}


def test_parse_seafac_rows_no_year_returns_empty():
    """_parse_seafac_rows returns [] when the title carries no year token."""
    soup = BeautifulSoup("<table></table>", "lxml")
    assert psf._parse_seafac_rows(soup.table, "no year here") == []


def test_fetch_html_table_seafac_branch(monkeypatch):
    """_fetch_html_table routes ppi-seafac to the forecast parser."""
    html = (_FIXTURES / "ppi_seafac.html").read_bytes()
    _patch_session(monkeypatch, _FakeResponse(html))
    result = psf._fetch_html_table(
        "ppi-seafac", "https://www.bls.gov/web/ppi/ppi-seafac.htm", "Forecast label"
    )
    assert result["table_id"] == "ppi-seafac"
    assert len(result["rows"]) > 0
    assert all(r["table_id"] == "ppi-seafac" for r in result["rows"])


def test_wps_titles_missing_cache(monkeypatch):
    """_wps_titles returns an empty map when the metadata cache is unavailable."""
    from openbb_bls.utils.metadata._core import BlsMetadata

    def _raise(self, category):
        raise FileNotFoundError("no cache")

    monkeypatch.setattr(BlsMetadata, "get_series", _raise)
    titles = psf._wps_titles()
    assert titles == {}
    # Second call hits the memo branch.
    assert psf._wps_titles() == {}


def test_wps_titles_skips_none_rows(monkeypatch):
    """_wps_titles skips rows whose series_id or title is None and strips prefixes."""
    from openbb_bls.utils.metadata._core import BlsMetadata

    class _StubDF:
        def __init__(self, data):
            self._data = data

        def __getitem__(self, key):
            return self._data[key]

    stub = _StubDF(
        {
            "series_id": ["WPS011", None, "WPS012"],
            "series_title": [
                "PPI Commodity data for Farm products-Fruits, seasonally adjusted",
                "orphan title",
                None,
            ],
        }
    )
    monkeypatch.setattr(BlsMetadata, "get_series", lambda self, category: stub)
    titles = psf._wps_titles()
    assert titles == {"WPS011": "Farm products-Fruits"}


def test_fetcher_fd_id_end_to_end(monkeypatch):
    """BlsPpiSeasonalFactorsFetcher resolves fd_id through the 5-year parser."""
    html = (_FIXTURES / "ppi_fdidsf.html").read_bytes()
    _patch_session(monkeypatch, _FakeResponse(html))
    fetcher = psf.BlsPpiSeasonalFactorsFetcher
    query = fetcher.transform_query({"category": "fd_id"})
    data = fetcher.extract_data(query, None)
    rows = fetcher.transform_data(query, data)
    assert len(rows) == 36
    assert rows[0].code == "WPSFD4"


def test_fetcher_empty_raises(monkeypatch):
    """transform_data raises EmptyDataError when no rows parse."""
    from openbb_core.provider.utils.errors import EmptyDataError

    fetcher = psf.BlsPpiSeasonalFactorsFetcher
    query = fetcher.transform_query({"category": "fd_id"})
    with pytest.raises(EmptyDataError):
        fetcher.transform_data(query, {"rows": [], "table_id": "ppi-fdidsf"})
