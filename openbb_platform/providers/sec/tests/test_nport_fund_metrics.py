"""Tests for the SEC NPORT Fund Metrics model."""

import asyncio

import pytest
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_sec.models.nport_fund_metrics import (
    SecNportFundMetricsFetcher,
    SecNportFundMetricsQueryParams,
)

_FETCH = "openbb_sec.models.nport_disclosure.SecNportDisclosureFetcher.fetch_data"


def test_transform_query_uppercases():
    """The symbol is upper-cased."""
    query = SecNportFundMetricsFetcher.transform_query({"symbol": "vmfxx"})
    assert isinstance(query, SecNportFundMetricsQueryParams)
    assert query.symbol == "VMFXX"


def test_aextract_returns_metadata(monkeypatch):
    """aextract_data returns the disclosure fetcher's metadata."""

    async def fake(self, params, credentials, **kwargs):
        return AnnotatedResult(result=[], metadata={"net_assets": "1"})

    monkeypatch.setattr(_FETCH, fake)
    query = SecNportFundMetricsFetcher.transform_query({"symbol": "X"})
    assert asyncio.run(SecNportFundMetricsFetcher.aextract_data(query, None)) == {
        "net_assets": "1"
    }


def test_aextract_without_metadata(monkeypatch):
    """A plain-list result yields empty metadata."""

    async def fake(self, params, credentials, **kwargs):
        return []

    monkeypatch.setattr(_FETCH, fake)
    query = SecNportFundMetricsFetcher.transform_query({"symbol": "X"})
    assert asyncio.run(SecNportFundMetricsFetcher.aextract_data(query, None)) == {}


def test_transform_data_monthly():
    """Monthly NPORT metadata becomes one row per reporting month."""
    query = SecNportFundMetricsFetcher.transform_query({"symbol": "X"})
    data = {
        "fund_name": "Fund",
        "net_assets": "100",
        "total_assets": "110",
        "cash_and_equivalents": "5",
        "returns": {"2024-03-31": 0.01, "2024-02-29": 0.02},
        "flow": {"2024-03-31": {"creation": "10", "redemption": "4"}},
        "gains": {"2024-03-31": {"realized": "3", "unrealized": "2"}},
    }
    rows = SecNportFundMetricsFetcher.transform_data(query, data)
    assert len(rows) == 2
    latest = rows[0].model_dump()
    assert latest["total_return"] == 0.01
    assert latest["net_flow"] == 6.0
    assert latest["realized_gains"] == 3.0
    assert rows[1].model_dump()["net_flow"] is None


def test_transform_data_snapshot():
    """N-MFP metadata (no monthly data) becomes a single snapshot row."""
    query = SecNportFundMetricsFetcher.transform_query({"symbol": "X"})
    data = {
        "fund_name": "MMF",
        "period_ending": "2026-05-31",
        "net_assets": "100",
        "seven_day_gross_yield": 0.05,
        "weighted_average_maturity": 14,
        "weighted_average_life": 40,
    }
    rows = SecNportFundMetricsFetcher.transform_data(query, data)
    assert len(rows) == 1
    row = rows[0].model_dump()
    assert row["seven_day_gross_yield"] == 0.05
    assert row["weighted_average_maturity"] == 14
    assert row["weighted_average_life"] == 40
    assert row["total_return"] is None


def test_transform_data_empty():
    """Metadata with neither months nor a period raises EmptyDataError."""
    query = SecNportFundMetricsFetcher.transform_query({"symbol": "X"})
    with pytest.raises(EmptyDataError):
        SecNportFundMetricsFetcher.transform_data(query, {})
