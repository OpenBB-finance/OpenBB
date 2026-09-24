"""Unit tests for ``openbb_sec.utils.company_choices``."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from openbb_sec.utils.company_choices import get_company_choices


def _run(cached_request, use_cache=False, aget=None):
    with (
        patch("openbb_sec.utils.cache.cached_request", cached_request),
        patch("openbb_sec.utils.cache.aget_cached", AsyncMock(return_value=aget)),
        patch("openbb_sec.utils.cache.aset_cached", AsyncMock()) as aset,
    ):
        result = asyncio.run(get_company_choices(use_cache=use_cache))
    return result, aset


def test_maps_rows_to_choices():
    response = {
        "rows": [
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "cik": "320193",
                "sic_name": "Electronic Computers",
            },
            {"ticker": "MSFT", "name": "Microsoft Corp", "cik": "789019"},
            {"name": "No Ticker Co", "cik": "1"},
        ]
    }
    choices, _ = _run(AsyncMock(return_value=response))
    assert len(choices) == 2
    assert choices[0] == {
        "label": "Apple Inc.",
        "value": "AAPL",
        "extraInfo": {
            "description": "AAPL | 320193",
            "rightOfDescription": "Electronic Computers",
        },
    }
    assert choices[1]["extraInfo"]["rightOfDescription"] == ""


def test_paginates_until_short_page():
    page1 = {
        "rows": [
            {"ticker": f"T{i}", "name": f"C{i}", "cik": str(i)} for i in range(1000)
        ]
    }
    page2 = {"rows": [{"ticker": "LAST", "name": "Last Co", "cik": "9999"}]}
    mock = AsyncMock(side_effect=[page1, page2])
    choices, _ = _run(mock)
    assert len(choices) == 1001
    assert choices[-1]["value"] == "LAST"
    assert mock.await_count == 2


def test_label_falls_back_to_ticker():
    choices, _ = _run(AsyncMock(return_value={"rows": [{"ticker": "ZZZ", "cik": "9"}]}))
    assert choices[0]["label"] == "ZZZ"


def test_non_dict_response_returns_empty():
    choices, _ = _run(AsyncMock(return_value=None))
    assert choices == []


def test_dolt_error_raises():
    response = {
        "query_execution_status": "Error",
        "query_execution_message": "bad query",
    }
    with pytest.raises(Exception, match="bad query"):
        _run(AsyncMock(return_value=response))


def test_returns_cached_when_available():
    cached = [{"label": "Cached Co", "value": "X"}]
    choices, _ = _run(AsyncMock(), use_cache=True, aget=cached)
    assert choices == cached


def test_caches_result_when_use_cache():
    page = {"rows": [{"ticker": "AAPL", "name": "Apple", "cik": "1"}]}
    choices, aset = _run(AsyncMock(return_value=page), use_cache=True, aget=None)
    assert choices[0]["value"] == "AAPL"
    aset.assert_awaited_once()


def test_dedupes_ticker_and_keeps_best_ranked_row():
    response = {
        "rows": [
            {
                "ticker": "DE",
                "name": "Deere Funding Canada Corp",
                "cik": "315189",
                "rank": 42,
            },
            {
                "ticker": "DE",
                "name": "Deere & Company",
                "cik": "315189",
                "rank": 3,
            },
        ]
    }
    with (
        patch(
            "openbb_sec.utils.cache.cached_request", AsyncMock(return_value=response)
        ),
        patch("openbb_sec.utils.cache.aget_cached", AsyncMock(return_value=None)),
        patch("openbb_sec.utils.cache.aset_cached", AsyncMock()),
    ):
        choices = asyncio.run(get_company_choices(use_cache=False))

    assert len(choices) == 1
    assert choices[0]["value"] == "DE"
    assert choices[0]["label"] == "Deere & Company"
    assert choices[0]["extraInfo"]["description"] == "DE | 315189"


def test_dedupes_ticker_with_invalid_ranks():
    response = {
        "rows": [
            {
                "ticker": "DE",
                "name": "First",
                "cik": "315189",
                "rank": "bad-prev",
            },
            {
                "ticker": "DE",
                "name": "Second",
                "cik": "315189",
                "rank": "bad-curr",
            },
        ]
    }
    choices, _ = _run(AsyncMock(return_value=response))
    assert len(choices) == 1
    assert choices[0]["label"] == "First"
