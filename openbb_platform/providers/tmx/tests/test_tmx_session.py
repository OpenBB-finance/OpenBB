"""Tests for the pooled TMX sessions."""

import asyncio

import pytest

from openbb_tmx.utils import session as session_utils


@pytest.fixture(autouse=True)
def _empty_pool():
    """Start and finish each test with an empty pool."""
    session_utils._SESSIONS.clear()
    session_utils._CACHED_SESSIONS.clear()
    session_utils._JARS.clear()

    yield

    asyncio.run(session_utils.close_sessions())


class TestPooling:
    """The pool hands the same session to every caller on a loop."""

    @pytest.mark.asyncio
    async def test_the_uncached_session_is_reused(self):
        first = await session_utils.get_session()
        second = await session_utils.get_session()

        assert first is second
        assert len(session_utils._SESSIONS) == 1

    @pytest.mark.asyncio
    async def test_the_cached_session_is_reused(self):
        first = await session_utils.get_cached_session()
        second = await session_utils.get_cached_session()

        assert first is second
        assert len(session_utils._CACHED_SESSIONS) == 1

    @pytest.mark.asyncio
    async def test_both_sessions_share_one_cookie_jar(self):
        plain = await session_utils.get_session()
        cached = await session_utils.get_cached_session()

        assert plain.cookie_jar is cached.cookie_jar
        assert len(session_utils._JARS) == 1

    @pytest.mark.asyncio
    async def test_a_closed_session_is_replaced(self):
        first = await session_utils.get_session()
        await first.close()
        second = await session_utils.get_session()

        assert second is not first
        assert not second.closed

    @pytest.mark.asyncio
    async def test_a_closed_cached_session_is_replaced(self):
        first = await session_utils.get_cached_session()
        await first.close()
        second = await session_utils.get_cached_session()

        assert second is not first
        assert not second.closed

    def test_each_loop_gets_its_own_session(self):
        async def _grab():
            return await session_utils.get_session()

        first = asyncio.run(_grab())
        second = asyncio.run(_grab())

        assert first is not second
        assert first.closed
        assert second.closed


class TestLifetime:
    """Sessions close with the loop that owns them."""

    def test_closing_the_loop_empties_the_pool(self):
        async def _open():
            await session_utils.get_session()
            await session_utils.get_cached_session()

        asyncio.run(_open())

        assert not session_utils._SESSIONS
        assert not session_utils._CACHED_SESSIONS
        assert not session_utils._JARS

    def test_the_loop_still_closes_when_the_pool_raises(self, monkeypatch):
        async def _boom(loop=None):
            raise RuntimeError("no")

        monkeypatch.setattr(session_utils, "close_sessions", _boom)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(session_utils.get_session())
        loop.close()

        assert loop.is_closed()

    def test_a_loop_is_hooked_only_once(self):
        loop = asyncio.new_event_loop()
        session_utils._hook_loop_close(loop)
        hooked = loop.close
        session_utils._hook_loop_close(loop)

        assert loop.close is hooked

        loop.close()

    def test_a_loop_that_rejects_the_hook_is_left_alone(self):
        class Frozen:
            """A loop whose attributes cannot be set, as uvloop's cannot."""

            def close(self):
                """Close nothing."""

            def __setattr__(self, name, value):
                raise AttributeError(name)

        loop = Frozen()
        session_utils._hook_loop_close(loop)

        assert not hasattr(loop, "_tmx_close_hooked")

    @pytest.mark.asyncio
    async def test_closing_one_loop_leaves_the_others(self):
        await session_utils.get_session()
        other = object()
        session_utils._SESSIONS[other] = None

        await session_utils.close_sessions(asyncio.get_running_loop())

        assert list(session_utils._SESSIONS) == [other]

        session_utils._SESSIONS.pop(other)

    @pytest.mark.asyncio
    async def test_a_session_that_fails_to_close_is_still_dropped(self):
        class Stubborn:
            """A session whose close always raises."""

            closed = False

            async def close(self):
                """Refuse to close."""
                raise RuntimeError("no")

        session_utils._SESSIONS[object()] = Stubborn()
        await session_utils.close_sessions()

        assert not session_utils._SESSIONS


class TestPrime:
    """Priming warms the session and reports whether the host answered."""

    @pytest.mark.asyncio
    async def test_a_good_response_is_reported(self, monkeypatch):
        class Response:
            status = 200

            def release(self):
                """Release nothing."""

        class Session:
            async def get(self, url, **kwargs):
                """Answer every request."""
                return Response()

        async def _session():
            return Session()

        monkeypatch.setattr(session_utils, "get_session", _session)

        assert await session_utils.prime() is True

    @pytest.mark.asyncio
    async def test_a_bad_status_is_reported(self, monkeypatch):
        class Response:
            status = 503

            def release(self):
                """Release nothing."""

        class Session:
            async def get(self, url, **kwargs):
                """Answer every request badly."""
                return Response()

        async def _session():
            return Session()

        monkeypatch.setattr(session_utils, "get_session", _session)

        assert await session_utils.prime() is False

    @pytest.mark.asyncio
    async def test_a_failed_request_is_reported(self, monkeypatch):
        class Session:
            async def get(self, url, **kwargs):
                """Fail every request."""
                raise ConnectionError("down")

        async def _session():
            return Session()

        monkeypatch.setattr(session_utils, "get_session", _session)

        assert await session_utils.prime() is False
