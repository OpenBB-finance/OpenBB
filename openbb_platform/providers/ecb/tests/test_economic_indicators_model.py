import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_ecb.models.economic_indicators import (
    ECBEconomicIndicatorsFetcher as Fetcher,
    _build_title,
)
from openbb_ecb.utils import query_builder


def _stub(records):
    async def _fetch(*args, **kwargs):
        return [dict(r) for r in records]

    return _fetch


def test_build_title_uses_dimension_labels_only():
    record = {
        "_dim_ids": ["FREQ", "CURRENCY", "EXR_TYPE", "MISSING"],
        "FREQ__label": "Daily",
        "CURRENCY__label": "US dollar",
        "EXR_TYPE__label": "Spot",
        "UNIT__label": "USD",
    }
    assert _build_title(record) == "US dollar - Spot"


def test_transform_standardizes():
    query = Fetcher.transform_query({"symbol": "EXR::D.USD.EUR.SP00.A"})
    data = [
        {
            "_flow": "EXR",
            "series_key": "D.USD.EUR.SP00.A",
            "date": "2024-01-02",
            "OBS_VALUE": 1.09,
            "REF_AREA__label": "Euro area",
            "CURRENCY__label": "US dollar",
            "_dim_ids": ["FREQ", "CURRENCY"],
            "FREQ__label": "Daily",
            "UNIT": "USD",
        }
    ]
    out = Fetcher.transform_data(query, data)
    assert out[0].symbol == "EXR::D.USD.EUR.SP00.A"
    assert out[0].symbol_root == "EXR"
    assert out[0].value == 1.09
    assert out[0].frequency == "Daily"
    assert out[0].unit == "USD"
    assert out[0].country == "Euro area"


def test_aextract_valid(monkeypatch):
    monkeypatch.setattr(
        query_builder,
        "fetch_sdmx_data",
        _stub(
            [
                {
                    "series_key": "D.USD.EUR.SP00.A",
                    "date": "2024-01-02",
                    "OBS_VALUE": 1.09,
                }
            ]
        ),
    )
    query = Fetcher.transform_query(
        {"symbol": "EXR::D.USD.EUR.SP00.A", "use_cache": False}
    )
    raw = asyncio.run(Fetcher.aextract_data(query, None))
    assert raw[0]["_flow"] == "EXR"


def test_aextract_invalid_symbol_and_flow(monkeypatch):
    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _stub([]))
    with pytest.raises(OpenBBError):
        asyncio.run(
            Fetcher.aextract_data(
                Fetcher.transform_query({"symbol": "EXR", "use_cache": False}), None
            )
        )
    with pytest.raises(OpenBBError):
        asyncio.run(
            Fetcher.aextract_data(
                Fetcher.transform_query({"symbol": "ZZZ::key", "use_cache": False}),
                None,
            )
        )


def test_aextract_empty_raises(monkeypatch):
    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _stub([]))
    with pytest.raises(OpenBBError):
        asyncio.run(
            Fetcher.aextract_data(
                Fetcher.transform_query(
                    {"symbol": "EXR::D.USD.EUR.SP00.A", "use_cache": False}
                ),
                None,
            )
        )
