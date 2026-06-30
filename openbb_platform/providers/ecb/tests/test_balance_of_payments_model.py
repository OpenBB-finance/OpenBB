"""Unit tests for the ECB balance of payments model."""

import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_ecb.models.balance_of_payments import (
    ECBBalanceOfPaymentsFetcher as Fetcher,
)
from openbb_ecb.utils import query_builder


def _stub(records):
    async def _fetch(*args, **kwargs):
        return [dict(r) for r in records]

    return _fetch


def test_transform_sums_and_pivots():
    """Component series sum by period and pivot to one row per period; gaps -> None."""
    query = Fetcher.transform_query({"report_type": "main"})
    data = [
        # financial_services style aggregate: two component series summed
        {"_item": "current_account", "date": "2023-03-31", "OBS_VALUE": 100.0},
        {"_item": "current_account", "date": "2023-03-31", "OBS_VALUE": 25.0},
        {"_item": "goods", "date": "2023-03-31", "OBS_VALUE": 50.0},
        {"_item": "current_account", "date": "2023-06-30", "OBS_VALUE": 120.0},
        {"_item": "goods", "date": "2023-06-30", "OBS_VALUE": None},  # skipped
    ]
    out = Fetcher.transform_data(query, data)
    assert len(out) == 2
    first = next(r for r in out if str(r.period) == "2023-03-31")
    assert first.current_account == 125.0  # summed
    assert first.goods == 50.0
    second = next(r for r in out if str(r.period) == "2023-06-30")
    assert second.goods is None  # gap -> None


def test_transform_empty_raises():
    """No data or all-null data raises."""
    query = Fetcher.transform_query({"report_type": "main"})
    with pytest.raises(OpenBBError):
        Fetcher.transform_data(query, [])
    with pytest.raises(OpenBBError):
        Fetcher.transform_data(
            query, [{"_item": "goods", "date": "2023-03-31", "OBS_VALUE": None}]
        )


def test_aextract_tags_item(monkeypatch):
    """Extract returns raw component records tagged with the item name."""
    monkeypatch.setattr(
        query_builder,
        "fetch_sdmx_data",
        _stub([{"date": "2023-03-31", "OBS_VALUE": 1.0}]),
    )
    query = Fetcher.transform_query(
        {
            "report_type": "main",
            "start_date": date(2023, 1, 1),
            "end_date": date(2023, 6, 30),
            "use_cache": False,
        }
    )
    raw = asyncio.run(Fetcher.aextract_data(query, None))
    assert raw and all("_item" in r for r in raw)
