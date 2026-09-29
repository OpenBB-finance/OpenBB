"""Unit tests for ``openbb_sec.models.compare_company_facts``."""

import asyncio
import types

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_sec.models.compare_company_facts import (
    SecCompareCompanyFactsFetcher,
    SecCompareCompanyFactsQueryParams,
)


def _run(coro):
    """Run an async coroutine from a sync test (no pytest-asyncio)."""
    return asyncio.run(coro)


def _async_return(value):
    """Build a zero-arg awaitable returning ``value``."""

    async def _inner(*args, **kwargs):
        return value

    return _inner


class TestCompareCompanyFacts:
    """SecCompareCompanyFacts query validation + extract/transform."""

    def test_fact_default_when_empty(self):
        assert SecCompareCompanyFactsQueryParams(fact="").fact == "Revenues"

    def test_fact_passthrough(self):
        assert SecCompareCompanyFactsQueryParams(fact="Assets").fact == "Assets"

    def test_transform_query_passthrough(self):
        qp = SecCompareCompanyFactsFetcher.transform_query({"fact": "Assets"})
        assert isinstance(qp, SecCompareCompanyFactsQueryParams)

    def test_extract_with_symbol_warns_and_returns(self, monkeypatch):
        q = types.SimpleNamespace(
            symbol="AAPL",
            fact="Revenues",
            year=2023,
            calendar_period="q1",
            instantaneous=True,
            use_cache=False,
        )
        payload = {
            "metadata": {"x": 1},
            "data": [
                {
                    "cik": 320193,
                    "val": 1,
                    "accn": "a",
                    "entityName": "Apple",
                    "fact": "Revenues",
                }
            ],
        }
        monkeypatch.setattr(
            "openbb_sec.utils.frames.get_concept", _async_return(payload)
        )
        # instantaneous is ignored (and warns) when a symbol is present;
        # calendar_period is now respected for symbols, so it no longer warns.
        with pytest.warns(Warning):
            out = _run(SecCompareCompanyFactsFetcher.aextract_data(q, None))
        assert out["data"][0]["val"] == 1

    def test_extract_without_symbol_uses_frame(self, monkeypatch):
        q = types.SimpleNamespace(
            symbol=None,
            fact="Revenues",
            year=2023,
            calendar_period=None,
            instantaneous=False,
            use_cache=False,
        )
        monkeypatch.setattr("openbb_sec.utils.frames.get_frame", _async_return({}))
        # Empty frame -> EmptyDataError
        with pytest.raises(EmptyDataError):
            _run(SecCompareCompanyFactsFetcher.aextract_data(q, None))

    def test_extract_q4_universe_uses_get_universe_quarter4(self, monkeypatch):
        # No symbol + calendar_period='q4' + not instantaneous -> derived-Q4 universe.
        q = types.SimpleNamespace(
            symbol=None,
            fact="Revenues",
            year=2023,
            calendar_period="q4",
            instantaneous=False,
            use_cache=False,
        )
        payload = {"metadata": {"frame": "CY2023Q4"}, "data": [{"cik": 1, "val": 7}]}
        monkeypatch.setattr(
            "openbb_sec.utils.frames.get_universe_quarter4", _async_return(payload)
        )
        out = _run(SecCompareCompanyFactsFetcher.aextract_data(q, None))
        assert out["metadata"]["frame"] == "CY2023Q4"
        assert out["data"][0]["val"] == 7

    def test_transform_data_with_metadata(self):
        data = {
            "metadata": {"frame": "CY2023"},
            "data": [
                {
                    "cik": 320193,
                    "val": 100,
                    "accn": "0000320193-24-000081",
                    "entityName": "Apple Inc.",
                    "fact": "Revenues",
                }
            ],
        }
        res = SecCompareCompanyFactsFetcher.transform_data(
            types.SimpleNamespace(), data
        )
        assert res.metadata == {"frame": "CY2023"}
        assert len(res.result) == 1
        assert res.result[0].value == 100

    def test_transform_data_empty_raises(self):
        with pytest.raises(EmptyDataError):
            SecCompareCompanyFactsFetcher.transform_data(types.SimpleNamespace(), {})
