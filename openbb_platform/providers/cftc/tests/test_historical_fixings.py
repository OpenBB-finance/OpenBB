import asyncio
from datetime import date, timedelta

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_cftc.models.historical_fixings import (
    CftcHistoricalFixingsData,
    CftcHistoricalFixingsFetcher,
    CftcHistoricalFixingsQueryParams,
    build_series,
)

SERIES = {
    date(2026, 7, 22): 0.036400,
    date(2026, 7, 23): 0.036500,
    date(2026, 7, 24): 0.036300,
}


def test_build_series_orders_and_differences():
    rows = build_series(SERIES)

    assert [r["date"] for r in rows] == sorted(SERIES)
    assert rows[0]["change_bps"] is None
    assert rows[0]["rate"] == pytest.approx(3.64)
    assert rows[1]["change_bps"] == pytest.approx(1.0)
    assert rows[2]["change_bps"] == pytest.approx(-2.0)


def test_build_series_handles_an_empty_window():
    assert build_series({}) == []


def test_transform_query_defaults_to_a_year_back():
    query = CftcHistoricalFixingsFetcher.transform_query({})

    assert query.index == "SOFR"
    assert (query.end_date - query.start_date) == timedelta(days=365)


def test_transform_query_keeps_an_explicit_window():
    query = CftcHistoricalFixingsFetcher.transform_query(
        {
            "index": "euribor",
            "start_date": date(2026, 1, 1),
            "end_date": date(2026, 7, 1),
        }
    )

    assert query.index == "EURIBOR"
    assert query.start_date == date(2026, 1, 1)
    assert query.end_date == date(2026, 7, 1)


def test_transform_query_backfills_only_the_start():
    query = CftcHistoricalFixingsFetcher.transform_query({"end_date": date(2026, 7, 1)})

    assert query.end_date == date(2026, 7, 1)
    assert query.start_date == date(2026, 7, 1) - timedelta(days=365)


def test_index_validator_passes_non_strings():
    query = CftcHistoricalFixingsQueryParams(index="sofr")

    assert query.index == "SOFR"


def _patch_fixings(monkeypatch, fixings):
    async def _get(index, start_date, end_date, use_cache=True):
        return fixings

    monkeypatch.setattr("openbb_cftc.utils.fixings.get_fixings", _get)


def test_aextract_returns_the_published_series(monkeypatch):
    _patch_fixings(monkeypatch, SERIES)
    query = CftcHistoricalFixingsFetcher.transform_query({"index": "SOFR"})

    assert (
        asyncio.run(CftcHistoricalFixingsFetcher.aextract_data(query, None)) == SERIES
    )


def test_aextract_rejects_an_unknown_index(monkeypatch):
    query = CftcHistoricalFixingsQueryParams(index="NOPE")

    with pytest.raises(EmptyDataError, match="not a published benchmark"):
        asyncio.run(CftcHistoricalFixingsFetcher.aextract_data(query, None))


def test_aextract_raises_on_an_empty_window(monkeypatch):
    _patch_fixings(monkeypatch, {})
    query = CftcHistoricalFixingsFetcher.transform_query({"index": "SOFR"})

    with pytest.raises(EmptyDataError, match="No SOFR fixings"):
        asyncio.run(CftcHistoricalFixingsFetcher.aextract_data(query, None))


def test_transform_data_summarizes_the_window():
    query = CftcHistoricalFixingsFetcher.transform_query({"index": "SOFR"})
    result = CftcHistoricalFixingsFetcher.transform_data(query, SERIES)

    assert all(isinstance(r, CftcHistoricalFixingsData) for r in result.result)

    meta = result.metadata

    assert meta["index"] == "SOFR"
    assert meta["source"] == "nyfed"
    assert meta["series"] == "secured/sofr"
    assert meta["basis"] == 360.0
    assert meta["observations"] == 3
    assert meta["start_date"] == "2026-07-22"
    assert meta["end_date"] == "2026-07-24"
    assert meta["latest"] == pytest.approx(3.63)
    assert meta["low"] == pytest.approx(3.63)
    assert meta["high"] == pytest.approx(3.65)


def test_transform_data_reports_a_blank_series_path():
    query = CftcHistoricalFixingsFetcher.transform_query({"index": "CORRA"})
    result = CftcHistoricalFixingsFetcher.transform_data(query, SERIES)

    assert result.metadata["series"] is None
