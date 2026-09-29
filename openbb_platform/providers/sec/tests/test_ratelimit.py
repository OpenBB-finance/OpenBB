"""Unit tests for the SEC EDGAR process-wide rate limiter."""

from openbb_sec.utils import ratelimit


def test_default_when_unset(monkeypatch):
    """An unset env var yields the default rate."""
    monkeypatch.delenv(ratelimit.REQUESTS_PER_SECOND_ENV_VAR, raising=False)
    assert ratelimit._requests_per_second() == ratelimit._DEFAULT_REQUESTS_PER_SECOND


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
