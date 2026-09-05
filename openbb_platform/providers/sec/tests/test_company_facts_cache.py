"""Tests for SEC company-facts HTTP caching."""

import pytest
from openbb_sec.utils import company_facts


@pytest.mark.asyncio
async def test_company_facts_uses_persistent_sqlite_cache(monkeypatch, tmp_path):
    """Repeated calls should target the same persistent six-hour cache."""
    import aiohttp_client_cache
    import aiohttp_client_cache.session as cache_session
    import openbb_core.app.utils as app_utils
    import openbb_core.provider.utils.helpers as request_helpers

    backends = []
    sessions = []

    class FakeBackend:
        def __init__(self, cache_name, expire_after=None):
            self.cache_name = cache_name
            self.expire_after = expire_after
            backends.append(self)

    class FakeCachedSession:
        def __init__(self, *, cache=None, expire_after=None):
            self.cache = cache
            self.expire_after = expire_after
            self.deleted_expired = False
            self.closed = False
            sessions.append(self)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def delete_expired_responses(self):
            self.deleted_expired = True

        async def close(self):
            self.closed = True

    async def fake_amake_request(url, **kwargs):
        assert url.endswith("CIK0000000123.json")
        assert kwargs["session"] in sessions
        return {"entityName": "Test Company", "cik": 123, "facts": {}}

    monkeypatch.setattr(aiohttp_client_cache, "SQLiteBackend", FakeBackend)
    monkeypatch.setattr(cache_session, "CachedSession", FakeCachedSession)
    monkeypatch.setattr(app_utils, "get_user_cache_directory", lambda: tmp_path)
    monkeypatch.setattr(request_helpers, "amake_request", fake_amake_request)
    monkeypatch.setattr(
        company_facts,
        "resolve_company_facts",
        lambda facts_json, **kwargs: facts_json,
    )

    await company_facts.get_standardized_financials(cik=123, use_cache=True)
    await company_facts.get_standardized_financials(cik=123, use_cache=True)

    expected_cache = f"{tmp_path}/http/sec_company_facts"
    assert len(backends) == 2
    assert [backend.cache_name for backend in backends] == [
        expected_cache,
        expected_cache,
    ]
    assert all(backend.expire_after == 3600 * 6 for backend in backends)
    assert all(session.cache in backends for session in sessions)
    assert all(session.deleted_expired for session in sessions)
    assert all(session.closed for session in sessions)
