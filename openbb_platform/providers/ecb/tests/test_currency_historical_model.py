"""Unit tests for the ECB currency historical model."""

import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_ecb.models import currency_historical as ch_module
from openbb_ecb.models.currency_historical import (
    ECBCurrencyHistoricalFetcher as Fetcher,
)
from openbb_ecb.utils import query_builder


def test_exr_pair_choices(monkeypatch):
    """The symbol dropdown lists the available EUR pairs; failure -> []."""
    pairs = ch_module._exr_pair_choices()
    assert "EURUSD" in pairs
    assert all(p.startswith("EUR") for p in pairs)

    from openbb_ecb.utils.metadata import EcbMetadata

    def _boom(self, dataflow_id):
        raise RuntimeError("no cache")

    monkeypatch.setattr(EcbMetadata, "get_dataflow_dimensions", _boom)
    assert ch_module._exr_pair_choices() == []


def _stub(records):
    async def _fetch(*args, **kwargs):
        return [dict(r) for r in records]

    return _fetch


def test_split_pair():
    """Pairs split into (base, quote); bad input raises."""
    assert Fetcher._split_pair("USD") == ("EUR", "USD")
    assert Fetcher._split_pair("EURUSD") == ("EUR", "USD")
    with pytest.raises(OpenBBError):
        Fetcher._split_pair("BADX")  # 4 chars -> invalid length


def test_transform_eur_quote_and_cross():
    """EUR-base, EUR-quote, cross, 3-letter, and empty segments are handled."""
    query = Fetcher.transform_query({"symbol": "EURUSD,USDEUR,USDGBP,GBP,"})
    data = [
        {"_currency": "USD", "date": "2024-01-02", "OBS_VALUE": 1.08},
        {"_currency": "GBP", "date": "2024-01-02", "OBS_VALUE": 0.85},
        {"_currency": "USD", "date": "2024-01-02", "OBS_VALUE": None},  # skipped
    ]
    out = {row.symbol: row.close for row in Fetcher.transform_data(query, data)}
    assert round(out["EURUSD"], 4) == 1.08
    assert round(out["USDEUR"], 4) == round(1 / 1.08, 4)
    assert round(out["USDGBP"], 4) == round(0.85 / 1.08, 4)
    assert round(out["GBP"], 4) == 0.85


def test_transform_skips_missing_dates():
    """A cross pair skips dates that are missing in one leg."""
    query = Fetcher.transform_query({"symbol": "USDGBP"})
    data = [
        {"_currency": "USD", "date": "2024-01-02", "OBS_VALUE": 1.08},
        {"_currency": "GBP", "date": "2024-01-02", "OBS_VALUE": 0.85},
        {"_currency": "USD", "date": "2024-01-03", "OBS_VALUE": 1.10},  # no GBP -> skip
    ]
    out = Fetcher.transform_data(query, data)
    assert [str(r.date) for r in out] == ["2024-01-02"]


def test_transform_empty_raises():
    """No computable data raises."""
    query = Fetcher.transform_query({"symbol": "EURUSD"})
    with pytest.raises(OpenBBError):
        Fetcher.transform_data(query, [])


def test_aextract_tags_currency(monkeypatch):
    """Extract returns raw per-currency records tagged with the currency."""
    monkeypatch.setattr(
        query_builder,
        "fetch_sdmx_data",
        _stub([{"date": "2024-01-02", "OBS_VALUE": 1.08}]),
    )
    query = Fetcher.transform_query(
        {
            "symbol": "EURUSD,USDGBP,",
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 1, 3),
            "use_cache": False,
        }
    )
    raw = asyncio.run(Fetcher.aextract_data(query, None))
    assert {r["_currency"] for r in raw} == {"USD", "GBP"}
