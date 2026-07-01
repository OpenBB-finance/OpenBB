"""Tests for the Atlanta Fed publication helpers, index model, and commands."""

import base64
import json
from datetime import date
from unittest.mock import MagicMock

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.atlanta_publications import (
    FederalReserveAtlantaPublicationsData,
    FederalReserveAtlantaPublicationsFetcher,
)
from openbb_federal_reserve.utils import atlanta_publications as ap

_BIE_HTML = (
    '<a href="/-/media/Project/Atlanta/FRBA/Documents/research/inflationproject'
    '/bie/2026/06/2026-06-monthly-chart-pack.pdf">x</a>'
    '<a href="/-/media/Project/Atlanta/FRBA/Documents/research/inflationproject'
    '/bie/2026/05/2026-05-monthly-chart-pack.pdf">x</a>'
)
_SBU_HTML = (
    '<a href="/-/media/Project/Atlanta/FRBA/Documents/datafiles/research/surveys'
    '/business-uncertainty/monthly-report/2026/2026-06.pdf">x</a>'
    '<a href="/-/media/Project/Atlanta/FRBA/Documents/datafiles/research/surveys'
    '/business-uncertainty/monthly-report/2026/2026-05.pdf">x</a>'
)
_WP_ITEMS = [
    {
        "Title": "The Anatomy  of Polarization",
        "Date": "2026-06-22T14:43:00",
        "Authors": [{"FullName": "Fabio  Cerina"}, {"FullName": "Elisa  Dienesch"}],
        "Url": (
            "https://www.atlantafed.org/research-and-data/publications/working-papers"
            "/2026/06/22/07-anatomy-of-polarization"
        ),
    }
]
_WP_PAGE_HTML = (
    '<a href="/-/media/Project/Atlanta/FRBA/Documents/research/publication'
    '/working-paper/2026/06/22/07-anatomy-of-polarization.pdf">PDF</a>'
)


def _json_response(payload: dict) -> MagicMock:
    """Build a JSON response carrying the working-papers feed payload."""
    response = MagicMock()
    response.headers = {"Content-Type": "application/json; charset=utf-8"}
    response.json = MagicMock(return_value=payload)
    response.raise_for_status = MagicMock()
    return response


def _html_response(text: str) -> MagicMock:
    """Build a text/PDF response with the given body."""
    response = MagicMock()
    response.headers = {"Content-Type": "text/html"}
    response.text = text
    response.content = b"%PDF-1.7 fake atlanta pdf"
    response.raise_for_status = MagicMock()
    return response


def _make_request(url, *args, **kwargs):
    """Path-aware fake covering listings, the WP feed, landing pages, and PDFs."""
    if url.endswith("business-inflation-expectations"):
        return _html_response(_BIE_HTML)
    if url.endswith("business-uncertainty"):
        return _html_response(_SBU_HTML)
    if "getFilteredResults" in url:
        if "PageNumber=1" in url:
            return _json_response({"FilteredFeedItemsJson": json.dumps(_WP_ITEMS)})
        return _json_response({"FilteredFeedItemsJson": json.dumps([])})
    if url.endswith("07-anatomy-of-polarization"):
        return _html_response(_WP_PAGE_HTML)
    return _html_response("")


@pytest.fixture(autouse=True)
def _patch_make_request(monkeypatch):
    """Route every helper request through the path-aware fake."""
    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.make_request", _make_request
    )


class TestIndexListing:
    """Tests for the BIE and SBU listing-page indexers."""

    def test_bie_chart_pack(self):
        """The BIE listing classifies chart-pack links, newest first."""
        catalog = ap.list_publications("bie_chart_pack")
        assert [r["id"] for r in catalog] == [
            "bie_chart_pack_2026-06",
            "bie_chart_pack_2026-05",
        ]
        assert catalog[0]["title"] == "BIE Monthly Chart Pack June 2026"
        assert catalog[0]["url"].endswith("2026-06-monthly-chart-pack.pdf")

    def test_sbu_monthly_report(self):
        """The SBU listing classifies monthly-report links, newest first."""
        catalog = ap.list_publications("sbu_monthly_report")
        assert [r["date"] for r in catalog] == ["2026-06-01", "2026-05-01"]
        assert catalog[0]["url"].endswith("2026-06.pdf")


class TestIndexWorkingPapers:
    """Tests for the Working Papers feed indexer."""

    def test_paginates_and_classifies(self):
        """The feed pages until empty and classifies authors and slug id."""
        catalog = ap.list_publications("working_paper")
        assert len(catalog) == 1
        record = catalog[0]
        assert record["id"] == "07-anatomy-of-polarization"
        assert record["date"] == "2026-06-22"
        assert record["title"] == "The Anatomy of Polarization"
        assert record["authors"] == "Fabio Cerina, Elisa Dienesch"

    def test_paginates_skips_missing_url_and_stops_on_empty(self, monkeypatch):
        """A full first page advances, items without a Url skip, an empty page stops."""
        from openbb_federal_reserve.utils.atlanta_publications import (
            _WORKING_PAPERS_PAGE_SIZE,
        )

        def _page(prefix, count):
            """Build a full feed page of items with derived URLs."""
            return [
                {
                    "Title": f"{prefix} {index}",
                    "Date": "2026-01-01T00:00:00",
                    "Authors": [],
                    "Url": (
                        "https://www.atlantafed.org/research-and-data/publications"
                        f"/working-papers/2026/01/01/{prefix}-{index:02d}-paper"
                    ),
                }
                for index in range(count)
            ]

        page_one = _page("a", _WORKING_PAPERS_PAGE_SIZE)
        page_two = _page("b", _WORKING_PAPERS_PAGE_SIZE)
        page_two[0]["Url"] = ""

        def _request(url, *args, **kwargs):
            """Serve two full pages then an empty page; one page-two item has no Url."""
            if "getFilteredResults" in url:
                if "PageNumber=1" in url:
                    return _json_response(
                        {"FilteredFeedItemsJson": json.dumps(page_one)}
                    )
                if "PageNumber=2" in url:
                    return _json_response(
                        {"FilteredFeedItemsJson": json.dumps(page_two)}
                    )
                return _json_response({"FilteredFeedItemsJson": json.dumps([])})
            if "/working-papers/" in url:
                slug = url.rstrip("/").rsplit("/", 1)[-1]
                return _html_response(
                    '<a href="/-/media/Project/Atlanta/FRBA/Documents/research'
                    f'/publication/working-paper/2026/01/01/{slug}.pdf">PDF</a>'
                )
            return _make_request(url, *args, **kwargs)

        monkeypatch.setattr("openbb_core.provider.utils.helpers.make_request", _request)
        catalog = ap.list_publications("working_paper")
        assert len(catalog) == 2 * _WORKING_PAPERS_PAGE_SIZE - 1
        assert all(r["url"].endswith(".pdf") for r in catalog)

    def test_non_json_page_breaks(self, monkeypatch):
        """A non-JSON page stops pagination without raising."""

        def _request(url, *args, **kwargs):
            """Return an HTML error page for the working-papers feed."""
            if "getFilteredResults" in url:
                return _html_response("<html>error</html>")
            return _make_request(url, *args, **kwargs)

        monkeypatch.setattr("openbb_core.provider.utils.helpers.make_request", _request)
        assert ap.list_publications("working_paper") == []


class TestListPublicationsMerged:
    """Tests for the merged catalog."""

    def test_all_series_merged_newest_first(self):
        """With no series filter every archive plus GDPNow slides merges."""
        catalog = ap.list_publications()
        series = {r["series"] for r in catalog}
        assert series == {
            "bie_chart_pack",
            "sbu_monthly_report",
            "working_paper",
            "gdpnow_slides",
        }
        assert catalog == sorted(catalog, key=lambda r: r["date"], reverse=True)

    def test_gdpnow_slides_folded_in(self):
        """The static GDPNow slide deck is folded in as a catalog record."""
        catalog = ap.list_publications()
        slides = [r for r in catalog if r["series"] == "gdpnow_slides"]
        assert len(slides) == 1
        assert slides[0]["title"] == "GDPNow Real GDP Tracking Slides"
        assert slides[0]["url"] == ap.GDPNOW_SLIDES_URL
        assert slides[0]["url"].endswith("RealGDPTrackingSlides.pdf")


class TestFetchPublicationPdf:
    """Tests for ``fetch_publication_pdf``."""

    def test_latest_bie(self):
        """With no selector the newest BIE chart pack downloads."""
        out = ap.fetch_publication_pdf(series="bie_chart_pack")
        assert out["data_format"]["filename"] == "Atlanta_bie_chart_pack_2026-06.pdf"
        assert base64.b64decode(out["content"]).startswith(b"%PDF")

    def test_by_date_sbu(self):
        """A date selects that month's SBU report."""
        out = ap.fetch_publication_pdf(series="sbu_monthly_report", date="2026-05")
        assert out["data_format"]["filename"] == (
            "Atlanta_sbu_monthly_report_2026-05.pdf"
        )

    def test_by_date_bie(self):
        """A date selects the matching BIE chart pack."""
        out = ap.fetch_publication_pdf(date="2026-05", series="bie_chart_pack")
        assert out["data_format"]["filename"] == "Atlanta_bie_chart_pack_2026-05.pdf"

    def test_working_paper_scrapes_landing_page(self):
        """A working paper resolves its PDF from the landing page."""
        out = ap.fetch_publication_pdf(series="working_paper")
        assert out["data_format"]["filename"] == "Atlanta_working_paper_2026-06.pdf"
        assert base64.b64decode(out["content"]).startswith(b"%PDF")

    def test_working_paper_no_pdf_raises(self, monkeypatch):
        """A landing page without a PDF link raises ``OpenBBError``."""

        def _request(url, *args, **kwargs):
            """Serve a landing page lacking any PDF link."""
            if url.endswith("07-anatomy-of-polarization"):
                return _html_response("<html>no pdf here</html>")
            return _make_request(url, *args, **kwargs)

        monkeypatch.setattr("openbb_core.provider.utils.helpers.make_request", _request)
        with pytest.raises(OpenBBError):
            ap.fetch_publication_pdf(series="working_paper")

    def test_unknown_date_raises(self):
        """An unknown date raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            ap.fetch_publication_pdf(date="1999-01", series="bie_chart_pack")

    def test_empty_catalog_raises(self, monkeypatch):
        """An empty catalog raises ``OpenBBError``."""
        monkeypatch.setattr(ap, "list_publications", lambda series=None: [])
        with pytest.raises(OpenBBError):
            ap.fetch_publication_pdf(series="bie_chart_pack")


class TestPublicationsIndexModel:
    """Tests for the discovery index data model."""

    _CATALOG = [
        {
            "series": "working_paper",
            "id": "07-anatomy",
            "date": "2026-06-22",
            "title": "Anatomy",
            "url": "https://x/anatomy.pdf",
            "authors": "Fabio Cerina",
        },
        {
            "series": "bie_chart_pack",
            "id": "bie_chart_pack_2026-06",
            "date": "2026-06-01",
            "title": "BIE June 2026",
            "url": "https://x/bie.pdf",
            "authors": None,
        },
        {
            "series": "sbu_monthly_report",
            "id": "sbu_monthly_report_2025-01",
            "date": "2025-01-01",
            "title": "SBU January 2025",
            "url": "https://x/sbu.pdf",
            "authors": None,
        },
    ]

    def _patch(self, monkeypatch):
        """Point the index model at a synthetic catalog."""
        monkeypatch.setattr(
            ap, "list_publications", lambda series=None: list(self._CATALOG)
        )

    def test_filters_start_and_end_date(self, monkeypatch):
        """The start_date and end_date filters narrow the catalog."""
        self._patch(monkeypatch)
        query = FederalReserveAtlantaPublicationsFetcher.transform_query(
            {"start_date": "2026-01-01", "end_date": "2026-06-15"}
        )
        rows = FederalReserveAtlantaPublicationsFetcher.transform_data(
            query, FederalReserveAtlantaPublicationsFetcher.extract_data(query, None)
        )
        assert all(isinstance(r, FederalReserveAtlantaPublicationsData) for r in rows)
        assert [r.title for r in rows] == ["BIE June 2026"]
        assert rows[0].date == date(2026, 6, 1)
        assert not hasattr(rows[0], "id")

    def test_no_filter_returns_all(self, monkeypatch):
        """With no filters the full catalog is returned."""
        self._patch(monkeypatch)
        query = FederalReserveAtlantaPublicationsFetcher.transform_query({})
        rows = FederalReserveAtlantaPublicationsFetcher.transform_data(
            query, FederalReserveAtlantaPublicationsFetcher.extract_data(query, None)
        )
        assert len(rows) == 3

    def test_empty_raises(self, monkeypatch):
        """An empty catalog raises ``EmptyDataError``."""
        monkeypatch.setattr(ap, "list_publications", lambda series=None: [])
        query = FederalReserveAtlantaPublicationsFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaPublicationsFetcher.extract_data(query, None)


class TestPublicationsChoices:
    """Tests for the shared regional_publications_choices contract."""

    @pytest.mark.asyncio
    async def test_choices_include_gdpnow_slides(self):
        """The choices endpoint surfaces the folded GDPNow slides with a url."""
        from openbb_federal_reserve.federal_reserve_router import (
            regional_publications_choices,
        )

        choices = await regional_publications_choices("atlanta")
        urls = {choice["value"] for choice in choices}
        assert ap.GDPNOW_SLIDES_URL in urls
        slide_choice = next(
            choice for choice in choices if choice["value"] == ap.GDPNOW_SLIDES_URL
        )
        assert "GDPNow Real GDP Tracking Slides" in slide_choice["label"]
