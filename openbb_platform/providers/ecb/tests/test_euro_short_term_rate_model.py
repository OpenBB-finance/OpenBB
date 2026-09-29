import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_ecb.models.euro_short_term_rate import (
    ECBEuroShortTermRateFetcher as Fetcher,
)
from openbb_ecb.utils import query_builder


def _stub(records):
    async def _fetch(*args, **kwargs):
        return [dict(r) for r in records]

    return _fetch


def _record(data_type, value, day="2025-01-02"):
    return {"DATA_TYPE_EST": data_type, "OBS_VALUE": value, "date": day}


def test_transform_pivots_and_scales():
    data = [
        _record("WT", 2.182),
        _record("R25", 2.16),
        _record("R75", 2.2),
        _record("TT", 64538),
        _record("NT", 919),
        _record("NB", 44),
        _record("VL", 43),
        _record("ZZ", 1),
        _record(None, 5),
        {"DATA_TYPE_EST": "WT", "OBS_VALUE": None, "date": "2025-01-03"},
    ]
    out = Fetcher.transform_data(Fetcher.transform_query({}), data)
    assert len(out) == 1
    row = out[0]
    assert round(row.rate, 5) == 0.02182
    assert row.percentile_25 == 0.0216
    assert row.large_bank_share_of_volume == 0.43
    assert row.volume == 64538.0
    assert row.transactions == 919 and row.number_of_banks == 44


def test_aextract(monkeypatch):
    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _stub([_record("WT", 2.0)]))
    out = asyncio.run(
        Fetcher.aextract_data(Fetcher.transform_query({"use_cache": False}), None)
    )
    assert out[0]["DATA_TYPE_EST"] == "WT"


def test_aextract_empty_raises(monkeypatch):
    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _stub([]))
    with pytest.raises(OpenBBError):
        asyncio.run(
            Fetcher.aextract_data(Fetcher.transform_query({"use_cache": False}), None)
        )
