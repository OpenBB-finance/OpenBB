"""Tests for the San Francisco Fed publications helpers and commands."""

import base64
from datetime import date
from unittest.mock import MagicMock

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.san_francisco_publications import (
    FederalReserveSanFranciscoPublicationsData,
    FederalReserveSanFranciscoPublicationsFetcher,
)
from openbb_federal_reserve.utils import san_francisco_publications as sfp


def _entry(date_str, slug, title, volume=None, issue=None):
    """Build a synthetic wp-json publication entry."""
    return {
        "date": f"{date_str}T10:00:00",
        "slug": slug,
        "title": {"rendered": title},
        "link": f"https://www.frbsf.org/x/{slug}/",
        "meta": {
            "publication_volume": volume,
            "publication_issue": issue,
        },
    }


_EL_ENTRIES = [
    _entry("2026-06-22", "latest-el", "Latest <em>EL</em>", volume="2026", issue="16"),
    _entry("2026-04-06", "revised-el", "Revised EL", volume="2026", issue="09"),
    _entry("2025-01-10", "no-issue-el", "No Issue EL", volume="2025", issue=""),
]
_FV_ENTRIES = [
    _entry("2026-06-04", "fv-june", "FedViews June"),
    _entry("2025-11-20", "fv-nov", "FedViews November"),
]


def _wp_response(entries, total_pages=1):
    """Build a paged wp-json response."""
    response = MagicMock()
    response.headers = {"X-WP-TotalPages": str(total_pages)}
    response.json = MagicMock(return_value=entries)
    response.raise_for_status = MagicMock()
    return response


class TestDerivePdf:
    """Tests for ``_derive_pdf``."""

    def test_economic_letter_zero_pads_issue(self):
        """A valid volume and issue derive a zero-padded el URL."""
        url = sfp._derive_pdf("economic_letter", _EL_ENTRIES[1])
        assert url == "https://www.frbsf.org/wp-content/uploads/el2026-09.pdf"

    def test_economic_letter_missing_issue_returns_none(self):
        """A non-numeric issue is not derivable."""
        assert sfp._derive_pdf("economic_letter", _EL_ENTRIES[2]) is None

    def test_fedviews_derives_from_date(self):
        """A FedViews entry derives a date-based fv URL."""
        url = sfp._derive_pdf("fedviews", _FV_ENTRIES[0])
        assert url == "https://www.frbsf.org/wp-content/uploads/fv20260604.pdf"


class TestRecord:
    """Tests for ``_record``."""

    def test_strips_html_and_carries_metadata(self):
        """The record strips title HTML and carries volume and issue."""
        record = sfp._record("economic_letter", _EL_ENTRIES[0])
        assert record["title"] == "Latest EL"
        assert record["date"] == "2026-06-22"
        assert record["volume"] == "2026"
        assert record["issue"] == "16"
        assert record["url"].endswith("el2026-16.pdf")


class TestListPublications:
    """Tests for ``list_publications``."""

    def test_unknown_type_raises(self):
        """An unknown publication type raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            sfp.list_publications("unknown")

    def test_pages_and_sorts(self, monkeypatch):
        """Multi-page enumeration concatenates and sorts newest first."""
        pages = {1: _EL_ENTRIES[:2], 2: _EL_ENTRIES[2:]}

        def _make_request(url, *args, **kwargs):
            """Return the correct page from the url query string."""
            page = 2 if "page=2" in url else 1
            return _wp_response(pages[page], total_pages=2)

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        catalog = sfp.list_publications("economic_letter")
        assert len(catalog) == 3
        assert [r["date"] for r in catalog] == [
            "2026-06-22",
            "2026-04-06",
            "2025-01-10",
        ]


class TestResolvePdfUrl:
    """Tests for ``_resolve_pdf_url``."""

    def test_derived_url_when_valid(self, monkeypatch):
        """A working derived URL is returned without scraping."""
        head = MagicMock()
        head.ok = True
        head.headers = {"Content-Type": "application/pdf"}
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: head,
        )
        record = sfp._record("fedviews", _FV_ENTRIES[0])
        assert sfp._resolve_pdf_url(record).endswith("fv20260604.pdf")

    def test_scrape_fallback(self, monkeypatch):
        """A failing derived URL falls back to the scraped landing page."""

        def _make_request(url, *args, **kwargs):
            """404 the derived PDF, serve HTML with the real suffixed link."""
            response = MagicMock()
            response.raise_for_status = MagicMock()
            if url.endswith(".pdf"):
                response.ok = False
                response.headers = {"Content-Type": "text/html"}
            else:
                response.text = (
                    '<a href="https://www.frbsf.org/wp-content/uploads/'
                    'fv20251120-final.pdf">x</a>'
                )
            return response

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        record = sfp._record("fedviews", _FV_ENTRIES[1])
        assert sfp._resolve_pdf_url(record).endswith("fv20251120-final.pdf")

    def test_unresolvable_raises(self, monkeypatch):
        """A missing derived URL and empty landing page raise ``OpenBBError``."""

        def _make_request(url, *args, **kwargs):
            """Serve a landing page without any PDF link."""
            response = MagicMock()
            response.raise_for_status = MagicMock()
            response.text = "<html>no pdf here</html>"
            return response

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        record = sfp._record("economic_letter", _EL_ENTRIES[2])
        with pytest.raises(OpenBBError):
            sfp._resolve_pdf_url(record)


class TestFetchPublicationPdf:
    """Tests for ``fetch_publication_pdf``."""

    def test_latest(self, monkeypatch):
        """The latest publication downloads as a base64 PDF payload."""
        monkeypatch.setattr(
            sfp,
            "list_publications",
            lambda _: [sfp._record("fedviews", _FV_ENTRIES[0])],
        )
        monkeypatch.setattr(
            sfp,
            "_resolve_pdf_url",
            lambda record: "https://www.frbsf.org/wp-content/uploads/fv20260604.pdf",
        )
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response_pdf(),
        )
        out = sfp.fetch_publication_pdf("fedviews")
        assert out["data_format"]["filename"] == "fv20260604.pdf"
        assert base64.b64decode(out["content"]).startswith(b"%PDF")

    def test_by_date(self, monkeypatch):
        """A requested date selects the matching publication."""
        catalog = [sfp._record("economic_letter", e) for e in _EL_ENTRIES]
        monkeypatch.setattr(sfp, "list_publications", lambda _: catalog)
        monkeypatch.setattr(
            sfp,
            "_resolve_pdf_url",
            lambda record: "https://www.frbsf.org/wp-content/uploads/el2026-09.pdf",
        )
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response_pdf(),
        )
        out = sfp.fetch_publication_pdf("economic_letter", date="2026-04")
        assert out["data_format"]["filename"] == "el2026-09.pdf"

    def test_no_catalog_raises(self, monkeypatch):
        """An empty catalog raises ``OpenBBError``."""
        monkeypatch.setattr(sfp, "list_publications", lambda _: [])
        with pytest.raises(OpenBBError):
            sfp.fetch_publication_pdf("economic_letter")

    def test_unknown_date_raises(self, monkeypatch):
        """A date absent from the catalog raises ``OpenBBError``."""
        monkeypatch.setattr(
            sfp,
            "list_publications",
            lambda _: [sfp._record("fedviews", _FV_ENTRIES[0])],
        )
        with pytest.raises(OpenBBError):
            sfp.fetch_publication_pdf("fedviews", date="1999-01")


def _response_pdf():
    """Build a make_request response with PDF bytes."""
    response = MagicMock()
    response.content = b"%PDF-1.7 fake publication"
    response.raise_for_status = MagicMock()
    return response


class TestPublicationsIndex:
    """Tests for the publications index data model."""

    def _patch(self, monkeypatch):
        """Point the index model at a synthetic catalog."""
        catalog = [sfp._record("economic_letter", e) for e in _EL_ENTRIES]
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.san_francisco_publications.list_publications",
            lambda _: catalog,
        )

    def test_filters_start_and_end_date(self, monkeypatch):
        """The start_date and end_date filters narrow the catalog."""
        self._patch(monkeypatch)
        query = FederalReserveSanFranciscoPublicationsFetcher.transform_query(
            {"start_date": "2026-01-01", "end_date": "2026-05-01"}
        )
        rows = FederalReserveSanFranciscoPublicationsFetcher.transform_data(
            query,
            FederalReserveSanFranciscoPublicationsFetcher.extract_data(query, None),
        )
        assert all(
            isinstance(r, FederalReserveSanFranciscoPublicationsData) for r in rows
        )
        assert [r.date for r in rows] == [date(2026, 4, 6)]

    def test_no_filter_returns_all(self, monkeypatch):
        """With no filters the full catalog is returned."""
        self._patch(monkeypatch)
        query = FederalReserveSanFranciscoPublicationsFetcher.transform_query({})
        rows = FederalReserveSanFranciscoPublicationsFetcher.transform_data(
            query,
            FederalReserveSanFranciscoPublicationsFetcher.extract_data(query, None),
        )
        assert len(rows) == 3

    def test_empty_raises(self, monkeypatch):
        """An empty catalog raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.san_francisco_publications.list_publications",
            lambda _: [],
        )
        query = FederalReserveSanFranciscoPublicationsFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveSanFranciscoPublicationsFetcher.extract_data(query, None)


class TestListAllPublications:
    """Tests for the merged all-series catalog used by the file selector."""

    def test_merges_all_types_newest_first(self, monkeypatch):
        """An unset type enumerates every series and merges them, newest first."""
        by_type = {
            sfp.PUBLICATION_TYPES["economic_letter"]: _EL_ENTRIES,
            sfp.PUBLICATION_TYPES["fedviews"]: _FV_ENTRIES,
        }

        def _make_request(url, *args, **kwargs):
            """Serve the single page of entries for the requested type id."""
            type_id = next(t for t in by_type if f"publication-type={t}" in url)
            return _wp_response(by_type[type_id], total_pages=1)

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        catalog = sfp.list_publications()
        assert {r["publication_type"] for r in catalog} == {
            "economic_letter",
            "fedviews",
        }
        assert [r["date"] for r in catalog] == sorted(
            (r["date"] for r in catalog), reverse=True
        )
        assert catalog[0]["date"] == "2026-06-22"


class TestPublicationsViewerConfig:
    """Tests for the multi-file-viewer widget config on the Data model."""

    def test_multi_file_viewer_with_file_selector(self):
        """The Data model declares the shared download/choices viewer endpoints."""
        config = FederalReserveSanFranciscoPublicationsData.model_config[
            "json_schema_extra"
        ]["x-widget_config"]
        assert config["$.type"] == "multi_file_viewer"
        assert config["$.subCategory"] == "Publications & Reports"
        assert config["$.endpoint"].endswith(
            "/federal_reserve/regional_publications_download"
        )
        param = config["$.params"][0]
        assert param["roles"] == ["fileSelector"]
        assert param["optionsParams"] == {"district": "sf"}
        assert param["optionsEndpoint"].endswith(
            "/federal_reserve/regional_publications_choices"
        )
