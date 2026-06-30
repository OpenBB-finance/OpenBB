"""Unit tests for the ECB yield curve model."""

import asyncio

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_ecb.models.yield_curve import ECBYieldCurveFetcher as Fetcher
from openbb_ecb.utils import query_builder

_PREFIX = "B.U2.EUR.4F.G_N_A.SV_C_YM."


def _stub(records):
    async def _fetch(*args, **kwargs):
        return [dict(r) for r in records]

    return _fetch


def test_transform_maps_dedupes_scales():
    """series_key -> maturity, dedupe, nearest-date, /100 scaling."""
    query = Fetcher.transform_query({"date": "2023-11-20"})
    data = [
        {"series_key": _PREFIX + "SR_3M", "date": "2023-11-20", "OBS_VALUE": 3.8},
        {"series_key": _PREFIX + "SR_10Y", "date": "2023-11-20", "OBS_VALUE": 2.66},
        # duplicate (overlapping window) -> deduped
        {"series_key": _PREFIX + "SR_3M", "date": "2023-11-20", "OBS_VALUE": 3.8},
        {"series_key": _PREFIX + "ZZ", "date": "2023-11-20", "OBS_VALUE": 9},  # unknown
        {"series_key": _PREFIX + "SR_6M", "date": "2023-11-20", "OBS_VALUE": None},
    ]
    out = Fetcher.transform_data(query, data)
    by = {r.maturity: r.rate for r in out}
    assert round(by["month_3"], 5) == 0.038
    assert round(by["year_10"], 5) == 0.0266


def test_transform_empty_raises():
    """No mappable rows raises."""
    query = Fetcher.transform_query({"date": "2023-11-20"})
    with pytest.raises(EmptyDataError):
        Fetcher.transform_data(query, [{"series_key": _PREFIX + "ZZ", "OBS_VALUE": 1}])


def test_aextract(monkeypatch):
    """Extract fetches each requested date's window and returns raw records."""
    monkeypatch.setattr(
        query_builder,
        "fetch_sdmx_data",
        _stub(
            [{"series_key": _PREFIX + "SR_3M", "date": "2023-11-20", "OBS_VALUE": 3.8}]
        ),
    )
    query = Fetcher.transform_query(
        {"date": "2023-11-17,2023-11-20", "use_cache": False}
    )
    raw = asyncio.run(Fetcher.aextract_data(query, None))
    assert raw and all("series_key" in r for r in raw)
