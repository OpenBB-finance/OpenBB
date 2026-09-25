"""Tests for the disk-backed result cache."""

import pytest

from openbb_tmx.utils.memo import memoize


class TestMemoize:
    """Holding an async function's result on disk."""

    @pytest.fixture
    def counted(self):
        """Count how often the wrapped function actually runs."""
        calls: list = []

        @memoize(ttl=60)
        async def work(value, keyword=None):
            """Record the call and echo its arguments."""
            calls.append((value, keyword))

            return {"value": value, "keyword": keyword}

        work.cache_clear()

        yield work, calls

        work.cache_clear()

    async def test_a_result_is_reused(self, counted):
        work, calls = counted

        assert await work("a") == {"value": "a", "keyword": None}
        assert await work("a") == {"value": "a", "keyword": None}
        assert len(calls) == 1

    async def test_each_argument_is_held_apart(self, counted):
        work, calls = counted
        await work("a")
        await work("a", keyword="b")

        assert len(calls) == 2

    async def test_clearing_forgets_every_result(self, counted):
        work, calls = counted
        await work("a")
        work.cache_clear()
        await work("a")

        assert len(calls) == 2

    async def test_clearing_tolerates_an_expired_result(self):
        """An expired key is still listed but can no longer be read."""
        import time

        @memoize(ttl=0.05)
        async def stale():
            """Store a result that expires almost immediately."""
            return "gone"

        stale.cache_clear()

        assert await stale() == "gone"

        time.sleep(0.1)
        stale.cache_clear()

        assert await stale() == "gone"

        stale.cache_clear()
