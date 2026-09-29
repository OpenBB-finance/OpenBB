"""Tests for the shared process-cached ``curl_cffi`` session helper."""

import sys
import types

import pytest

from openbb_federal_reserve.utils import curl_session


class _FakeSession:
    """Records the impersonate kwarg passed to the session factory."""

    def __init__(self, impersonate=None):
        self.impersonate = impersonate


@pytest.fixture(autouse=True)
def _patch_factory(monkeypatch):
    """Replace ``curl_cffi.requests.Session`` with a fake and clear the cache."""
    created: list[_FakeSession] = []

    def factory(impersonate=None):
        session = _FakeSession(impersonate=impersonate)
        created.append(session)
        return session

    fake_requests = types.SimpleNamespace(Session=factory)
    fake_curl_cffi = types.SimpleNamespace(requests=fake_requests)
    monkeypatch.setitem(sys.modules, "curl_cffi", fake_curl_cffi)
    monkeypatch.setitem(sys.modules, "curl_cffi.requests", fake_requests)
    monkeypatch.setattr(curl_session, "_sessions", {})
    yield created


class TestCurlSession:
    """Tests for ``get_session`` and ``reset_session``."""

    def test_first_call_creates_and_warms_once(self, _patch_factory):
        """First call builds a chrome session and runs the warmup exactly once."""
        warmed: list[object] = []
        session = curl_session.get_session("k", warmup=warmed.append)
        assert isinstance(session, _FakeSession)
        assert session.impersonate == "chrome"
        assert warmed == [session]
        assert len(_patch_factory) == 1

    def test_second_call_returns_cached_without_rewarming(self, _patch_factory):
        """A repeat call returns the same object and does not re-warm or rebuild."""
        calls: list[object] = []
        first = curl_session.get_session("k", warmup=calls.append)
        second = curl_session.get_session("k", warmup=calls.append)
        assert first is second
        assert calls == [first]
        assert len(_patch_factory) == 1

    def test_distinct_keys_get_distinct_sessions(self, _patch_factory):
        """Different keys are cached independently."""
        a = curl_session.get_session("a")
        b = curl_session.get_session("b")
        assert a is not b
        assert len(_patch_factory) == 2

    def test_warmup_none_skips_warmup(self, _patch_factory):
        """Passing no warmup callable still creates and caches a session."""
        session = curl_session.get_session("k")
        assert isinstance(session, _FakeSession)
        assert curl_session.get_session("k") is session
        assert len(_patch_factory) == 1

    def test_reset_session_rebuilds_and_rewarms(self, _patch_factory):
        """After reset the next call recreates the session and re-runs warmup."""
        warmed: list[object] = []
        first = curl_session.get_session("k", warmup=warmed.append)
        curl_session.reset_session("k")
        second = curl_session.get_session("k", warmup=warmed.append)
        assert first is not second
        assert warmed == [first, second]
        assert len(_patch_factory) == 2

    def test_reset_unknown_key_is_noop(self, _patch_factory):
        """Resetting a key that was never cached does not raise."""
        curl_session.reset_session("missing")
        assert _patch_factory == []
