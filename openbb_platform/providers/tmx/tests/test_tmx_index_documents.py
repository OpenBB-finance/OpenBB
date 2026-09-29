"""Tests for the index documents viewer and the index profile."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_tmx.models.index_documents import TmxIndexDocumentsFetcher
from openbb_tmx.models.index_info import TmxIndexInfoFetcher
from openbb_tmx.routers.index import (
    DocumentRequest,
    document_choices,
    document_view,
    symbol_choices,
)

PUBLISHED = {
    "indices": {
        "^TSX": {
            "name_en": "S&P/TSX Composite Index",
            "overview_en": "<p>The headline index &amp; benchmark.</p>",
            "nb_constituents": 219,
            "updated": "2026-07-24T20:00:02-04:00",
            "factsheet": "https://spindices.com/file.pdf?indexId=5457755",
            "methodology": "https://spindices.com/methodology-canadian.pdf",
            "performance": {"yeartodate": 11.53, "previousday": 0.501},
            "quotedmarketvalue": {"total": 5.5e12, "largestweight": 8.168},
        },
        "^TXCE": {
            "name_en": "S&P/TSX Capped Composite",
            "methodology": "https://spindices.com/methodology-canadian.pdf",
        },
        "^TXBA": {"name_en": "S&P/TSX Bare Index"},
    }
}


@pytest.fixture
def published(monkeypatch):
    """Serve the index reference file."""

    async def file(url, use_cache=True, **kwargs):
        return PUBLISHED

    monkeypatch.setattr("openbb_tmx.utils.helpers.get_data_from_url", file)


@pytest.fixture
def ratios(monkeypatch):
    """Serve the published key data."""

    async def graph(operation, query, variables=None, **kwargs):
        return {"getIndexKeyData": {"peRatio": 21.26, "divYield": 2.13}}

    monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", graph)


class TestDocuments:
    """The documents an index publishes."""

    async def test_an_index_carries_both_of_its_documents(self, published):
        rows = await TmxIndexDocumentsFetcher.fetch_data({"symbol": "^tsx"}, {})

        assert [r.document_type for r in rows] == ["factsheet", "methodology"]
        assert rows[0].name == "S&P/TSX Composite Index - Factsheet"
        assert rows[0].index_name == "S&P/TSX Composite Index"

    async def test_the_whole_universe_is_listed_without_a_symbol(self, published):
        rows = await TmxIndexDocumentsFetcher.fetch_data({}, {})

        assert len(rows) == 3
        assert {r.symbol for r in rows} == {"^TSX", "^TXCE"}

    async def test_one_kind_of_document_is_listed_on_its_own(self, published):
        rows = await TmxIndexDocumentsFetcher.fetch_data(
            {"document_type": "factsheet"}, {}
        )

        assert [r.symbol for r in rows] == ["^TSX"]

    async def test_an_index_publishing_nothing_is_reported(self, published):
        with pytest.raises(EmptyDataError, match="No documents"):
            await TmxIndexDocumentsFetcher.fetch_data({"symbol": "^TXBA"}, {})

    async def test_an_unknown_index_is_reported(self, published):
        with pytest.raises(OpenBBError, match="was not found"):
            await TmxIndexDocumentsFetcher.fetch_data({"symbol": "^NOPE"}, {})

    async def test_an_empty_file_is_reported(self, monkeypatch):
        async def nothing(url, use_cache=True, **kwargs):
            return {}

        monkeypatch.setattr("openbb_tmx.utils.helpers.get_data_from_url", nothing)

        with pytest.raises(EmptyDataError):
            await TmxIndexDocumentsFetcher.fetch_data({}, {})

    async def test_an_index_without_a_name_still_names_its_document(self, monkeypatch):
        async def unnamed(url, use_cache=True, **kwargs):
            return {"indices": {"^X": {"factsheet": "https://spindices.com/x.pdf"}}}

        monkeypatch.setattr("openbb_tmx.utils.helpers.get_data_from_url", unnamed)
        rows = await TmxIndexDocumentsFetcher.fetch_data({"symbol": "^X"}, {})

        assert rows[0].name == "Factsheet"


class TestViewer:
    """The endpoints behind the multi-file viewer."""

    async def test_the_file_selector_is_populated(self, published):
        offered = await document_choices("^TSX")

        assert offered[0]["label"] == "S&P/TSX Composite Index - Factsheet"
        assert offered[0]["value"].startswith("https://spindices.com/")

    async def test_one_kind_of_document_narrows_the_selector(self, published):
        offered = await document_choices("^TSX", "methodology")

        assert [o["label"] for o in offered] == [
            "S&P/TSX Composite Index - Methodology"
        ]

    async def test_an_index_with_no_documents_offers_none(self, published):
        assert await document_choices("^TXBA") == []

    async def test_only_indices_with_documents_are_offered(self, published):
        offered = await symbol_choices()

        assert [o["value"] for o in offered] == ["^TSX", "^TXCE"]
        assert offered[0]["label"] == "S&P/TSX Composite Index (^TSX)"

    async def test_no_published_file_offers_no_indices(self, monkeypatch):
        async def broken(url, use_cache=True, **kwargs):
            raise OSError("the file is unreachable")

        monkeypatch.setattr("openbb_tmx.utils.helpers.get_data_from_url", broken)

        assert await symbol_choices() == []

    async def test_a_document_the_publisher_withholds_is_handed_over_as_a_url(
        self, published
    ):
        files = await document_view(
            DocumentRequest(
                url=[
                    "https://spindices.com/file.pdf?indexId=5457755",
                    "https://spindices.com/methodology-canadian.pdf",
                ]
            )
        )

        assert files[0]["url"] == "https://spindices.com/file.pdf?indexId=5457755"
        assert "content" not in files[0]
        assert files[0]["data_format"] == {
            "data_type": "pdf",
            "filename": "S&P/TSX Composite Index - Factsheet.pdf",
        }

    async def test_a_document_the_publisher_serves_is_handed_over_whole(
        self, published, monkeypatch
    ):
        from base64 import b64decode

        async def download(url, use_cache=True, accept_type="json", **kwargs):
            return b"%PDF-1.6 factsheet"

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", download)
        files = await document_view(
            DocumentRequest(url="https://spindices.com/file.pdf?indexId=5457755")
        )

        assert b64decode(files[0]["content"]) == b"%PDF-1.6 factsheet"

    async def test_one_selection_is_accepted(self, published):
        files = await document_view(
            DocumentRequest(url="https://spindices.com/methodology-canadian.pdf")
        )

        assert len(files) == 1

    async def test_an_unlisted_url_falls_back_to_its_file_name(self, published):
        files = await document_view(
            DocumentRequest(url="https://spindices.com/other.pdf?v=2")
        )

        assert files[0]["data_format"]["filename"] == "other.pdf"

    async def test_an_unreadable_catalog_still_serves_the_files(self, monkeypatch):
        async def broken(url, use_cache=True, **kwargs):
            raise OSError("the file is unreachable")

        monkeypatch.setattr("openbb_tmx.utils.helpers.get_data_from_url", broken)
        files = await document_view(
            DocumentRequest(url="https://spindices.com/other.pdf")
        )

        assert files[0]["data_format"]["filename"] == "other.pdf"

    async def test_nothing_selected_returns_nothing(self, published):
        assert await document_view(DocumentRequest()) == []


class TestInfo:
    """The index profile."""

    async def test_the_profile_carries_its_documents_and_ratios(
        self, published, ratios
    ):
        rows = await TmxIndexInfoFetcher.fetch_data({"symbol": "^TSX"}, {})
        record = rows[0]

        assert record.description == "The headline index & benchmark."
        assert record.factsheet.endswith("indexId=5457755")
        assert record.methodology.endswith("methodology-canadian.pdf")
        assert record.num_constituents == 219
        assert record.market_value == 5.5e12
        assert record.largest_constituent_weight == pytest.approx(0.08168)
        assert record.year_to_date == pytest.approx(0.1153)
        assert record.pe_ratio == 21.26
        assert record.dividend_yield == pytest.approx(0.0213)

    async def test_unpublished_key_data_is_not_fatal(self, published, monkeypatch):
        async def refused(*args, **kwargs):
            raise OpenBBError("the index endpoint refused the request")

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", refused)
        rows = await TmxIndexInfoFetcher.fetch_data({"symbol": "^TSX"}, {})

        assert rows[0].pe_ratio is None
        assert rows[0].num_constituents == 219

    async def test_an_index_with_no_overview_has_no_description(
        self, published, ratios
    ):
        rows = await TmxIndexInfoFetcher.fetch_data({"symbol": "^TXBA"}, {})

        assert rows[0].description is None

    async def test_an_unknown_index_is_reported(self, published, ratios):
        with pytest.raises(OpenBBError, match="was not found"):
            await TmxIndexInfoFetcher.fetch_data({"symbol": "^NOPE"}, {})

    async def test_an_empty_file_is_reported(self, monkeypatch, ratios):
        async def nothing(url, use_cache=True, **kwargs):
            return {}

        monkeypatch.setattr("openbb_tmx.utils.helpers.get_data_from_url", nothing)

        with pytest.raises(EmptyDataError):
            await TmxIndexInfoFetcher.fetch_data({"symbol": "^TSX"}, {})


class TestViewerWidget:
    """The widget the Workspace renders."""

    @pytest.fixture(scope="class")
    def widget(self):
        """Build the registered widget."""
        import warnings

        warnings.filterwarnings("ignore")
        from openbb_core.api.rest_api import app
        from openbb_platform_api.utils.widgets import build_json

        return build_json(app.openapi(), [])["tmx_index_documents_obb"]

    def test_it_is_a_file_viewer(self, widget):
        assert widget["type"] == "multi_file_viewer"
        assert widget["source"] == ["TMX"]

    def test_the_file_selector_depends_on_the_index(self, widget):
        params = {p["paramName"]: p for p in widget["params"]}
        selector = params["url"]

        assert selector["roles"] == ["fileSelector"]
        assert selector["multiSelect"] is True
        assert selector["show"] is False
        assert selector["optionsParams"] == {
            "symbol": "$symbol",
            "document_type": "$document_type",
        }
        assert params["symbol"]["value"] == "^TSX"
        assert params["symbol"]["optionsEndpoint"].endswith("/index/symbol_choices")

    def test_it_is_laid_out_with_the_index_group(self):
        import json
        import pathlib

        app = json.loads(
            pathlib.Path("openbb_tmx/assets/apps.json").read_text(encoding="utf-8")
        )[0]
        group = next(g for g in app["groups"] if g["name"] == "Indices Index")

        assert "tmx_index_documents_obb" in group["widgetIds"]
        assert "tmx_index_documents_obb" in [
            cell["i"] for cell in app["tabs"]["indices"]["layout"]
        ]
