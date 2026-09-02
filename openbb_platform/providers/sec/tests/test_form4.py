"""Tests for SEC Form 4 download helpers."""

import asyncio

from openbb_sec.utils import form4


def test_download_data_reuses_one_session(monkeypatch):
    """Reuse one HTTP session across every URL in a download batch."""
    created_sessions = []
    request_sessions = []

    class FakeSession:
        def __init__(self):
            self.close_calls = 0

        async def close(self):
            self.close_calls += 1

    async def get_session(**_kwargs):
        session = FakeSession()
        created_sessions.append(session)
        return session

    async def make_request(url, **kwargs):
        request_sessions.append((url, kwargs.get("session")))
        return b"<ownershipDocument />"

    async def parse_data(_data):
        return []

    async def no_sleep(_delay):
        return None

    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.get_async_requests_session", get_session
    )
    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.amake_request", make_request
    )
    monkeypatch.setattr(asyncio, "sleep", no_sleep)
    monkeypatch.setattr(form4, "parse_form_4_data", parse_data)

    result = asyncio.run(
        form4.download_data(
            ["https://example.com/one.xml", "https://example.com/two.xml"],
            use_cache=False,
        )
    )

    assert result == []
    assert len(created_sessions) == 1
    assert request_sessions == [
        ("https://example.com/one.xml", created_sessions[0]),
        ("https://example.com/two.xml", created_sessions[0]),
    ]
    assert created_sessions[0].close_calls == 1
