"""Tests for the St. Louis Fed publications index model, util, and viewer."""

from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.st_louis_publications import (
    FederalReserveStLouisPublicationsData,
    FederalReserveStLouisPublicationsFetcher,
)
from openbb_federal_reserve.utils import st_louis as st_louis_utils

_SYNOPSES = [
    {
        "item_id": "672949",
        "title": "What Is Behind the Rise in Markups?",
        "year": 2024,
        "issue": 14,
        "date": "2024-07-01",
        "url": "https://fraser.stlouisfed.org/title/economic-synopses-6715/x-672949",
        "pdf_url": "https://fraser.stlouisfed.org/files/economicsynopses_20240701.pdf",
    },
    {
        "item_id": "624571",
        "title": "The College Wealth Divide Continues to Grow",
        "year": 2020,
        "issue": 1,
        "date": "2020-04-09",
        "url": "https://fraser.stlouisfed.org/title/economic-synopses-6715/y-624571",
        "pdf_url": "https://fraser.stlouisfed.org/files/economicsynopses_20200409.pdf",
    },
    {
        "item_id": "111111",
        "title": "An Article With No PDF",
        "year": None,
        "issue": None,
        "date": "",
        "url": "https://fraser.stlouisfed.org/title/economic-synopses-6715/z-111111",
        "pdf_url": "",
    },
]


class TestListPublications:
    """Tests for the publications-catalog aggregation helper."""

    def test_folds_synopses_pdfs_and_skips_missing(self, monkeypatch):
        """Synopses with a PDF url become catalog records; PDF-less ones drop."""
        monkeypatch.setattr(st_louis_utils, "list_economic_synopses", lambda: _SYNOPSES)
        catalog = st_louis_utils.list_publications()
        assert [record["id"] for record in catalog] == ["672949", "624571"]
        assert all(record["series"] == "economic_synopses" for record in catalog)
        assert catalog[0]["url"].endswith("economicsynopses_20240701.pdf")
        assert catalog[0]["date"] == "2024-07-01"
        assert catalog[0]["title"] == "What Is Behind the Rise in Markups?"


class TestPublicationsIndexModel:
    """Tests for the publications discovery index model."""

    def _patch(self, monkeypatch):
        """Point the fetcher at the synthetic synopses catalog."""
        monkeypatch.setattr(st_louis_utils, "list_economic_synopses", lambda: _SYNOPSES)

    def test_no_filter_returns_all_pdf_records(self, monkeypatch):
        """With no filters every PDF-backed publication is returned with a url."""
        self._patch(monkeypatch)
        query = FederalReserveStLouisPublicationsFetcher.transform_query({})
        rows = FederalReserveStLouisPublicationsFetcher.transform_data(
            query, FederalReserveStLouisPublicationsFetcher.extract_data(query, None)
        )
        assert all(isinstance(r, FederalReserveStLouisPublicationsData) for r in rows)
        assert len(rows) == 2
        assert all(r.url.endswith(".pdf") for r in rows)
        assert not hasattr(rows[0], "id")

    def test_filters_start_and_end_date(self, monkeypatch):
        """The start_date and end_date filters narrow the catalog."""
        self._patch(monkeypatch)
        query = FederalReserveStLouisPublicationsFetcher.transform_query(
            {"start_date": "2024-01-01", "end_date": "2024-12-31"}
        )
        rows = FederalReserveStLouisPublicationsFetcher.transform_data(
            query, FederalReserveStLouisPublicationsFetcher.extract_data(query, None)
        )
        assert [r.title for r in rows] == ["What Is Behind the Rise in Markups?"]
        assert rows[0].date == date(2024, 7, 1)

    def test_empty_raises(self, monkeypatch):
        """An empty catalog raises ``EmptyDataError``."""
        monkeypatch.setattr(st_louis_utils, "list_economic_synopses", list)
        query = FederalReserveStLouisPublicationsFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveStLouisPublicationsFetcher.extract_data(query, None)


class TestViewerConfig:
    """Tests for the multi_file_viewer x-widget_config."""

    def test_widget_config(self):
        """The data model declares one multi_file_viewer wired to the stl district."""
        config = FederalReserveStLouisPublicationsData.model_config[
            "json_schema_extra"
        ]["x-widget_config"]
        assert config["$.type"] == "multi_file_viewer"
        assert config["$.name"] == "St. Louis Fed Publications"
        assert config["$.subCategory"] == "Publications & Reports"
        assert config["$.source"] == ["Federal Reserve Bank of St. Louis"]
        assert config["$.endpoint"].endswith("/regional_publications_download")
        param = config["$.params"][0]
        assert param["optionsEndpoint"].endswith("/regional_publications_choices")
        assert param["optionsParams"] == {"district": "stl"}
        assert param["roles"] == ["fileSelector"]
        assert param["multiSelect"] is True


class TestRegionalPublicationsChoices:
    """The shared choices endpoint dispatches to the St. Louis fetcher."""

    @pytest.mark.asyncio
    async def test_stl_returns_url_choices(self, monkeypatch):
        """``regional_publications_choices('stl')`` returns label/url choices."""
        from openbb_federal_reserve.federal_reserve_router import (
            regional_publications_choices,
        )

        monkeypatch.setattr(st_louis_utils, "list_economic_synopses", lambda: _SYNOPSES)
        choices = await regional_publications_choices("stl")
        assert len(choices) == 2
        assert choices[0]["value"].endswith("economicsynopses_20240701.pdf")
        assert "What Is Behind the Rise in Markups?" in choices[0]["label"]
        assert "2024-07" in choices[0]["label"]
