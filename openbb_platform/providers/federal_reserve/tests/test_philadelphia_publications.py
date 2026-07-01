"""Tests for the Philadelphia Fed publications index, report, and choices."""

import base64
from datetime import date
from unittest.mock import MagicMock

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.philadelphia_publications import (
    FederalReservePhiladelphiaPublicationsData,
    FederalReservePhiladelphiaPublicationsFetcher,
)
from openbb_federal_reserve.utils import philadelphia_publications as pubs

_LISTING_HTML = {
    "survey-of-professional-forecasters": (
        '<a href="/-/media/FRBP/Assets/Surveys-And-Data'
        '/survey-of-professional-forecasters/2026/spfq226.pdf">x</a>'
        '<a href="/-/media/FRBP/Assets/Surveys-And-Data'
        '/survey-of-professional-forecasters/1990/spfq390.pdf">x</a>'
        '<a href="/-/media/FRBP/Assets/Surveys-And-Data'
        '/survey-of-professional-forecasters/2026/spfq926.pdf">x</a>'
    ),
    "manufacturing-business-outlook-survey": (
        '<a href="/-/media/FRBP/Assets/Surveys-And-Data'
        '/MBOS/2026/bos0626.pdf">x</a>'
        '<a href="/-/media/FRBP/Assets/Surveys-And-Data'
        '/MBOS/1968/bos0568.pdf">x</a>'
    ),
    "nonmanufacturing-business-outlook-survey": (
        '<a href="/-/media/FRBP/Assets/Surveys-And-Data/NBOS/2026/nbos0626.pdf">x</a>'
    ),
    "livingston-survey": (
        '<a href="/-/media/FRBP/Assets/Surveys-And-Data'
        '/livingston-survey/2026/livjun26.pdf">x</a>'
        '<a href="/-/media/FRBP/Assets/Surveys-And-Data'
        '/livingston-survey/1991/livdec91.pdf">x</a>'
    ),
}


def _make_request(url, *args, **kwargs):
    """Path-aware fake: listing HTML for landing pages, PDF bytes otherwise."""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    for key in sorted(_LISTING_HTML, key=len, reverse=True):
        if url.endswith(key):
            response.text = _LISTING_HTML[key]
            return response
    response.content = b"%PDF-1.7 fake report"
    return response


class TestClassify:
    """Tests for the publication filename classifier."""

    def test_spf_quarter_and_century_pivot(self):
        """An SPF filename resolves quarter and pivots its two-digit year."""
        record = pubs._classify(
            "spf",
            "/-/media/FRBP/Assets/Surveys-And-Data"
            "/survey-of-professional-forecasters/1990/spfq390.pdf",
        )
        assert record["date"] == "1990-07-01"
        assert record["id"] == "spf_spfq390"
        assert record["title"] == "Survey of Professional Forecasters 1990:Q3"

    def test_spf_invalid_quarter_returns_none(self):
        """A quarter digit out of range is not classifiable."""
        assert (
            pubs._classify(
                "spf",
                "/-/media/FRBP/Assets/Surveys-And-Data"
                "/survey-of-professional-forecasters/2026/spfq926.pdf",
            )
            is None
        )

    def test_livingston_month_abbreviation(self):
        """A Livingston filename resolves its month abbreviation and year."""
        record = pubs._classify(
            "livingston",
            "/-/media/FRBP/Assets/Surveys-And-Data/livingston-survey/1991/livdec91.pdf",
        )
        assert record["date"] == "1991-12-01"
        assert record["title"] == "Livingston Survey December 1991"

    def test_mbos_month_year(self):
        """An MBOS filename resolves its month/year fields."""
        record = pubs._classify(
            "mbos",
            "/-/media/FRBP/Assets/Surveys-And-Data/MBOS/1968/bos0568.pdf",
        )
        assert record["date"] == "1968-05-01"
        assert record["series"] == "mbos"

    def test_mbos_invalid_month_returns_none(self):
        """An MBOS month out of range is not classifiable."""
        assert (
            pubs._classify(
                "mbos",
                "/-/media/FRBP/Assets/Surveys-And-Data/MBOS/2026/bos1326.pdf",
            )
            is None
        )

    def test_non_matching_stem_returns_none(self):
        """A filename that does not match the series pattern is skipped."""
        assert (
            pubs._classify(
                "nbos",
                "/-/media/FRBP/Assets/Surveys-And-Data/NBOS/2026/overview.pdf",
            )
            is None
        )

    def test_spf_non_matching_stem_returns_none(self):
        """An SPF link whose stem is not ``spfqNYY`` is skipped."""
        assert (
            pubs._classify(
                "spf",
                "/-/media/FRBP/Assets/Surveys-And-Data"
                "/survey-of-professional-forecasters/2026/summary.pdf",
            )
            is None
        )

    def test_livingston_non_month_returns_none(self):
        """A Livingston link with a non-month abbreviation is skipped."""
        assert (
            pubs._classify(
                "livingston",
                "/-/media/FRBP/Assets/Surveys-And-Data"
                "/livingston-survey/2026/livxyz26.pdf",
            )
            is None
        )


class TestListPublications:
    """Tests for ``list_publications``."""

    def test_single_series(self, monkeypatch):
        """A single series indexes and classifies its listing, newest first."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        catalog = pubs.list_publications("spf")
        ids = [record["id"] for record in catalog]
        assert ids == ["spf_spfq226", "spf_spfq390"]

    def test_all_series_merged(self, monkeypatch):
        """With no series, all four archives merge into one catalog."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        catalog = pubs.list_publications()
        series = {record["series"] for record in catalog}
        assert series == {"spf", "mbos", "nbos", "livingston"}
        assert catalog == sorted(
            catalog, key=lambda r: (r["date"], r["id"]), reverse=True
        )


class TestFetchPublicationPdf:
    """Tests for ``fetch_publication_pdf``."""

    def test_latest_for_series(self, monkeypatch):
        """The most recent report for a series downloads as base64 PDF."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        out = pubs.fetch_publication_pdf(series="spf")
        assert out["data_format"]["filename"] == "Philadelphia_spf_spfq226.pdf"
        assert base64.b64decode(out["content"]).startswith(b"%PDF")

    def test_by_date(self, monkeypatch):
        """A date selects the matching month's report."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        out = pubs.fetch_publication_pdf(series="mbos", date="2026-06")
        assert out["data_format"]["filename"] == "Philadelphia_mbos_bos0626.pdf"

    def test_unknown_date_raises(self, monkeypatch):
        """An unknown date raises ``OpenBBError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        with pytest.raises(OpenBBError):
            pubs.fetch_publication_pdf(date="1800-01", series="spf")

    def test_empty_catalog_raises(self, monkeypatch):
        """An empty catalog raises ``OpenBBError``."""
        monkeypatch.setattr(pubs, "list_publications", lambda series=None: [])
        with pytest.raises(OpenBBError):
            pubs.fetch_publication_pdf(series="spf")


class TestPublicationsIndexModel:
    """Tests for the publications index data model."""

    _CATALOG = [
        {
            "series": "spf",
            "id": "spf_spfq226",
            "date": "2026-04-01",
            "title": "Survey of Professional Forecasters 2026:Q2",
            "url": "https://x/spfq226.pdf",
        },
        {
            "series": "mbos",
            "id": "mbos_bos0126",
            "date": "2026-01-01",
            "title": "Manufacturing Business Outlook Survey January 2026",
            "url": "https://x/bos0126.pdf",
        },
    ]

    def _patch(self, monkeypatch):
        """Point the index model at a synthetic catalog."""
        monkeypatch.setattr(
            pubs, "list_publications", lambda series=None: list(self._CATALOG)
        )

    def test_multi_file_viewer_widget_config(self):
        """The data model carries the shared multi_file_viewer widget config."""
        config = FederalReservePhiladelphiaPublicationsData.model_config[
            "json_schema_extra"
        ]["x-widget_config"]
        assert config["$.type"] == "multi_file_viewer"
        assert config["$.endpoint"].endswith(
            "/federal_reserve/regional_publications_download"
        )
        param = config["$.params"][0]
        assert param["optionsEndpoint"].endswith(
            "/federal_reserve/regional_publications_choices"
        )
        assert param["optionsParams"] == {"district": "philadelphia"}
        assert param["roles"] == ["fileSelector"]

    def test_no_filter_returns_all(self, monkeypatch):
        """With no filters the full catalog is returned."""
        self._patch(monkeypatch)
        query = FederalReservePhiladelphiaPublicationsFetcher.transform_query({})
        rows = FederalReservePhiladelphiaPublicationsFetcher.transform_data(
            query,
            FederalReservePhiladelphiaPublicationsFetcher.extract_data(query, None),
        )
        assert all(
            isinstance(r, FederalReservePhiladelphiaPublicationsData) for r in rows
        )
        assert all("id" not in r.model_dump() for r in rows)
        assert len(rows) == 2

    def test_date_filters(self, monkeypatch):
        """The start_date and end_date filters narrow the catalog."""
        self._patch(monkeypatch)
        query = FederalReservePhiladelphiaPublicationsFetcher.transform_query(
            {"start_date": "2026-02-01", "end_date": "2026-12-31"}
        )
        rows = FederalReservePhiladelphiaPublicationsFetcher.transform_data(
            query,
            FederalReservePhiladelphiaPublicationsFetcher.extract_data(query, None),
        )
        assert [r.date for r in rows] == [date(2026, 4, 1)]

    def test_empty_raises(self, monkeypatch):
        """An empty catalog raises ``EmptyDataError``."""
        monkeypatch.setattr(pubs, "list_publications", lambda series=None: [])
        query = FederalReservePhiladelphiaPublicationsFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReservePhiladelphiaPublicationsFetcher.extract_data(query, None)
