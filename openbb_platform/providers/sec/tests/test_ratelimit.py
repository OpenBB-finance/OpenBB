"""Unit tests for the SEC EDGAR process-wide rate limiter."""

import asyncio

from openbb_sec.utils import ratelimit


def test_default_when_unset(monkeypatch):
    """An unset env var yields the default rate."""
    monkeypatch.delenv(ratelimit.REQUESTS_PER_SECOND_ENV_VAR, raising=False)
    assert ratelimit._requests_per_second() == 7.5


def test_valid_override(monkeypatch):
    """A positive numeric override is honored."""
    monkeypatch.setenv(ratelimit.REQUESTS_PER_SECOND_ENV_VAR, "4.5")
    assert ratelimit._requests_per_second() == 4.5


def test_invalid_value_falls_back(monkeypatch):
    """A non-numeric override falls back to the default."""
    monkeypatch.setenv(ratelimit.REQUESTS_PER_SECOND_ENV_VAR, "fast")
    assert ratelimit._requests_per_second() == ratelimit._DEFAULT_REQUESTS_PER_SECOND


def test_non_positive_falls_back(monkeypatch):
    """A zero or negative override falls back to the default."""
    monkeypatch.setenv(ratelimit.REQUESTS_PER_SECOND_ENV_VAR, "0")
    assert ratelimit._requests_per_second() == ratelimit._DEFAULT_REQUESTS_PER_SECOND


def test_sec_amake_request_retries_timeouts(monkeypatch):
    """A transient timeout is retried through the SEC request helper."""
    attempts = 0
    delays = []

    async def _rate_limit():
        return None

    async def _amake_request(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise asyncio.TimeoutError
        return {"ok": True}

    async def _sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(ratelimit, "sec_rate_limit", _rate_limit)
    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.amake_request",
        _amake_request,
    )
    monkeypatch.setattr(ratelimit.asyncio, "sleep", _sleep)

    assert asyncio.run(ratelimit.sec_amake_request("https://sec.gov/example")) == {
        "ok": True
    }
    assert attempts == 3
    assert delays == [1, 2]
