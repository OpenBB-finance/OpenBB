"""Tests for the ``BlsSeriesFetcher``."""

import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_bls.models.series import (
    BlsSeriesData,
    BlsSeriesFetcher,
    BlsSeriesQueryParams,
)


def test_series_symbol_choices_endpoint_is_category_scoped(stub_cache_path):
    """The symbol picker returns the chosen category's series as {label, value}."""
    import openbb_bls.routers.core as core_mod
    from openbb_bls.routers.core import series_symbol_choices

    core_mod._SYMBOL_CHOICES_CACHE.clear()
    cpi = asyncio.run(series_symbol_choices("cpi"))
    assert cpi and all(set(o) == {"label", "value"} for o in cpi)
    # Scoped to the requested category (not the full cross-category universe).
    assert {o["value"] for o in cpi} == {"CUUR0000SA0", "CUUR0000SAF1"}
    assert any("All items in U.S. city average" in o["label"] for o in cpi)
    # A different category returns its own series; result is memoized.
    assert {o["value"] for o in asyncio.run(series_symbol_choices("ppi"))} == {"WPU01"}
    assert asyncio.run(series_symbol_choices("cpi")) is cpi
    # Unknown categories degrade to an empty option list.
    assert asyncio.run(series_symbol_choices("does-not-exist")) == []
    core_mod._SYMBOL_CHOICES_CACHE.clear()


def test_transform_query_builds_params():
    """``transform_query`` constructs a ``BlsSeriesQueryParams`` instance."""
    params = BlsSeriesFetcher.transform_query(
        {
            "symbol": "APU0000701111",
            "start_date": date(2022, 1, 1),
            "end_date": date(2022, 12, 1),
        }
    )
    assert isinstance(params, BlsSeriesQueryParams)
    assert params.symbol == "APU0000701111"
    assert params.calculations is True


def test_aextract_data_single_chunk_returns_canned_payload(monkeypatch):
    """Stub ``get_bls_timeseries`` to verify a one-chunk happy path."""
    calls: list[dict] = []

    async def fake_fetch(**kwargs):
        calls.append(kwargs)
        return {
            "data": [
                {
                    "symbol": "APU0000701111",
                    "date": "2022-06-01",
                    "value": 1.5,
                }
            ],
            "metadata": {"APU0000701111": {"series_title": "Flour"}},
            "messages": [],
        }

    monkeypatch.setattr("openbb_bls.utils.helpers.get_bls_timeseries", fake_fetch)
    params = BlsSeriesFetcher.transform_query(
        {
            "symbol": "APU0000701111",
            "start_date": date(2022, 1, 1),
            "end_date": date(2022, 12, 1),
        }
    )
    out = asyncio.run(
        BlsSeriesFetcher.aextract_data(params, credentials={"bls_api_key": "k"})
    )
    assert len(calls) == 1
    assert out["data"][0]["symbol"] == "APU0000701111"
    assert out["metadata"]["APU0000701111"]["series_title"] == "Flour"


def test_aextract_data_chunks_symbols(monkeypatch):
    """Symbol lists longer than 50 fan out across multiple requests."""
    call_counter = {"n": 0}

    async def fake_fetch(**kwargs):
        call_counter["n"] += 1
        return {
            "data": [
                {"symbol": kwargs["series_ids"][0], "date": "2022-01-01", "value": 1.0}
            ],
            "metadata": {},
            "messages": [],
        }

    monkeypatch.setattr("openbb_bls.utils.helpers.get_bls_timeseries", fake_fetch)
    # 105 symbols → ceil(105/50)=3 chunks; one year range so 3 total tasks.
    symbols = ",".join(f"S{i:04d}" for i in range(105))
    params = BlsSeriesFetcher.transform_query(
        {
            "symbol": symbols,
            "start_date": date(2022, 1, 1),
            "end_date": date(2022, 12, 1),
        }
    )
    asyncio.run(
        BlsSeriesFetcher.aextract_data(params, credentials={"bls_api_key": "k"})
    )
    assert call_counter["n"] == 3


def test_aextract_data_chunks_years(monkeypatch):
    """Year spans wider than 20 fan out across multiple year-range requests."""
    call_counter = {"n": 0}

    async def fake_fetch(**kwargs):
        call_counter["n"] += 1
        return {
            "data": [
                {"symbol": "APU", "date": f"{kwargs['start_year']}-01-01", "value": 1.0}
            ],
            "metadata": {},
            "messages": [],
        }

    monkeypatch.setattr("openbb_bls.utils.helpers.get_bls_timeseries", fake_fetch)
    params = BlsSeriesFetcher.transform_query(
        {
            "symbol": "APU",
            "start_date": date(1980, 1, 1),
            "end_date": date(2025, 12, 31),
        }
    )
    asyncio.run(
        BlsSeriesFetcher.aextract_data(params, credentials={"bls_api_key": "k"})
    )
    # 1980..2025 = 46 years → ceil(46/20)=3 year chunks
    assert call_counter["n"] == 3


def test_aextract_data_all_empty_raises_openbb_error(monkeypatch):
    """``EmptyDataError`` returns from every fan-out collapse into ``OpenBBError``."""

    async def fake_fetch(**kwargs):
        return EmptyDataError("no rows for that window")

    monkeypatch.setattr("openbb_bls.utils.helpers.get_bls_timeseries", fake_fetch)
    params = BlsSeriesFetcher.transform_query(
        {
            "symbol": "APU",
            "start_date": date(2022, 1, 1),
            "end_date": date(2022, 12, 1),
        }
    )
    with pytest.raises(OpenBBError, match="no rows for that window"):
        asyncio.run(
            BlsSeriesFetcher.aextract_data(params, credentials={"bls_api_key": "k"})
        )


def test_aextract_data_all_empty_no_messages_raises_empty(monkeypatch):
    """When fetch returns empty data + no messages, raise ``EmptyDataError``."""

    async def fake_fetch(**kwargs):
        return {"data": [], "metadata": {}, "messages": []}

    monkeypatch.setattr("openbb_bls.utils.helpers.get_bls_timeseries", fake_fetch)
    params = BlsSeriesFetcher.transform_query(
        {
            "symbol": "APU",
            "start_date": date(2022, 1, 1),
            "end_date": date(2022, 12, 1),
        }
    )
    with pytest.raises(EmptyDataError, match="returned empty"):
        asyncio.run(
            BlsSeriesFetcher.aextract_data(params, credentials={"bls_api_key": "k"})
        )


def test_earliest_begin_year_variants(monkeypatch):
    """``_earliest_begin_year`` resolves the min begin year or returns None."""
    from pandas import DataFrame

    import openbb_bls.models.series as sm
    import openbb_bls.utils.metadata as md

    # Guards: no category / no symbols.
    assert sm._earliest_begin_year(["X"], None) is None
    assert sm._earliest_begin_year([], "cpi") is None

    def fake_get(self, category):
        if category == "boom":
            raise KeyError("unknown category")
        if category == "nocol":
            return DataFrame([{"series_id": "A"}])
        return DataFrame(
            [
                {"series_id": "A", "begin_year": "1990"},
                {"series_id": "B", "begin_year": "1975"},
                {"series_id": "C", "begin_year": "bad"},
            ]
        )

    monkeypatch.setattr(md.BlsMetadata, "get_series", fake_get)
    assert sm._earliest_begin_year(["A"], "boom") is None  # lookup error
    assert sm._earliest_begin_year(["A"], "nocol") is None  # no begin_year column
    assert sm._earliest_begin_year(["A", "B", "C"], "ok") == 1975  # min, junk skipped
    assert sm._earliest_begin_year(["Z"], "ok") is None  # no matching symbols


def test_aextract_data_default_uses_full_history(monkeypatch):
    """No ``start_date`` -> the series' begin year from metadata."""
    import openbb_bls.models.series as sm

    seen: list[tuple] = []

    async def fake_fetch(**kwargs):
        seen.append((kwargs["start_year"], kwargs["end_year"]))
        return {
            "data": [{"symbol": "APU", "date": "2000-01-01", "value": 1.0}],
            "metadata": {},
            "messages": [],
        }

    monkeypatch.setattr("openbb_bls.utils.helpers.get_bls_timeseries", fake_fetch)
    monkeypatch.setattr(sm, "_earliest_begin_year", lambda symbols, category: 1995)
    params = BlsSeriesFetcher.transform_query({"symbol": "APU"})
    asyncio.run(
        BlsSeriesFetcher.aextract_data(params, credentials={"bls_api_key": "k"})
    )
    assert seen[0][0] == 1995


def test_aextract_data_default_dates_fall_back(monkeypatch):
    """When metadata can't resolve the begin year, default to a 20-year window."""
    import openbb_bls.models.series as sm

    seen: list[tuple] = []

    async def fake_fetch(**kwargs):
        seen.append((kwargs["start_year"], kwargs["end_year"]))
        return {
            "data": [{"symbol": "APU", "date": "2022-01-01", "value": 1.0}],
            "metadata": {},
            "messages": [],
        }

    monkeypatch.setattr("openbb_bls.utils.helpers.get_bls_timeseries", fake_fetch)
    monkeypatch.setattr(sm, "_earliest_begin_year", lambda symbols, category: None)
    params = BlsSeriesFetcher.transform_query({"symbol": "APU"})
    asyncio.run(
        BlsSeriesFetcher.aextract_data(params, credentials={"bls_api_key": "k"})
    )
    assert seen, "fetch must be invoked at least once"
    start, end = seen[0]
    assert end - start in (19, 20)


def test_aextract_data_without_credentials(monkeypatch):
    """Missing credentials are tolerated; the helper receives ``api_key=''``."""
    captured: dict = {}

    async def fake_fetch(**kwargs):
        captured.update(kwargs)
        return {
            "data": [{"symbol": "X", "date": "2022-01-01", "value": 1.0}],
            "metadata": {},
            "messages": [],
        }

    monkeypatch.setattr("openbb_bls.utils.helpers.get_bls_timeseries", fake_fetch)
    params = BlsSeriesFetcher.transform_query(
        {"symbol": "X", "start_date": date(2022, 1, 1), "end_date": date(2022, 12, 31)}
    )
    asyncio.run(BlsSeriesFetcher.aextract_data(params, credentials=None))
    assert captured["api_key"] == ""


def test_transform_data_applies_bounds_and_warnings():
    """``transform_data`` filters by start/end date and warns on messages."""
    query = BlsSeriesFetcher.transform_query(
        {
            "symbol": "X",
            "start_date": date(2022, 2, 1),
            "end_date": date(2022, 11, 30),
        }
    )
    payload = {
        "data": [
            {"symbol": "X", "date": "2022-01-01", "value": 1.0},
            {"symbol": "X", "date": "2022-06-01", "value": 2.0},
            {"symbol": "X", "date": "2022-12-31", "value": 3.0},
        ],
        "metadata": {"X": {"series_title": "Demo"}},
        "messages": ["watch out"],
    }
    with pytest.warns(UserWarning, match="watch out"):
        result = BlsSeriesFetcher.transform_data(query, payload)
    assert [r.value for r in result.result] == [2.0]
    assert all(isinstance(r, BlsSeriesData) for r in result.result)
    assert result.metadata == {"X": {"series_title": "Demo"}}


def test_transform_data_without_bounds_returns_all_rows():
    """No date bounds → every row in the payload survives."""
    query = BlsSeriesFetcher.transform_query({"symbol": "X"})
    payload = {
        "data": [
            {"symbol": "X", "date": "2020-01-01", "value": 1.0},
            {"symbol": "X", "date": "2021-01-01", "value": 2.0},
        ],
        "metadata": {},
        "messages": [],
    }
    result = BlsSeriesFetcher.transform_data(query, payload)
    assert len(result.result) == 2
