"""Tests for the EIA Data Browser model."""

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_us_eia.models.data_browser import (
    EiaDataBrowserFetcher,
    EiaDataBrowserQueryParams,
)

METADATA = {
    "response": {
        "id": "spt",
        "frequency": [
            {"id": "daily", "format": "YYYY-MM-DD"},
            {"id": "monthly", "format": "YYYY-MM"},
        ],
        "defaultFrequency": "daily",
        "data": {"value": {"units": "$/BBL"}},
        "facets": [{"id": "duoarea"}, {"id": "product"}],
    }
}

PAGE = {
    "response": {
        "total": "2",
        "dateFormat": "YYYY-MM",
        "data": [
            {"period": "2024-02", "product": "EPCBRENT", "value": "83.5"},
            {"period": "2024-01", "product": "EPCBRENT", "value": "80.1"},
        ],
    }
}


def _stub(monkeypatch, metadata=METADATA, page=PAGE):
    from openbb_core.provider.utils import helpers as core_helpers

    calls = {"urls": []}

    async def fake_amake_request(url, response_callback=None, **kwargs):
        calls["urls"].append(url)
        return metadata if "/data/" not in url else page

    monkeypatch.setattr(core_helpers, "amake_request", fake_amake_request)
    return calls


class TestDataBrowserQueryParams:
    """Route cleaning and facet string parsing."""

    def test_route_cleaned(self):
        query = EiaDataBrowserQueryParams(route=" /petroleum/pri/spt/data/ ")
        assert query.route == "petroleum/pri/spt"

    def test_facet_query_parses_pairs(self):
        query = EiaDataBrowserQueryParams(
            route="x", facets="duoarea:NUS; product:EPCBRENT,EPCWTI"
        )
        assert query.facet_query == {
            "duoarea": ["NUS"],
            "product": ["EPCBRENT", "EPCWTI"],
        }

    def test_facet_query_empty(self):
        assert EiaDataBrowserQueryParams(route="x").facet_query == {}

    def test_facet_query_invalid_pair_raises(self):
        query = EiaDataBrowserQueryParams(route="x", facets="duoarea=NUS")
        with pytest.raises(OpenBBError, match="Invalid facet filter"):
            _ = query.facet_query

    def test_transform_query_validates_facets(self):
        with pytest.raises(OpenBBError, match="Invalid facet filter"):
            EiaDataBrowserFetcher.transform_query({"route": "x", "facets": "bad"})


class TestDataBrowserFetcher:
    """Live-metadata resolution and the request pipeline."""

    @pytest.mark.asyncio
    async def test_fetch_data_end_to_end(self, monkeypatch):
        calls = _stub(monkeypatch)
        rows = await EiaDataBrowserFetcher.fetch_data(
            {
                "route": "petroleum/pri/spt",
                "frequency": "monthly",
                "facets": "product:EPCBRENT",
                "start_date": date(2024, 1, 1),
                "end_date": date(2024, 2, 29),
            },
            {"eia_api_key": "MOCK_KEY"},
        )
        assert len(rows) == 2
        assert rows[0].date == date(2024, 1, 1)
        assert rows[0].model_dump()["value"] == 80.1
        data_url = calls["urls"][-1]
        assert "start=2024-01" in data_url
        assert "end=2024-02" in data_url
        assert "facets%5Bproduct%5D%5B%5D=EPCBRENT" in data_url

    @pytest.mark.asyncio
    async def test_default_frequency_used(self, monkeypatch):
        calls = _stub(monkeypatch)
        await EiaDataBrowserFetcher.fetch_data(
            {"route": "petroleum/pri/spt"}, {"eia_api_key": "MOCK_KEY"}
        )
        assert "frequency=daily" in calls["urls"][-1]

    @pytest.mark.asyncio
    async def test_category_route_raises(self, monkeypatch):
        metadata = {"response": {"routes": [{"id": "spt"}, {"id": "gnd"}]}}
        _stub(monkeypatch, metadata=metadata)
        with pytest.raises(OpenBBError, match="not a data route"):
            await EiaDataBrowserFetcher.fetch_data(
                {"route": "petroleum/pri"}, {"eia_api_key": "MOCK_KEY"}
            )

    @pytest.mark.asyncio
    async def test_unknown_route_raises(self, monkeypatch):
        _stub(monkeypatch, metadata={"response": {}})
        with pytest.raises(OpenBBError, match="not a valid EIA data route"):
            await EiaDataBrowserFetcher.fetch_data(
                {"route": "nonsense"}, {"eia_api_key": "MOCK_KEY"}
            )

    @pytest.mark.asyncio
    async def test_invalid_frequency_raises(self, monkeypatch):
        _stub(monkeypatch)
        with pytest.raises(OpenBBError, match="Frequency 'hourly'"):
            await EiaDataBrowserFetcher.fetch_data(
                {"route": "petroleum/pri/spt", "frequency": "hourly"},
                {"eia_api_key": "MOCK_KEY"},
            )

    @pytest.mark.asyncio
    async def test_data_type_subset_requested(self, monkeypatch):
        calls = _stub(monkeypatch)
        await EiaDataBrowserFetcher.fetch_data(
            {"route": "petroleum/pri/spt", "data_type": "value"},
            {"eia_api_key": "MOCK_KEY"},
        )
        assert "data%5B0%5D=value" in calls["urls"][-1]

    @pytest.mark.asyncio
    async def test_invalid_data_type_raises(self, monkeypatch):
        _stub(monkeypatch)
        with pytest.raises(OpenBBError, match="Invalid data_type"):
            await EiaDataBrowserFetcher.fetch_data(
                {"route": "petroleum/pri/spt", "data_type": "quantity"},
                {"eia_api_key": "MOCK_KEY"},
            )

    @pytest.mark.asyncio
    async def test_unknown_facet_raises(self, monkeypatch):
        _stub(monkeypatch)
        with pytest.raises(OpenBBError, match="Invalid facet id"):
            await EiaDataBrowserFetcher.fetch_data(
                {"route": "petroleum/pri/spt", "facets": "stateId:TX"},
                {"eia_api_key": "MOCK_KEY"},
            )

    @pytest.mark.asyncio
    async def test_desc_sort_and_limit(self, monkeypatch):
        _stub(monkeypatch)
        rows = await EiaDataBrowserFetcher.fetch_data(
            {"route": "petroleum/pri/spt", "sort": "desc", "limit": 1},
            {"eia_api_key": "MOCK_KEY"},
        )
        assert len(rows) == 1
        assert rows[0].date == date(2024, 2, 1)
