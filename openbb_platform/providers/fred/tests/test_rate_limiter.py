"""Tests for the throttled, retrying, cached FRED transport."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_fred.utils import rate_limiter


class _Response:
    """A stand-in for the client response the transport reads."""

    def __init__(self, payload=None, status: int = 200, retry_after=None):
        self.payload = payload if payload is not None else {}
        self.status = status
        self.headers = {} if retry_after is None else {"Retry-After": retry_after}

    async def json(self):
        """Return the decoded body."""
        return self.payload


class _Clock:
    """A monotonic clock the test winds forward by hand."""

    def __init__(self, now: float = 1000.0):
        self.now = now

    def monotonic(self) -> float:
        """Return the time the test has wound to."""
        return self.now


@pytest.fixture(autouse=True)
def _unthrottled(monkeypatch):
    """Drop the request gap so the transport tests do not wait on it."""
    monkeypatch.setattr(rate_limiter, "MIN_INTERVAL_SECONDS", 0.0)
    monkeypatch.setattr(rate_limiter, "_last_request_at", 0.0)
    rate_limiter.cache_clear()
    yield
    rate_limiter.cache_clear()


def _serve(monkeypatch, responses: list, calls: list | None = None):
    """Answer each request with the next response in turn."""
    queue = list(responses)

    async def amake_request(url, response_callback=None, **kwargs):
        if calls is not None:
            calls.append(url)

        response = queue.pop(0) if len(queue) > 1 else queue[0]

        return await response_callback(response, None)

    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.amake_request", amake_request
    )


class TestFredGet:
    """One request, throttled and cached."""

    async def test_the_payload_is_returned(self, monkeypatch):
        _serve(monkeypatch, [_Response({"ok": True})])

        assert await rate_limiter.fred_get("https://x/a", use_cache=False) == {
            "ok": True
        }

    async def test_a_repeat_is_served_from_memory(self, monkeypatch):
        calls: list = []
        _serve(monkeypatch, [_Response({"ok": True})], calls)

        await rate_limiter.fred_get("https://x/b?api_key=one")
        await rate_limiter.fred_get("https://x/b?api_key=one")

        assert len(calls) == 1

    async def test_the_key_does_not_split_the_cache(self, monkeypatch):
        calls: list = []
        _serve(monkeypatch, [_Response({"ok": True})], calls)

        await rate_limiter.fred_get("https://x/c?api_key=one")
        await rate_limiter.fred_get("https://x/c?api_key=two")

        assert len(calls) == 1

    async def test_a_cached_payload_is_handed_over_as_a_copy(self, monkeypatch):
        _serve(monkeypatch, [_Response({"rows": [1, 2]})])

        first = await rate_limiter.fred_get("https://x/d")
        first["rows"].append(3)
        second = await rate_limiter.fred_get("https://x/d")

        assert second["rows"] == [1, 2]

    async def test_an_empty_payload_is_not_cached(self, monkeypatch):
        calls: list = []
        _serve(monkeypatch, [_Response({})], calls)

        await rate_limiter.fred_get("https://x/e")
        await rate_limiter.fred_get("https://x/e")

        assert len(calls) == 2

    async def test_a_refused_request_is_not_cached(self, monkeypatch):
        calls: list = []

        async def amake_request(url, response_callback=None, **kwargs):
            calls.append(url)
            raise RuntimeError("boom")

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", amake_request
        )

        for _ in range(2):
            with pytest.raises(RuntimeError):
                await rate_limiter.fred_get("https://x/f")

        assert len(calls) == 2

    async def test_a_rate_limited_response_is_retried(self, monkeypatch):
        calls: list = []
        _serve(
            monkeypatch,
            [_Response(status=429, retry_after="0"), _Response({"ok": True})],
            calls,
        )

        got = await rate_limiter.fred_get("https://x/g", use_cache=False)

        assert got == {"ok": True}
        assert len(calls) == 2

    async def test_a_rate_limit_that_never_lifts_is_reported(self, monkeypatch):
        _serve(monkeypatch, [_Response(status=429, retry_after="0")])

        with pytest.raises(OpenBBError, match="rate limit exceeded"):
            await rate_limiter.fred_get("https://x/h", use_cache=False, max_retries=1)

    async def test_a_rate_limit_in_the_body_is_retried(self, monkeypatch):
        calls: list = []
        _serve(
            monkeypatch,
            [_Response({"error_code": "429"}), _Response({"ok": True})],
            calls,
        )

        got = await rate_limiter.fred_get("https://x/i", use_cache=False)

        assert got == {"ok": True}
        assert len(calls) == 2

    async def test_an_unreadable_retry_after_falls_back_to_backoff(self, monkeypatch):
        monkeypatch.setattr(rate_limiter, "DEFAULT_BACKOFF_SECONDS", 0.0)
        calls: list = []
        _serve(
            monkeypatch,
            [_Response(status=429, retry_after="soon"), _Response({"ok": True})],
            calls,
        )

        assert await rate_limiter.fred_get("https://x/j", use_cache=False) == {
            "ok": True
        }

    async def test_a_reader_of_the_raw_response_is_used(self, monkeypatch):
        async def read(response, session):
            return "read by hand"

        _serve(monkeypatch, [_Response({"ok": True})])

        got = await rate_limiter.fred_get(
            "https://x/k", response_callback=read, use_cache=False
        )

        assert got == "read by hand"

    async def test_concurrent_callers_share_one_request(self, monkeypatch):
        import asyncio

        calls: list = []

        async def amake_request(url, response_callback=None, **kwargs):
            calls.append(url)
            await asyncio.sleep(0.05)
            return await response_callback(_Response({"ok": True}), None)

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", amake_request
        )
        got = await asyncio.gather(
            *(rate_limiter.fred_get("https://x/l") for _ in range(4))
        )

        assert len(calls) == 1
        assert got == [{"ok": True}] * 4

    async def test_a_shared_failure_reaches_every_caller(self, monkeypatch):
        import asyncio

        async def amake_request(url, response_callback=None, **kwargs):
            await asyncio.sleep(0.05)
            raise RuntimeError("boom")

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", amake_request
        )
        got = await asyncio.gather(
            *(rate_limiter.fred_get("https://x/m") for _ in range(3)),
            return_exceptions=True,
        )

        assert all(isinstance(g, RuntimeError) for g in got)

    async def test_clearing_memory_leaves_the_disk_tier_answering(self, monkeypatch):
        calls: list = []
        _serve(monkeypatch, [_Response({"ok": True})], calls)

        await rate_limiter.fred_get("https://x/n")
        rate_limiter.cache_clear()

        assert await rate_limiter.fred_get("https://x/n") == {"ok": True}
        assert len(calls) == 1

    async def test_clearing_both_tiers_asks_again(self, monkeypatch):
        from openbb_fred.utils import cache

        calls: list = []
        _serve(monkeypatch, [_Response({"ok": True})], calls)

        await rate_limiter.fred_get("https://x/o")
        rate_limiter.cache_clear()
        cache.clear()
        await rate_limiter.fred_get("https://x/o")

        assert len(calls) == 2

    async def test_a_rate_limit_without_a_retry_after_falls_back_to_backoff(
        self, monkeypatch
    ):
        monkeypatch.setattr(rate_limiter, "DEFAULT_BACKOFF_SECONDS", 0.0)
        calls: list = []
        _serve(monkeypatch, [_Response(status=429), _Response({"ok": True})], calls)

        got = await rate_limiter.fred_get("https://x/p", use_cache=False)

        assert got == {"ok": True}
        assert len(calls) == 2

    async def test_a_payload_that_is_not_an_object_is_handed_back_whole(
        self, monkeypatch
    ):
        _serve(monkeypatch, [_Response([{"error_code": "429"}])])

        got = await rate_limiter.fred_get("https://x/q", use_cache=False)

        assert got == [{"error_code": "429"}]

    async def test_a_request_that_answers_with_nothing_is_not_cached(self, monkeypatch):
        calls: list = []

        async def read(response, session):
            return None

        _serve(monkeypatch, [_Response({"ok": True})], calls)

        assert (
            await rate_limiter.fred_get("https://x/r", response_callback=read) is None
        )
        assert (
            await rate_limiter.fred_get("https://x/r", response_callback=read) is None
        )
        assert len(calls) == 2

    def test_a_request_driven_without_an_event_loop_is_not_shared(self, monkeypatch):
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE", "0")
        _serve(monkeypatch, [_Response({"ok": True})])
        request = rate_limiter.fred_get("https://x/s")

        with pytest.raises(StopIteration) as finished:
            request.send(None)

        assert finished.value.value == {"ok": True}
        assert rate_limiter._inflight == {}


class TestMemoryCache:
    """The in-process tier the transport holds in front of the disk cache."""

    @pytest.fixture(autouse=True)
    def _disk_off(self, monkeypatch):
        """Switch the disk tier off so only the memory tier answers."""
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE", "0")

    async def test_a_lifetime_of_nothing_switches_the_tier_off(self, monkeypatch):
        monkeypatch.setattr(rate_limiter, "CACHE_TTL_SECONDS", 0.0)
        calls: list = []
        _serve(monkeypatch, [_Response({"ok": True})], calls)

        await rate_limiter.fred_get("https://x/ttl-off")
        await rate_limiter.fred_get("https://x/ttl-off")

        assert len(calls) == 2
        assert not rate_limiter._cache

    async def test_a_tier_sized_to_nothing_holds_no_entry(self, monkeypatch):
        monkeypatch.setattr(rate_limiter, "CACHE_MAX_ENTRIES", 0)
        calls: list = []
        _serve(monkeypatch, [_Response({"ok": True})], calls)

        await rate_limiter.fred_get("https://x/size-off")
        await rate_limiter.fred_get("https://x/size-off")

        assert len(calls) == 2
        assert not rate_limiter._cache

    async def test_an_entry_that_has_aged_out_is_asked_for_again(self, monkeypatch):
        clock = _Clock()
        monkeypatch.setattr(rate_limiter, "time", clock)
        monkeypatch.setattr(rate_limiter, "CACHE_TTL_SECONDS", 60.0)
        calls: list = []
        _serve(monkeypatch, [_Response({"ok": True})], calls)

        await rate_limiter.fred_get("https://x/aged")
        await rate_limiter.fred_get("https://x/aged")

        assert len(calls) == 1

        clock.now += 61.0

        assert await rate_limiter.fred_get("https://x/aged") == {"ok": True}
        assert len(calls) == 2

    async def test_the_oldest_entry_is_dropped_when_the_tier_is_full(self, monkeypatch):
        monkeypatch.setattr(rate_limiter, "CACHE_MAX_ENTRIES", 1)
        calls: list = []
        _serve(monkeypatch, [_Response({"ok": True})], calls)

        await rate_limiter.fred_get("https://x/first")
        await rate_limiter.fred_get("https://x/second")
        await rate_limiter.fred_get("https://x/first")

        assert len(calls) == 3
        assert len(rate_limiter._cache) == 1


class TestEnvironmentSettings:
    """The tunables the transport reads out of the environment."""

    def test_a_float_setting_is_read(self, monkeypatch):
        monkeypatch.setenv("OPENBB_FRED_MIN_INTERVAL", "1.5")

        assert rate_limiter._float_env("OPENBB_FRED_MIN_INTERVAL", 0.6) == 1.5

    def test_an_unreadable_float_setting_falls_back(self, monkeypatch):
        monkeypatch.setenv("OPENBB_FRED_MIN_INTERVAL", "soon")

        assert rate_limiter._float_env("OPENBB_FRED_MIN_INTERVAL", 0.6) == 0.6

    def test_a_float_setting_that_is_not_set_falls_back(self, monkeypatch):
        monkeypatch.delenv("OPENBB_FRED_MIN_INTERVAL", raising=False)

        assert rate_limiter._float_env("OPENBB_FRED_MIN_INTERVAL", 0.6) == 0.6

    def test_an_int_setting_is_read(self, monkeypatch):
        monkeypatch.setenv("OPENBB_FRED_MAX_RETRIES", "9")

        assert rate_limiter._int_env("OPENBB_FRED_MAX_RETRIES", 4) == 9

    def test_a_fractional_int_setting_falls_back(self, monkeypatch):
        monkeypatch.setenv("OPENBB_FRED_MAX_RETRIES", "4.5")

        assert rate_limiter._int_env("OPENBB_FRED_MAX_RETRIES", 4) == 4

    def test_an_empty_int_setting_falls_back(self, monkeypatch):
        monkeypatch.setenv("OPENBB_FRED_MAX_RETRIES", "")

        assert rate_limiter._int_env("OPENBB_FRED_MAX_RETRIES", 4) == 4


class TestAcquire:
    """The gap the transport holds between requests."""

    async def test_a_request_waits_for_its_turn(self, monkeypatch):
        """The first request goes straight through, the second waits the gap."""
        clock = _Clock()
        waited: list[float] = []

        async def wound(seconds):
            waited.append(seconds)
            clock.now += seconds

        monkeypatch.setattr(rate_limiter, "time", clock)
        monkeypatch.setattr("asyncio.sleep", wound)
        monkeypatch.setattr(rate_limiter, "MIN_INTERVAL_SECONDS", 0.5)
        monkeypatch.setattr(rate_limiter, "_last_request_at", 0.0)

        await rate_limiter.acquire()

        assert waited == []
        assert rate_limiter._last_request_at == 1000.0

        await rate_limiter.acquire()

        assert waited == [0.5]
        assert rate_limiter._last_request_at == 1000.5
        assert clock.now == 1000.5


class TestFredGetMany:
    """Many requests, in the order asked for."""

    async def test_the_results_line_up_with_the_urls(self, monkeypatch):
        async def amake_request(url, response_callback=None, **kwargs):
            return await response_callback(_Response({"url": url}), None)

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", amake_request
        )
        urls = [f"https://x/many/{i}" for i in range(5)]

        assert [r["url"] for r in await rate_limiter.fred_get_many(urls)] == urls

    async def test_a_failure_is_raised(self, monkeypatch):
        async def amake_request(url, response_callback=None, **kwargs):
            if url.endswith("2"):
                raise RuntimeError("boom")
            return await response_callback(_Response({"url": url}), None)

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", amake_request
        )

        with pytest.raises(RuntimeError, match="boom"):
            await rate_limiter.fred_get_many(
                [f"https://x/raise/{i}" for i in range(4)], use_cache=False
            )

    async def test_a_failure_can_be_returned_in_place(self, monkeypatch):
        async def amake_request(url, response_callback=None, **kwargs):
            if url.endswith("2"):
                raise RuntimeError("boom")
            return await response_callback(_Response({"url": url}), None)

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", amake_request
        )
        got = await rate_limiter.fred_get_many(
            [f"https://x/keep/{i}" for i in range(4)],
            return_exceptions=True,
            use_cache=False,
        )

        assert len(got) == 4
        assert isinstance(got[2], RuntimeError)

    async def test_nothing_asked_for_reads_nothing(self):
        assert await rate_limiter.fred_get_many([]) == []
