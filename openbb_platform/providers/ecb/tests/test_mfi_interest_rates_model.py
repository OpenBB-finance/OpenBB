import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_ecb.models.mfi_interest_rates import (
    DEFAULT_MFI_SYMBOL,
    ECBMfiInterestRatesFetcher as Fetcher,
)
from openbb_ecb.utils import query_builder


def _stub(records):
    async def _fetch(*args, **kwargs):
        return [dict(r) for r in records]

    return _fetch


def test_symbol_validation():
    query = Fetcher.transform_query(
        {"symbol": "corporate_loans, household_consumer_credit"}
    )
    assert query.symbol == "corporate_loans,household_consumer_credit"
    listed = Fetcher.transform_query(
        {"symbol": ["corporate_loans", "household_other_loans"]}
    )
    assert listed.symbol == "corporate_loans,household_other_loans"
    with pytest.raises(ValidationError):
        Fetcher.transform_query({"symbol": "not_a_series"})


def test_transform_pivots_wide():
    query = Fetcher.transform_query({"symbol": "corporate_loans,household_other_loans"})
    data = [
        {"_series_name": "corporate_loans", "OBS_VALUE": 4.13, "date": "2025-01-01"},
        {
            "_series_name": "household_other_loans",
            "OBS_VALUE": 6.2,
            "date": "2025-01-01",
        },
        {"_series_name": "corporate_loans", "OBS_VALUE": 4.0, "date": "2025-02-01"},
        {"_series_name": "corporate_loans", "OBS_VALUE": None, "date": "2025-03-01"},
        {"_series_name": "unknown_series", "OBS_VALUE": 9.9, "date": "2025-01-01"},
    ]
    out = Fetcher.transform_data(query, data)
    assert [str(r.date) for r in out] == ["2025-01-01", "2025-02-01"]
    first = out[0].model_dump()
    assert first["corporate_loans"] == 4.13
    assert first["household_other_loans"] == 6.2
    second = out[1].model_dump()
    assert second["corporate_loans"] == 4.0
    assert second["household_other_loans"] is None


def test_transform_empty_raises():
    query = Fetcher.transform_query({"symbol": "corporate_loans"})
    with pytest.raises(EmptyDataError):
        Fetcher.transform_data(
            query,
            [
                {
                    "_series_name": "corporate_loans",
                    "OBS_VALUE": None,
                    "date": "2025-01-01",
                }
            ],
        )


def test_aextract(monkeypatch):
    monkeypatch.setattr(
        query_builder,
        "fetch_sdmx_data",
        _stub([{"OBS_VALUE": 4.1, "date": "2025-01-01"}]),
    )
    query = Fetcher.transform_query(
        {"symbol": "corporate_loans,household_other_loans", "use_cache": False}
    )
    raw = asyncio.run(Fetcher.aextract_data(query, None))
    assert {r["_series_name"] for r in raw} == {
        "corporate_loans",
        "household_other_loans",
    }


def test_aextract_empty_raises(monkeypatch):
    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _stub([]))
    with pytest.raises(OpenBBError):
        asyncio.run(
            Fetcher.aextract_data(
                Fetcher.transform_query(
                    {"symbol": "corporate_loans", "use_cache": False}
                ),
                None,
            )
        )


def test_none_and_empty_inputs_default(monkeypatch):
    assert Fetcher.transform_query({"symbol": None}).symbol == DEFAULT_MFI_SYMBOL
    assert Fetcher.transform_query({"symbol": "   "}).symbol == DEFAULT_MFI_SYMBOL

    captured = {}

    async def _fetch(flow_ref, key, **kwargs):
        captured["key"] = key
        return [{"OBS_VALUE": 1.0, "date": "2025-01-01"}]

    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _fetch)
    raw = asyncio.run(
        Fetcher.aextract_data(
            Fetcher.transform_query(
                {"symbol": "corporate_loans", "country": None, "use_cache": False}
            ),
            None,
        )
    )
    assert raw
    assert "U2" in captured["key"]
