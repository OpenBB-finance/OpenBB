"""Tests for the Dallas Fed publication helpers, index model, and commands."""

import base64
from datetime import date
from unittest.mock import MagicMock

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.dallas_publications import (
    FederalReserveDallasPublicationsData,
    FederalReserveDallasPublicationsFetcher,
)
from openbb_federal_reserve.utils import dallas_publications as dp

_PAPERS_HTML = (
    '<a href="/-/media/documents/research/papers/2024/wp2419.pdf">x</a>'
    '<a href="/-/media/documents/research/papers/2012/wp1201.pdf">x</a>'
)
_SWE_HTML = (
    '<a href="/~/media/documents/research/swe/2022/swe2204.pdf">x</a>'
    '<a href="/~/media/documents/research/swe/1988/swe8801a.pdf">x</a>'
    '<a href="/~/media/documents/research/swe/2022/swe2213.pdf">x</a>'
)


def _make_request(url, *args, **kwargs):
    """Path-aware fake: listing HTML for the archive pages, PDF bytes otherwise."""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    if url.endswith("/research/papers"):
        response.text = _PAPERS_HTML
    elif url.endswith("/research/swe/archive"):
        response.text = _SWE_HTML
    else:
        response.content = b"%PDF-1.7 fake dallas pdf"
    return response


class TestClassify:
    """Tests for the publication filename classifier."""

    def test_working_paper(self):
        """A working-paper filename resolves to its year and id."""
        record = dp._classify("working_papers", "/x/wp2419.pdf")
        assert record["id"] == "wp2419"
        assert record["date"] == "2024-01-01"
        assert record["title"] == "Working Paper 2419"

    def test_working_paper_unparseable_returns_none(self):
        """A malformed working-paper filename is not classifiable."""
        assert dp._classify("working_papers", "/x/wpabc.pdf") is None

    def test_southwest_economy_with_letter_suffix(self):
        """A Southwest Economy filename with a letter suffix resolves to a month."""
        record = dp._classify("southwest_economy", "/x/swe2204.pdf")
        assert record["id"] == "swe2204"
        assert record["date"] == "2022-04-01"
        assert record["title"] == "Southwest Economy April 2022"

    def test_southwest_economy_1900s_year(self):
        """A two-digit year at or above 50 maps to the 1900s."""
        record = dp._classify("southwest_economy", "/x/swe8801a.pdf")
        assert record["date"] == "1988-01-01"

    def test_southwest_economy_unparseable_returns_none(self):
        """A malformed Southwest Economy filename is not classifiable."""
        assert dp._classify("southwest_economy", "/x/swexx.pdf") is None

    def test_southwest_economy_bad_month_returns_none(self):
        """An out-of-range month code is not classifiable."""
        assert dp._classify("southwest_economy", "/x/swe2213.pdf") is None


class TestListPublications:
    """Tests for ``list_publications``."""

    def test_all_series_dedups_and_sorts(self, monkeypatch):
        """Both series classify and merge with the static PDFs folded in."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        catalog = dp.list_publications()
        ids = [r["id"] for r in catalog]
        assert {"wp2419", "wp1201", "swe2204", "swe8801a"} <= set(ids)
        assert catalog == sorted(
            catalog, key=lambda r: (r["date"], r["id"]), reverse=True
        )

    def test_static_pdfs_folded_in(self, monkeypatch):
        """The questionnaires and energy charts fold in with real urls."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        catalog = dp.list_publications()
        by_id = {r["id"]: r for r in catalog}
        for survey, url in dp._QUESTIONNAIRES.items():
            record = by_id[f"questionnaire_{survey}"]
            assert record["series"] == "survey_questionnaire"
            assert record["url"] == url
        energy = by_id["energy_charts"]
        assert energy["series"] == "energy_charts"
        assert energy["url"] == dp._ENERGY_CHARTS_URL
        assert energy["url"].endswith("energycharts.pdf")

    def test_series_filter_scopes_one_archive(self, monkeypatch):
        """A series filter scopes the catalog to one archive, no static PDFs."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        catalog = dp.list_publications("working_papers")
        assert {r["series"] for r in catalog} == {"working_papers"}


class TestFetchPublicationPdf:
    """Tests for ``fetch_publication_pdf``."""

    def test_latest(self, monkeypatch):
        """With no selector the newest publication downloads."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        out = dp.fetch_publication_pdf(series="working_papers")
        assert out["data_format"]["filename"] == "Dallas_wp2419.pdf"
        assert base64.b64decode(out["content"]).startswith(b"%PDF")

    def test_by_date(self, monkeypatch):
        """A date selects the matching publication."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        out = dp.fetch_publication_pdf(series="southwest_economy", date="2022-04")
        assert out["data_format"]["filename"] == "Dallas_swe2204.pdf"

    def test_unknown_date_raises(self, monkeypatch):
        """An unknown date raises ``OpenBBError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        with pytest.raises(OpenBBError):
            dp.fetch_publication_pdf(date="1999-01", series="working_papers")

    def test_empty_catalog_raises(self, monkeypatch):
        """An empty catalog raises ``OpenBBError``."""
        monkeypatch.setattr(dp, "list_publications", lambda series=None: [])
        with pytest.raises(OpenBBError):
            dp.fetch_publication_pdf(series="working_papers")


class TestPublicationsIndex:
    """Tests for the discovery index data model."""

    _CATALOG = [
        {
            "series": "working_papers",
            "id": "wp2419",
            "date": "2024-01-01",
            "title": "Working Paper 2419",
            "url": "https://x/wp2419.pdf",
        },
        {
            "series": "southwest_economy",
            "id": "swe2204",
            "date": "2022-04-01",
            "title": "Southwest Economy April 2022",
            "url": "https://x/swe2204.pdf",
        },
        {
            "series": "southwest_economy",
            "id": "swe8801a",
            "date": "1988-01-01",
            "title": "Southwest Economy January 1988",
            "url": "https://x/swe8801a.pdf",
        },
    ]

    def _patch(self, monkeypatch):
        """Point the index model at a synthetic catalog."""
        monkeypatch.setattr(
            dp, "list_publications", lambda series=None: list(self._CATALOG)
        )

    def test_multi_file_viewer_widget_config(self):
        """The data model carries the shared multi_file_viewer widget config."""
        config = FederalReserveDallasPublicationsData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.type"] == "multi_file_viewer"
        assert config["$.endpoint"].endswith(
            "/federal_reserve/regional_publications_download"
        )
        param = config["$.params"][0]
        assert param["optionsEndpoint"].endswith(
            "/federal_reserve/regional_publications_choices"
        )
        assert param["optionsParams"] == {"district": "dallas"}
        assert param["roles"] == ["fileSelector"]

    def test_filters_start_and_end_date(self, monkeypatch):
        """The start_date and end_date filters narrow the catalog."""
        self._patch(monkeypatch)
        query = FederalReserveDallasPublicationsFetcher.transform_query(
            {"start_date": "2000-01-01", "end_date": "2023-12-31"}
        )
        rows = FederalReserveDallasPublicationsFetcher.transform_data(
            query, FederalReserveDallasPublicationsFetcher.extract_data(query, None)
        )
        assert all(isinstance(r, FederalReserveDallasPublicationsData) for r in rows)
        assert all("id" not in r.model_dump() for r in rows)
        assert [r.title for r in rows] == ["Southwest Economy April 2022"]
        assert rows[0].date == date(2022, 4, 1)

    def test_no_filter_returns_all(self, monkeypatch):
        """With no filters the full catalog is returned."""
        self._patch(monkeypatch)
        query = FederalReserveDallasPublicationsFetcher.transform_query({})
        rows = FederalReserveDallasPublicationsFetcher.transform_data(
            query, FederalReserveDallasPublicationsFetcher.extract_data(query, None)
        )
        assert len(rows) == 3

    def test_empty_raises(self, monkeypatch):
        """An empty catalog raises ``EmptyDataError``."""
        monkeypatch.setattr(dp, "list_publications", lambda series=None: [])
        query = FederalReserveDallasPublicationsFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveDallasPublicationsFetcher.extract_data(query, None)


class TestPublicationsChoices:
    """Tests for the shared regional_publications_choices contract."""

    @pytest.mark.asyncio
    async def test_choices_include_static_pdfs(self, monkeypatch):
        """The choices endpoint surfaces the folded questionnaires and charts."""
        from openbb_federal_reserve.federal_reserve_router import (
            regional_publications_choices,
        )

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        choices = await regional_publications_choices("dallas")
        urls = {choice["value"] for choice in choices}
        assert dp._ENERGY_CHARTS_URL in urls
        for url in dp._QUESTIONNAIRES.values():
            assert url in urls
