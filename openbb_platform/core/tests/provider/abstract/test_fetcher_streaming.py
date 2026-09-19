"""Tests for streaming fetchers."""

import asyncio
from collections.abc import AsyncIterator

import pytest

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams


class _StreamQueryParams(QueryParams):
    limit: int = 3


class _StreamData(Data):
    tick: int


class _StreamFetcher(Fetcher[_StreamQueryParams, AsyncIterator[_StreamData]]):
    @staticmethod
    def transform_query(params: dict) -> _StreamQueryParams:
        return _StreamQueryParams(**params)

    @staticmethod
    async def aextract_data(query, credentials, **kwargs) -> AsyncIterator[dict]:
        async def _gen():
            for index in range(query.limit):
                yield {"tick": index}

        return _gen()

    @staticmethod
    async def stream_data(query, data, **kwargs) -> AsyncIterator[_StreamData]:
        async for record in data:
            yield _StreamData.model_validate(record)


def test_is_streaming():
    assert _StreamFetcher.is_streaming is True


def test_data_type_unwraps_async_iterator():
    assert _StreamFetcher.data_type is _StreamData


def test_fetch_data_returns_stream():
    async def _run():
        stream = await _StreamFetcher.fetch_data({"limit": 2})
        return [row async for row in stream]

    rows = asyncio.run(_run())
    assert [row.tick for row in rows] == [0, 1]
    assert all(isinstance(row, _StreamData) for row in rows)


def test_fetcher_test_streaming_passes():
    _StreamFetcher.test({"limit": 3})


def test_test_stream_handles_short_stream():
    query = _StreamFetcher.transform_query({"limit": 1})
    _StreamFetcher._test_stream(query, None, max_items=2)


def test_base_stream_data_raises():
    with pytest.raises(NotImplementedError):
        Fetcher.stream_data(None, None)
