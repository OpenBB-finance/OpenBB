import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_ecb.models.ecb_interest_rates import ECBInterestRatesFetcher as Fetcher
from openbb_ecb.utils import query_builder


def test_transform_pivots_and_ffills():
    query = Fetcher.transform_query(
        {"start_date": date(2025, 1, 1), "end_date": date(2025, 1, 4)}
    )
    data = [
        {"PROVIDER_FM_ID": "DFR", "date": "2024-06-12", "OBS_VALUE": 3.75},
        {"PROVIDER_FM_ID": "DFR", "date": "2025-01-03", "OBS_VALUE": 3.0},
        {"PROVIDER_FM_ID": "MRR_FR", "date": "2024-06-12", "OBS_VALUE": 4.25},
        {"PROVIDER_FM_ID": "MLFR", "date": "2025-01-02", "OBS_VALUE": 4.5},
        {"PROVIDER_FM_ID": "DFR", "date": "2025-01-04", "OBS_VALUE": None},
        {"PROVIDER_FM_ID": "XXX", "date": "2024-06-12", "OBS_VALUE": 9.9},
    ]
    out = Fetcher.transform_data(query, data)
    assert [str(r.date) for r in out] == [
        "2025-01-01",
        "2025-01-02",
        "2025-01-03",
        "2025-01-04",
    ]
    assert out[0].deposit_facility == 3.75 and out[0].main_refinancing == 4.25
    assert out[0].marginal_lending is None
    assert out[1].marginal_lending == 4.5
    assert out[-1].deposit_facility == 3.0


def test_transform_default_window_and_absent_column():
    out = Fetcher.transform_data(
        Fetcher.transform_query({}),
        [{"PROVIDER_FM_ID": "DFR", "date": "2025-01-03", "OBS_VALUE": 2.4}],
    )
    assert out[0].deposit_facility == 2.4
    assert out[0].main_refinancing is None


def test_transform_empty_raises():
    with pytest.raises(EmptyDataError):
        Fetcher.transform_data(
            Fetcher.transform_query({}),
            [{"PROVIDER_FM_ID": "DFR", "date": "2025-01-03", "OBS_VALUE": None}],
        )


def test_aextract(monkeypatch):

    async def _fetch(*args, **kwargs):
        return [{"PROVIDER_FM_ID": "DFR", "date": "2025-01-03", "OBS_VALUE": 2.0}]

    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _fetch)
    raw = asyncio.run(
        Fetcher.aextract_data(Fetcher.transform_query({"use_cache": False}), None)
    )
    assert raw and raw[0]["OBS_VALUE"] == 2.0

    async def _empty(*args, **kwargs):
        return []

    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _empty)
    with pytest.raises(OpenBBError):
        asyncio.run(
            Fetcher.aextract_data(Fetcher.transform_query({"use_cache": False}), None)
        )
