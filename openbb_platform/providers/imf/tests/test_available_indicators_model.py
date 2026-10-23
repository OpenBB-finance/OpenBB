"""Unit tests for the IMF Available Indicators model and fetcher."""

# ruff: noqa: I001

from typing import Any

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_imf.models.available_indicators import (
    ImfAvailableIndicatorsData,
    ImfAvailableIndicatorsFetcher,
    ImfAvailableIndicatorsQueryParams,
)


class _StubMeta:
    """Stand-in for ``ImfMetadata`` used to drive ``aextract_data`` branches."""

    def __init__(
        self,
        result: list[dict[str, Any]] | None = None,
        raise_exc: Exception | None = None,
    ):
        self._result = result if result is not None else []
        self._raise_exc = raise_exc
        self.calls: list[dict[str, Any]] = []

    def search_indicators(
        self,
        query: str,
        dataflows: Any | None = None,
        keywords: Any | None = None,
    ) -> list[dict[str, Any]]:
        """Record args and return the stub result, or raise if configured."""
        self.calls.append(
            {"query": query, "dataflows": dataflows, "keywords": keywords}
        )
        if self._raise_exc is not None:
            raise self._raise_exc
        return self._result


class TestImfAvailableIndicatorsFetcher:
    """Tests for ``ImfAvailableIndicatorsFetcher``."""

    def test_transform_query_passes_defaults(self):
        """Empty params produce a query with all defaults None."""
        q = ImfAvailableIndicatorsFetcher.transform_query({})
        assert isinstance(q, ImfAvailableIndicatorsQueryParams)
        assert q.query is None
        assert q.dataflows is None
        assert q.keywords is None

    @pytest.mark.asyncio
    async def test_aextract_data_string_dataflows_and_keywords(self, monkeypatch):
        """String ``dataflows``/``keywords`` are split by comma before search."""
        stub = _StubMeta(result=[{"indicator": "GDP"}])
        monkeypatch.setattr(
            "openbb_imf.utils.metadata.ImfMetadata",
            lambda: stub,
        )
        q = ImfAvailableIndicatorsFetcher.transform_query(
            {
                "query": "gold,volume",
                "dataflows": "WEO,IFS",
                "keywords": "gold,not USD",
            }
        )
        out = await ImfAvailableIndicatorsFetcher.aextract_data(q, None)
        assert out == [{"indicator": "GDP"}]
        call = stub.calls[0]
        assert call["query"] == "gold, volume"
        assert call["dataflows"] == ["WEO", "IFS"]
        assert call["keywords"] == ["gold", "not USD"]

    @pytest.mark.asyncio
    async def test_aextract_data_list_dataflows_and_keywords(self, monkeypatch):
        """List ``dataflows``/``keywords`` flow through unchanged."""
        stub = _StubMeta(result=[{"indicator": "CPI"}])
        monkeypatch.setattr(
            "openbb_imf.utils.metadata.ImfMetadata",
            lambda: stub,
        )
        params: dict[str, Any] = {"dataflows": ["WEO"], "keywords": ["gold"]}
        q = ImfAvailableIndicatorsFetcher.transform_query(params)
        await ImfAvailableIndicatorsFetcher.aextract_data(q, None)
        call = stub.calls[0]
        assert call["query"] == ""
        assert call["dataflows"] == ["WEO"]
        assert call["keywords"] == ["gold"]

    @pytest.mark.asyncio
    async def test_aextract_data_search_failure_wraps_in_openbb_error(
        self, monkeypatch
    ):
        """Any exception from ``search_indicators`` is wrapped in ``OpenBBError``."""
        stub = _StubMeta(raise_exc=RuntimeError("boom"))
        monkeypatch.setattr(
            "openbb_imf.utils.metadata.ImfMetadata",
            lambda: stub,
        )
        q = ImfAvailableIndicatorsFetcher.transform_query({"query": "x"})
        with pytest.raises(OpenBBError):
            await ImfAvailableIndicatorsFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_aextract_data_empty_results_raises(self, monkeypatch):
        """Empty results raise ``EmptyDataError``."""
        stub = _StubMeta(result=[])
        monkeypatch.setattr(
            "openbb_imf.utils.metadata.ImfMetadata",
            lambda: stub,
        )
        q = ImfAvailableIndicatorsFetcher.transform_query({"query": "nope"})
        with pytest.raises(EmptyDataError):
            await ImfAvailableIndicatorsFetcher.aextract_data(q, None)

    def test_transform_data_constructs_symbol_and_typed_rows(self):
        """``transform_data`` builds ``symbol`` from ``dataflow_id::indicator`` and validates rows."""
        q = ImfAvailableIndicatorsFetcher.transform_query({"query": "any"})
        raw = [
            {
                "agency_id": "IMF.STA",
                "dataflow_id": "WEO",
                "dataflow_name": "World Economic Outlook",
                "structure_id": "DSD_WEO",
                "dimension_id": "INDICATOR",
                "indicator": "NGDP_RPCH",
                "label": "Real GDP Growth",
                "description": "Real gross domestic product growth.",
            }
        ]
        out = ImfAvailableIndicatorsFetcher.transform_data(q, raw)
        assert isinstance(out[0], ImfAvailableIndicatorsData)
        assert out[0].symbol == "WEO::NGDP_RPCH"
        assert out[0].description == "Real GDP Growth"
        assert out[0].long_description == "Real gross domestic product growth."
