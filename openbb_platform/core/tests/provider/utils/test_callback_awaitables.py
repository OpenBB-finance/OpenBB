"""Callbacks may produce awaitables without an async function declaration."""

import asyncio

import pytest

from openbb_core.provider.utils.helpers import maybe_coroutine


@pytest.mark.asyncio
async def test_sync_wrapper_result_is_awaited():
    async def calculate(value):
        return value + 1

    result = await maybe_coroutine(lambda: calculate(4))
    if asyncio.iscoroutine(result):
        result.close()
    assert result == 5


@pytest.mark.asyncio
async def test_callable_object_result_is_awaited():
    class Callback:
        async def __call__(self, value):
            return value * 2

    result = await maybe_coroutine(Callback(), 3)
    if asyncio.iscoroutine(result):
        result.close()
    assert result == 6


@pytest.mark.asyncio
async def test_future_result_is_awaited():
    future = asyncio.get_running_loop().create_future()
    future.set_result(7)
    assert await maybe_coroutine(lambda: future) == 7


@pytest.mark.asyncio
async def test_sync_values_and_exceptions_are_preserved():
    assert await maybe_coroutine(lambda x: x + 1, 2) == 3

    def fail():
        raise ValueError("callback failed")

    with pytest.raises(ValueError, match="callback failed"):
        await maybe_coroutine(fail)
