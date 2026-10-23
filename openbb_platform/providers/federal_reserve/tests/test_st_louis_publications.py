"""Tests for the St. Louis Fed publications index model, util, and viewer."""

from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.st_louis_publications import (
    FederalReserveStLouisPublicationsData,
    FederalReserveStLouisPublicationsFetcher,
    FederalReserveStLouisPublicationsQueryParams,
)
from openbb_federal_reserve.utils import st_louis as st_louis_utils

_CATALOG = [
    {
        "series": "Working Papers",
        "date": "2024-07-01",
        "title": "What Is Behind the Rise in Markups?",
        "url": "https://fraser.stlouisfed.org/files/wp_2024_07.pdf",
    },
    {
        "series": "Economic Synopses",
        "date": "2020-04-09",
        "title": "The College Wealth Divide Continues to Grow",
        "url": "https://fraser.stlouisfed.org/files/es_2020_04.pdf",
    },
    {
        "series": "Review",
        "date": "",
        "title": "An Undated Review Article",
        "url": "https://fraser.stlouisfed.org/files/rev_undated.pdf",
    },
]


class TestPublicationsIndexModel:
    """Tests for the publications discovery index model."""

    def test_no_filter_returns_all_records(self, monkeypatch):
        """With no filters every catalog record is returned with a document URL."""
        monkeypatch.setattr(st_louis_utils, "list_publications", lambda **_: _CATALOG)
        query = FederalReserveStLouisPublicationsFetcher.transform_query({})
        rows = FederalReserveStLouisPublicationsFetcher.transform_data(
            query, FederalReserveStLouisPublicationsFetcher.extract_data(query, None)
        )
        assert all(isinstance(r, FederalReserveStLouisPublicationsData) for r in rows)
        assert len(rows) == 3
        assert all(r.url.endswith(".pdf") for r in rows)
        assert rows[2].date is None

    def test_series_slug_and_paging_are_forwarded(self, monkeypatch):
        """The selected slug, offset, and limit are forwarded to the util."""
        captured = {}

        def _list(series=None, start_date=None, start=0, limit=20):
            captured.update(series=series, start=start, limit=limit)
            return _CATALOG

        monkeypatch.setattr(st_louis_utils, "list_publications", _list)
        query = FederalReserveStLouisPublicationsFetcher.transform_query(
            {"series": "working_papers", "offset": 30, "limit": 5}
        )
        FederalReserveStLouisPublicationsFetcher.extract_data(query, None)
        assert captured == {"series": "working_papers", "start": 30, "limit": 5}

    def test_filters_start_and_end_date(self, monkeypatch):
        """The start_date and end_date filters narrow the catalog."""
        monkeypatch.setattr(st_louis_utils, "list_publications", lambda **_: _CATALOG)
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
        monkeypatch.setattr(st_louis_utils, "list_publications", lambda **_: [])
        query = FederalReserveStLouisPublicationsFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveStLouisPublicationsFetcher.extract_data(query, None)


class TestPublicationSeriesModel:
    """Tests for the supported-series discovery model."""

    def test_returns_series_with_counts(self, monkeypatch):
        """The model returns each supported series with its document count."""
        from openbb_federal_reserve.models.regional.st_louis_publication_series import (
            FederalReserveStLouisPublicationSeriesData,
            FederalReserveStLouisPublicationSeriesFetcher,
        )

        monkeypatch.setattr(
            st_louis_utils,
            "list_series",
            lambda: [
                {"series": "working_papers", "name": "Working Papers", "count": 5}
            ],
        )
        query = FederalReserveStLouisPublicationSeriesFetcher.transform_query({})
        rows = FederalReserveStLouisPublicationSeriesFetcher.transform_data(
            query,
            FederalReserveStLouisPublicationSeriesFetcher.extract_data(query, None),
        )
        assert all(
            isinstance(r, FederalReserveStLouisPublicationSeriesData) for r in rows
        )
        assert rows[0].series == "working_papers"
        assert rows[0].count == 5

    def test_empty_raises(self, monkeypatch):
        """An empty series list raises ``EmptyDataError``."""
        from openbb_federal_reserve.models.regional.st_louis_publication_series import (
            FederalReserveStLouisPublicationSeriesFetcher,
        )

        monkeypatch.setattr(st_louis_utils, "list_series", list)
        query = FederalReserveStLouisPublicationSeriesFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveStLouisPublicationSeriesFetcher.extract_data(query, None)


class TestSeriesQueryConfig:
    """Tests for the series query-parameter configuration."""

    def test_series_options_pair_label_with_slug(self):
        """The series options list every document series as label/slug pairs."""
        extra = FederalReserveStLouisPublicationsQueryParams.__json_schema_extra__[
            "series"
        ]
        options = extra["x-widget_config"]["options"]
        assert [option["value"] for option in options] == list(
            st_louis_utils.SERIES_SLUGS
        )
        assert {"label": "Working Papers", "value": "working_papers"} in options

    def test_series_field_is_a_literal_of_slugs(self):
        """The series field is a Literal so the Python interface documents values."""
        from typing import get_args

        field = FederalReserveStLouisPublicationsQueryParams.model_fields["series"]
        literal = get_args(field.annotation)[0]
        assert set(get_args(literal)) == set(st_louis_utils.SERIES_SLUGS)


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
        assert param["optionsParams"]["district"] == "stl"
        assert param["optionsParams"]["series"] == "$series"
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

        monkeypatch.setattr(st_louis_utils, "list_publications", lambda **_: _CATALOG)
        choices = await regional_publications_choices("stl")
        assert len(choices) == 3
        assert (
            choices[0]["value"] == "https://fraser.stlouisfed.org/files/wp_2024_07.pdf"
        )
        assert "What Is Behind the Rise in Markups?" in choices[0]["label"]
        assert "2024-07" in choices[0]["label"]
        assert choices[2]["label"] == "An Undated Review Article"

    @pytest.mark.asyncio
    async def test_series_and_paging_forwarded_to_choices(self, monkeypatch):
        """The choices endpoint forwards the series and paging filters."""
        from openbb_federal_reserve.federal_reserve_router import (
            regional_publications_choices,
        )

        captured = {}

        def _list(series=None, start_date=None, start=0, limit=20):
            captured.update(series=series, start=start, limit=limit)
            return _CATALOG

        monkeypatch.setattr(st_louis_utils, "list_publications", _list)
        await regional_publications_choices(
            "stl", series="working_papers", limit=5, offset=10
        )
        assert captured == {"series": "working_papers", "start": 10, "limit": 5}
