"""Tests for the KC Fed Agricultural Bulletin helpers and commands."""

import base64
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.utils import (
    kansas_city as kc_http,
    kansas_city_publications,
)


class _FakeResponse:
    """Minimal stand-in for a curl_cffi response."""

    def __init__(self, status_code: int, content: bytes):
        self.status_code = status_code
        self.content = content

    def raise_for_status(self):
        """Raise for non-2xx responses."""
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class _FakeSession:
    """A fake session whose data fetch 403s once, then succeeds."""

    def __init__(self, payloads):
        self._payloads = list(payloads)
        self.warmups = 0

    def get(self, url, headers=None, timeout=None):
        """Return the warmup page, then queued payloads in order."""
        if url.endswith("kansascityfed.org/"):
            self.warmups += 1
            return _FakeResponse(200, b"<html></html>")
        return self._payloads.pop(0)


class TestSession:
    """Tests for session warm-up and the 403 retry."""

    def test_get_session_warms_up_once(self, monkeypatch):
        """``_get_session`` builds and warms a curl_cffi session once."""
        kc_http.reset_session()
        session = _FakeSession([])
        monkeypatch.setattr("curl_cffi.requests.Session", lambda **_k: session)
        first = kc_http._get_session()
        assert kc_http._get_session() is first
        assert session.warmups == 1
        kc_http.reset_session()

    def test_fetch_retries_once_on_403(self, monkeypatch):
        """A 403 triggers one session reset and retry."""
        session = _FakeSession([_FakeResponse(403, b""), _FakeResponse(200, b"ok")])
        resets: list[int] = []
        monkeypatch.setattr(kc_http, "_get_session", lambda: session)
        monkeypatch.setattr(kc_http, "reset_session", lambda: resets.append(1))
        assert kc_http.fetch_kansas_city("https://x/data.csv") == b"ok"
        assert resets == [1]


_LISTING_HTML = (
    '<a href="/documents/16478/KCFedAgBulletinQ12026.pdf">x</a>'
    '<a href="/documents/15006/KCFedAgBulletinQ42025.pdf">x</a>'
    '<a href="/Agriculture/documents/11189/AgBulletin_SecondQuarter2025.pdf">x</a>'
    '<a href="/Agriculture/documents/9359/Q422_Ag_Bulletin.pdf">x</a>'
    '<a href="/Agriculture/documents/8620/Ag-Bulletin-2021Q4.pdf">x</a>'
    '<a href="/Agriculture/documents/8256/archive-about-afdb.pdf">x</a>'
)


def _fetch(url, *args, **kwargs):
    """Path-aware fake: listing HTML for the landing page, PDF bytes otherwise."""
    if url.endswith("agricultural-data-and-indicators/"):
        return _LISTING_HTML.encode("utf-8")
    return b"%PDF-1.7 fake bulletin"


class TestParseQuarterYear:
    """Tests for the filename quarter/year parser."""

    def test_quarter_then_year(self):
        """A ``Q<q>-<year>`` filename parses to that quarter and year."""
        assert kansas_city_publications._parse_quarter_year(
            "Ag-Bulletin-Q1-2024.pdf"
        ) == (
            2024,
            1,
        )

    def test_year_then_quarter(self):
        """A ``<year>Q<q>`` filename parses to that year and quarter."""
        assert kansas_city_publications._parse_quarter_year(
            "Ag-Bulletin-2021Q4.pdf"
        ) == (
            2021,
            4,
        )

    def test_worded_quarter(self):
        """A worded quarter resolves to its number."""
        assert kansas_city_publications._parse_quarter_year(
            "AgBulletin_SecondQuarter2025.pdf"
        ) == (2025, 2)

    def test_two_digit_year(self):
        """A ``Q<q><yy>`` filename resolves the two-digit year."""
        assert kansas_city_publications._parse_quarter_year("Q422_Ag_Bulletin.pdf") == (
            2022,
            4,
        )

    def test_no_quarter_returns_none(self):
        """A filename without a quarter is not classifiable."""
        assert (
            kansas_city_publications._parse_quarter_year("archive-about-afdb.pdf")
            is None
        )


class TestListAgBulletins:
    """Tests for ``list_ag_bulletins``."""

    def test_classifies_dedups_and_sorts(self, monkeypatch):
        """The catalog classifies links, skips junk, and sorts newest first."""
        monkeypatch.setattr(kansas_city_publications, "fetch_kansas_city", _fetch)
        catalog = kansas_city_publications.list_ag_bulletins()
        dates = [record["date"] for record in catalog]
        assert dates == [
            "2026-01-01",
            "2025-10-01",
            "2025-04-01",
            "2022-10-01",
            "2021-10-01",
        ]
        assert not any("afdb" in record["url"] for record in catalog)
        assert catalog[0]["title"] == "Agricultural Bulletin Q1 2026"
        assert catalog[0]["url"].startswith("https://www.kansascityfed.org/documents")


class TestFetchAgBulletinPdf:
    """Tests for ``fetch_ag_bulletin_pdf``."""

    def test_latest(self, monkeypatch):
        """The latest bulletin downloads as a base64 PDF payload."""
        monkeypatch.setattr(kansas_city_publications, "fetch_kansas_city", _fetch)
        out = kansas_city_publications.fetch_ag_bulletin_pdf()
        assert out["data_format"]["filename"] == "KC_AgBulletin_2026-01-01.pdf"
        assert base64.b64decode(out["content"]).startswith(b"%PDF")

    def test_specific_date(self, monkeypatch):
        """A requested quarter selects that bulletin."""
        monkeypatch.setattr(kansas_city_publications, "fetch_kansas_city", _fetch)
        out = kansas_city_publications.fetch_ag_bulletin_pdf(date="2025-10")
        assert out["data_format"]["filename"] == "KC_AgBulletin_2025-10-01.pdf"

    def test_unknown_date_raises(self, monkeypatch):
        """A missing quarter raises ``OpenBBError``."""
        monkeypatch.setattr(kansas_city_publications, "fetch_kansas_city", _fetch)
        with pytest.raises(OpenBBError):
            kansas_city_publications.fetch_ag_bulletin_pdf(date="1999-01")

    def test_no_catalog_raises(self, monkeypatch):
        """An empty catalog raises ``OpenBBError``."""
        monkeypatch.setattr(kansas_city_publications, "list_ag_bulletins", list)
        with pytest.raises(OpenBBError):
            kansas_city_publications.fetch_ag_bulletin_pdf()


class TestPublicationsIndex:
    """Tests for the discovery index data model."""

    _CATALOG = [
        {
            "date": "2026-01-01",
            "year": 2026,
            "quarter": 1,
            "title": "Agricultural Bulletin Q1 2026",
            "url": "https://x/q12026.pdf",
        },
        {
            "date": "2025-10-01",
            "year": 2025,
            "quarter": 4,
            "title": "Agricultural Bulletin Q4 2025",
            "url": "https://x/q42025.pdf",
        },
    ]

    def _patch(self, monkeypatch):
        """Point the index model at a synthetic catalog."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.kansas_city_publications.list_ag_bulletins",
            lambda: list(self._CATALOG),
        )

    def test_filters_start_date(self, monkeypatch):
        """The start_date filter narrows the catalog."""
        from openbb_federal_reserve.models.regional.kansas_city_publications import (
            FederalReserveKansasCityPublicationsData as DataModel,
            FederalReserveKansasCityPublicationsFetcher as Fetcher,
        )

        self._patch(monkeypatch)
        query = Fetcher.transform_query({"start_date": "2026-01-01"})
        rows = Fetcher.transform_data(query, Fetcher.extract_data(query, None))
        assert all(isinstance(r, DataModel) for r in rows)
        assert [r.date for r in rows] == [date(2026, 1, 1)]

    def test_filters_end_date(self, monkeypatch):
        """The end_date filter narrows the catalog."""
        from openbb_federal_reserve.models.regional.kansas_city_publications import (
            FederalReserveKansasCityPublicationsFetcher as Fetcher,
        )

        self._patch(monkeypatch)
        query = Fetcher.transform_query({"end_date": "2025-12-31"})
        rows = Fetcher.transform_data(query, Fetcher.extract_data(query, None))
        assert [r.date for r in rows] == [date(2025, 10, 1)]

    def test_no_filter_returns_all(self, monkeypatch):
        """With no filters the full catalog is returned."""
        from openbb_federal_reserve.models.regional.kansas_city_publications import (
            FederalReserveKansasCityPublicationsFetcher as Fetcher,
        )

        self._patch(monkeypatch)
        query = Fetcher.transform_query({})
        rows = Fetcher.transform_data(query, Fetcher.extract_data(query, None))
        assert len(rows) == 2

    def test_empty_raises(self, monkeypatch):
        """An empty catalog raises ``EmptyDataError``."""
        from openbb_federal_reserve.models.regional.kansas_city_publications import (
            FederalReserveKansasCityPublicationsFetcher as Fetcher,
        )

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.kansas_city_publications.list_ag_bulletins",
            list,
        )
        query = Fetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            Fetcher.extract_data(query, None)
