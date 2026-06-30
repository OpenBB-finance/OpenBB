"""Unit tests for the ECB MFI interest rates model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from pydantic import ValidationError

from openbb_ecb.models.mfi_interest_rates import ECBMfiInterestRatesFetcher as Fetcher
from openbb_ecb.utils import query_builder


def _stub(records):
    async def _fetch(*args, **kwargs):
        return [dict(r) for r in records]

    return _fetch


def test_symbol_validation():
    """Curated series validate; unknown series raise."""
    query = Fetcher.transform_query(
        {"symbol": "corporate_loans, household_consumer_credit"}
    )
    assert query.symbol == "corporate_loans,household_consumer_credit"
    with pytest.raises(ValidationError):
        Fetcher.transform_query({"symbol": "not_a_series"})


def test_transform_maps_to_economic_indicators():
    """Rows map onto the EconomicIndicators model fields."""
    query = Fetcher.transform_query({"symbol": "corporate_loans"})
    data = [
        {
            "_series_name": "corporate_loans",
            "_key": "M.U2.B.A2A.A.R.A.2240.EUR.N",
            "OBS_VALUE": 4.13,
            "date": "2025-01-01",
            "REF_AREA__label": "Euro area",
            "TITLE": "Loans to NFCs",
        },
        {"_series_name": "corporate_loans", "OBS_VALUE": None, "date": "2025-02-01"},
    ]
    out = Fetcher.transform_data(query, data)
    assert len(out) == 1
    assert out[0].symbol_root == "corporate_loans"
    assert out[0].symbol.startswith("MIR::")
    assert out[0].value == 4.13
    assert out[0].country == "Euro area"


def test_aextract(monkeypatch):
    """Extract returns raw records tagged with the series name and key."""
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
    """No data raises."""
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
    """Framework-supplied None/empty for symbol & country fall back to defaults.

    Regression: via the REST API the framework passes the standard
    ``EconomicIndicators`` defaults explicitly — ``country=None`` crashed
    ``.upper()`` (500) and ``symbol=None`` failed the curated-set validator.
    """
    assert (
        Fetcher.transform_query({"symbol": None}).symbol
        == "household_loans_for_house_purchase"
    )
    assert (
        Fetcher.transform_query({"symbol": "   "}).symbol
        == "household_loans_for_house_purchase"
    )

    captured = {}

    async def _fetch(flow_ref, key, **kwargs):
        captured["key"] = key
        return [{"OBS_VALUE": 1.0, "date": "2025-01-01"}]

    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _fetch)
    raw = asyncio.run(
        Fetcher.aextract_data(
            Fetcher.transform_query({"country": None, "use_cache": False}), None
        )
    )
    assert raw  # did not crash on country=None
    assert "U2" in captured["key"]  # country None resolved to the euro-area default
