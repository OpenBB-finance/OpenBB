"""Tests for the shared curl_cffi session helper."""

import asyncio

import pytest

from openbb_government_us.utils import curl_session


class _FakeSession:
    """Stand-in for a curl_cffi AsyncSession."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.requested: list[str] = []
        self.closed = False

    async def get(self, url):
        self.requested.append(url)
        return url

    async def close(self):
        self.closed = True


@pytest.fixture(autouse=True)
def _clear_sessions(monkeypatch):
    """Isolate the module-level session cache and stub the real session class."""
    created: list[_FakeSession] = []

    def _factory(**kwargs):
        session = _FakeSession(**kwargs)
        created.append(session)
        return session

    monkeypatch.setattr("curl_cffi.requests.AsyncSession", _factory)
    curl_session._SESSIONS.clear()
    yield created
    curl_session._SESSIONS.clear()


class TestGetSession:
    """Tests for session creation and caching."""

    def test_impersonates_chrome(self, _clear_sessions):
        """The session impersonates Chrome to satisfy the WAF."""
        session = asyncio.run(curl_session.get_session("host"))
        assert session.kwargs == {"impersonate": "chrome"}

    def test_caches_by_key(self, _clear_sessions):
        """Repeat calls with the same key reuse one session."""
        first = asyncio.run(curl_session.get_session("host"))
        second = asyncio.run(curl_session.get_session("host"))
        assert first is second
        assert len(_clear_sessions) == 1

    def test_distinct_keys_get_distinct_sessions(self, _clear_sessions):
        """Different keys create independent sessions."""
        first = asyncio.run(curl_session.get_session("a"))
        second = asyncio.run(curl_session.get_session("b"))
        assert first is not second
        assert len(_clear_sessions) == 2

    def test_warmup_primes_the_session_once(self, _clear_sessions):
        """The warmup URL is requested only when the session is created."""
        asyncio.run(curl_session.get_session("host", warmup="https://example.gov"))
        asyncio.run(curl_session.get_session("host", warmup="https://example.gov"))
        assert _clear_sessions[0].requested == ["https://example.gov"]

    def test_without_warmup_no_request_is_made(self, _clear_sessions):
        """Omitting warmup creates the session without any request."""
        asyncio.run(curl_session.get_session("host"))
        assert _clear_sessions[0].requested == []


class TestCloseSessions:
    """Tests for session teardown."""

    def test_closes_and_clears_every_session(self, _clear_sessions):
        """Every cached session is closed and the cache emptied."""
        asyncio.run(curl_session.get_session("a"))
        asyncio.run(curl_session.get_session("b"))
        asyncio.run(curl_session.close_sessions())
        assert all(session.closed for session in _clear_sessions)
        assert curl_session._SESSIONS == {}

    def test_close_with_no_sessions_is_a_no_op(self):
        """Closing an empty cache does nothing."""
        asyncio.run(curl_session.close_sessions())
        assert curl_session._SESSIONS == {}
