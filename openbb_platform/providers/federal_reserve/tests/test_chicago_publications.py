"""Tests for the Chicago Fed publications helpers and index model."""

import base64
from datetime import date
from unittest.mock import MagicMock

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.utils import (
    chicago as chicago_http,
    chicago_publications,
)


def _feed_entry(date_str: str, title: str, link: str, volume="", issue="") -> dict:
    """Build a raw NewsFeed entry."""
    return {
        "Date": date_str,
        "Title": title,
        "Volume": volume,
        "Issue": issue,
        "Url": f"https://www.chicagofed.org/landing/{title}",
        "PublicationLink": link,
    }


_AGLETTER_PAGES = {
    1: [
        _feed_entry(
            "20260514",
            "AgLetter: May 2026",
            "https://www.chicagofed.org/-/media/agletter/may-2026.pdf?sc_lang=en",
            issue="2012",
        ),
        _feed_entry("", "Unparseable", "https://x/skip.pdf"),
    ],
    2: [
        _feed_entry(
            "200902",
            "AgLetter: February 2009",
            "https://www.chicagofed.org/-/media/agletter/february-2009.pdf",
        ),
    ],
    3: [
        _feed_entry(
            "200902",
            "AgLetter: February 2009",
            "https://www.chicagofed.org/-/media/agletter/february-2009.pdf",
        ),
    ],
}
_EP_PAGES = {
    1: [
        _feed_entry(
            "2012",
            "Economic Perspectives 2012",
            "https://www.chicagofed.org/-/media/ep/ep2012.pdf?sc_lang=en",
        ),
    ],
}


class TestParseDate:
    """Tests for ``_parse_date``."""

    def test_full_date(self):
        """An eight-digit value parses to a full date."""
        assert chicago_publications._parse_date("20260514") == date(2026, 5, 14)

    def test_year_month(self):
        """A six-digit value defaults the day to one."""
        assert chicago_publications._parse_date("200902") == date(2009, 2, 1)

    def test_year_only(self):
        """A four-digit value defaults the month and day to one."""
        assert chicago_publications._parse_date("2012") == date(2012, 1, 1)

    def test_invalid_returns_none(self):
        """Empty, wrong-length, non-numeric, or out-of-range values return None."""
        assert chicago_publications._parse_date(None) is None
        assert chicago_publications._parse_date("") is None
        assert chicago_publications._parse_date("2026051") is None
        assert chicago_publications._parse_date("abcd") is None
        assert chicago_publications._parse_date("20261301") is None


class TestRecord:
    """Tests for ``_record``."""

    def test_builds_record_and_strips_query(self):
        """A valid entry maps to a record with the PDF query string stripped."""
        entry = _feed_entry(
            "20260514",
            "AgLetter: May 2026",
            "https://x/may-2026.pdf?sc_lang=en",
            issue="2012",
        )
        record = chicago_publications._record("agletter", entry)
        assert record["date"] == "2026-05-14"
        assert record["series"] == "agletter"
        assert record["url"] == "https://x/may-2026.pdf"
        assert record["issue"] == "2012"
        assert record["volume"] is None

    def test_missing_date_or_link_returns_none(self):
        """An unparseable date or missing link yields no record."""
        assert chicago_publications._record("agletter", _feed_entry("", "t", "u")) is (
            None
        )
        assert (
            chicago_publications._record("agletter", _feed_entry("20260101", "t", ""))
            is None
        )


class TestListPublications:
    """Tests for ``list_publications``."""

    def _patch_feed(self, monkeypatch, pages_by_series):
        """Patch ``post_newsfeed`` to serve canned per-series page windows."""
        guid_to_series = {
            spec["guid"]: name for name, spec in chicago_publications._SERIES.items()
        }

        def _post(series_id, page=1):
            series = guid_to_series[series_id]
            return pages_by_series.get(series, {}).get(page, [])

        monkeypatch.setattr(chicago_http, "post_newsfeed", _post)

    def test_single_series_pages_dedups_and_sorts(self, monkeypatch):
        """A single series walks pages, dedups, and sorts newest first."""
        self._patch_feed(monkeypatch, {"agletter": _AGLETTER_PAGES})
        catalog = chicago_publications.list_publications("agletter")
        assert [r["date"] for r in catalog] == ["2026-05-14", "2009-02-01"]
        assert all(r["series"] == "agletter" for r in catalog)

    def test_all_series_combined(self, monkeypatch):
        """With no series filter every series is enumerated."""
        self._patch_feed(
            monkeypatch,
            {"agletter": _AGLETTER_PAGES, "economic_perspectives": _EP_PAGES},
        )
        catalog = chicago_publications.list_publications(None)
        series = {r["series"] for r in catalog}
        assert "agletter" in series
        assert "economic_perspectives" in series

    def test_unknown_series_raises(self, monkeypatch):
        """An unknown series key raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            chicago_publications.list_publications("nope")


class TestFetchPublicationPdf:
    """Tests for ``fetch_publication_pdf``."""

    def _patch(self, monkeypatch, catalog):
        """Point the fetcher at a synthetic catalog and a fake PDF download."""
        monkeypatch.setattr(
            chicago_publications, "list_publications", lambda series=None: list(catalog)
        )
        monkeypatch.setattr(chicago_http, "get_bytes", lambda url: b"%PDF-1.7 fake")

    _CATALOG = [
        {
            "date": "2026-05-14",
            "series": "agletter",
            "title": "AgLetter: May 2026",
            "volume": None,
            "issue": "2012",
            "landing_url": "l",
            "url": "https://x/may-2026.pdf",
        },
        {
            "date": "2026-02-12",
            "series": "agletter",
            "title": "AgLetter: February 2026",
            "volume": None,
            "issue": "2011",
            "landing_url": "l",
            "url": "https://x/february-2026.pdf",
        },
    ]

    def test_latest_default(self, monkeypatch):
        """With no selector the newest issue is returned as a base64 PDF."""
        self._patch(monkeypatch, self._CATALOG)
        out = chicago_publications.fetch_publication_pdf("agletter")
        assert out["data_format"]["filename"] == "may-2026.pdf"
        assert base64.b64decode(out["content"]).startswith(b"%PDF")

    def test_select_by_date(self, monkeypatch):
        """A date prefix selects the matching issue."""
        self._patch(monkeypatch, self._CATALOG)
        out = chicago_publications.fetch_publication_pdf("agletter", date="2026-02")
        assert out["data_format"]["filename"] == "february-2026.pdf"

    def test_unknown_series_raises(self, monkeypatch):
        """An unknown series raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            chicago_publications.fetch_publication_pdf("nope")

    def test_empty_catalog_raises(self, monkeypatch):
        """An empty catalog raises ``OpenBBError``."""
        self._patch(monkeypatch, [])
        with pytest.raises(OpenBBError):
            chicago_publications.fetch_publication_pdf("agletter")

    def test_unknown_date_raises(self, monkeypatch):
        """A date with no match raises ``OpenBBError``."""
        self._patch(monkeypatch, self._CATALOG)
        with pytest.raises(OpenBBError):
            chicago_publications.fetch_publication_pdf("agletter", date="1999-01")


class TestPublicationsModel:
    """Tests for the publications index data model."""

    from openbb_federal_reserve.models.regional.chicago_publications import (
        FederalReserveChicagoPublicationsData as DataModel,
        FederalReserveChicagoPublicationsFetcher as Fetcher,
    )

    _CATALOG = [
        {
            "date": "2026-05-14",
            "series": "agletter",
            "title": "AgLetter: May 2026",
            "volume": None,
            "issue": "2012",
            "landing_url": "l",
            "url": "https://x/may-2026.pdf",
        },
        {
            "date": "2026-01-01",
            "series": "agletter",
            "title": "AgLetter: January 2026",
            "volume": None,
            "issue": "2010",
            "landing_url": "l",
            "url": "https://x/january-2026.pdf",
        },
    ]

    def _patch(self, monkeypatch):
        """Point the model at a synthetic catalog."""
        monkeypatch.setattr(
            chicago_publications,
            "list_publications",
            lambda series=None: list(self._CATALOG),
        )

    def test_filters_dates(self, monkeypatch):
        """The start and end date filters narrow the catalog."""
        self._patch(monkeypatch)
        query = self.Fetcher.transform_query(
            {"start_date": "2026-02-01", "end_date": "2026-12-31"}
        )
        rows = self.Fetcher.transform_data(
            query, self.Fetcher.extract_data(query, None)
        )
        assert all(isinstance(r, self.DataModel) for r in rows)
        assert [r.date for r in rows] == [date(2026, 5, 14)]

    def test_no_filter_returns_all(self, monkeypatch):
        """With no filters the full catalog is returned."""
        self._patch(monkeypatch)
        query = self.Fetcher.transform_query({})
        rows = self.Fetcher.transform_data(
            query, self.Fetcher.extract_data(query, None)
        )
        assert len(rows) == 2

    def test_empty_raises(self, monkeypatch):
        """An empty catalog raises ``EmptyDataError``."""
        monkeypatch.setattr(
            chicago_publications, "list_publications", lambda series=None: []
        )
        query = self.Fetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            self.Fetcher.extract_data(query, None)


class TestChicagoHttp:
    """Tests for the patchable Chicago HTTP helper."""

    def test_get_text_decodes_bom(self, monkeypatch):
        """``get_text`` strips a UTF-8 BOM from the decoded body."""
        response = MagicMock(status_code=200, content="hi".encode("utf-8-sig"))
        response.raise_for_status = MagicMock()
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: response,
        )
        assert chicago_http.get_text("https://x") == "hi"

    def test_get_bytes_falls_back_on_403(self, monkeypatch):
        """A 403 from make_request triggers the curl_cffi session fallback."""
        forbidden = MagicMock(status_code=403)
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: forbidden,
        )
        ok = MagicMock(status_code=200, content=b"data")
        ok.raise_for_status = MagicMock()
        session = MagicMock()
        session.get = MagicMock(return_value=ok)
        monkeypatch.setattr(chicago_http, "_get_session", lambda: session)
        assert chicago_http.get_bytes("https://x") == b"data"
        session.get.assert_called_once()

    def test_post_newsfeed_falls_back_on_403(self, monkeypatch):
        """A 403 on the NewsFeed POST triggers the session fallback."""
        forbidden = MagicMock(status_code=403)
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: forbidden,
        )
        ok = MagicMock(status_code=200)
        ok.raise_for_status = MagicMock()
        ok.json = MagicMock(return_value=[{"Title": "x"}])
        session = MagicMock()
        session.post = MagicMock(return_value=ok)
        monkeypatch.setattr(chicago_http, "_get_session", lambda: session)
        assert chicago_http.post_newsfeed("GUID", 1) == [{"Title": "x"}]
        session.post.assert_called_once()

    def test_reset_session(self, monkeypatch):
        """``reset_session`` drops the shared cached session handle."""
        from openbb_federal_reserve.utils import curl_session

        curl_session._sessions["chicago"] = object()
        chicago_http.reset_session()
        assert "chicago" not in curl_session._sessions

    def test_get_session_creates_curl_session(self, monkeypatch):
        """``_get_session`` lazily builds and caches a curl_cffi session."""
        import sys
        import types

        sentinel = object()
        fake_session_module = types.SimpleNamespace(
            Session=lambda impersonate=None: sentinel
        )
        fake_curl = types.ModuleType("curl_cffi")
        fake_curl.requests = fake_session_module
        monkeypatch.setitem(sys.modules, "curl_cffi", fake_curl)
        chicago_http.reset_session()
        assert chicago_http._get_session() is sentinel
        assert chicago_http._get_session() is sentinel
        chicago_http.reset_session()
