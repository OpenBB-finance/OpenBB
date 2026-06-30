"""Unit tests for the ECB key interest rates model."""

import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_ecb.models.ecb_interest_rates import ECBInterestRatesFetcher as Fetcher
from openbb_ecb.utils import query_builder


def _stub(records):
    async def _fetch(*args, **kwargs):
        return [dict(r) for r in records]

    return _fetch


def test_transform_forward_fills():
    """Sparse change points are forward-filled to a daily series in-window."""
    query = Fetcher.transform_query(
        {
            "interest_rate_type": "deposit",
            "start_date": date(2025, 1, 1),
            "end_date": date(2025, 1, 5),
        }
    )
    data = [
        {"date": "2024-06-12", "OBS_VALUE": 3.75},
        {"date": "2025-01-03", "OBS_VALUE": 3.0},
        {"date": "2025-01-04", "OBS_VALUE": None},  # ignored
    ]
    out = Fetcher.transform_data(query, data)
    assert [str(r.date) for r in out] == [
        "2025-01-01",
        "2025-01-02",
        "2025-01-03",
        "2025-01-04",
        "2025-01-05",
    ]
    assert out[0].rate == 3.75 and out[-1].rate == 3.0


def test_transform_default_window_and_empty():
    """Default window uses min->today; all-null data raises."""
    out = Fetcher.transform_data(
        Fetcher.transform_query({"interest_rate_type": "lending"}),
        [{"date": "2025-01-03", "OBS_VALUE": 2.4}],
    )
    assert out[0].rate == 2.4
    with pytest.raises(EmptyDataError):
        Fetcher.transform_data(
            Fetcher.transform_query({"interest_rate_type": "lending"}),
            [{"date": "2025-01-03", "OBS_VALUE": None}],
        )


def test_aextract(monkeypatch):
    """Extract returns the raw change-point records."""
    monkeypatch.setattr(
        query_builder,
        "fetch_sdmx_data",
        _stub([{"date": "2025-01-03", "OBS_VALUE": 3.0}]),
    )
    out = asyncio.run(
        Fetcher.aextract_data(
            Fetcher.transform_query(
                {"interest_rate_type": "deposit", "use_cache": False}
            ),
            None,
        )
    )
    assert out[0]["OBS_VALUE"] == 3.0


def test_aextract_empty_raises(monkeypatch):
    """No records raises."""
    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _stub([]))
    with pytest.raises(OpenBBError):
        asyncio.run(
            Fetcher.aextract_data(
                Fetcher.transform_query(
                    {"interest_rate_type": "refinancing", "use_cache": False}
                ),
                None,
            )
        )
