"""Tests for the pooled Deribit HTTP sessions."""

import asyncio

import pytest

from openbb_deribit.utils import session as sessions

pytestmark = pytest.mark.uses_session


@pytest.fixture(autouse=True)
def _empty_pools():
    """Start and finish each test with empty pools."""
    sessions._SESSIONS.clear()
    sessions._CACHED_SESSIONS.clear()
    yield
    sessions._SESSIONS.clear()
    sessions._CACHED_SESSIONS.clear()


class TestGetSession:
    """One uncached session is held per running loop."""

    @pytest.mark.asyncio
    async def test_shared_within_a_loop(self):
        """Two callers on one loop share a session."""
        first = await sessions.get_session()
        second = await sessions.get_session()

        try:
            assert first is second
            assert len(sessions._SESSIONS) == 1
        finally:
            await sessions.close_sessions()

    @pytest.mark.asyncio
    async def test_rebuilt_when_closed(self):
        """A session someone closed is replaced rather than reused."""
        first = await sessions.get_session()
        await first.close()
        second = await sessions.get_session()

        try:
            assert first is not second
        finally:
            await sessions.close_sessions()


class TestGetCachedSession:
    """One cache-backed session is held per running loop, swept once."""

    @pytest.mark.asyncio
    async def test_shared_and_swept_once(self, monkeypatch, tmp_path):
        """The cache is swept the first time a session is built."""
        monkeypatch.setattr(
            "openbb_deribit.utils.cache.cache_path", lambda: str(tmp_path / "deribit")
        )
        swept: list = []

        async def _sweep(backend):
            swept.append(backend)

        monkeypatch.setattr("openbb_deribit.utils.cache.sweep_cache", _sweep)
        first = await sessions.get_cached_session()
        second = await sessions.get_cached_session()

        try:
            assert first is second
            assert len(swept) == 1
        finally:
            await sessions.close_sessions()

    @pytest.mark.asyncio
    async def test_a_failing_sweep_does_not_break_the_session(
        self, monkeypatch, tmp_path
    ):
        """A sweep that raises leaves a usable session behind."""
        monkeypatch.setattr(
            "openbb_deribit.utils.cache.cache_path", lambda: str(tmp_path / "deribit")
        )

        async def _sweep(backend):
            raise RuntimeError("disk is gone")

        monkeypatch.setattr("openbb_deribit.utils.cache.sweep_cache", _sweep)
        session = await sessions.get_cached_session()

        try:
            assert session.closed is False
        finally:
            await sessions.close_sessions()


class TestCloseSessions:
    """Closing empties the pools and closes what was open."""

    @pytest.mark.asyncio
    async def test_closes_everything(self, monkeypatch, tmp_path):
        """Both pools are emptied and both sessions closed."""
        monkeypatch.setattr(
            "openbb_deribit.utils.cache.cache_path", lambda: str(tmp_path / "deribit")
        )

        async def _sweep(backend):
            return None

        monkeypatch.setattr("openbb_deribit.utils.cache.sweep_cache", _sweep)
        plain = await sessions.get_session()
        cached = await sessions.get_cached_session()
        await sessions.close_sessions()

        assert plain.closed is True
        assert cached.closed is True
        assert not sessions._SESSIONS
        assert not sessions._CACHED_SESSIONS

    @pytest.mark.asyncio
    async def test_closes_only_the_named_loop(self):
        """Closing one loop leaves another loop's session alone."""
        mine = await sessions.get_session()
        sessions._SESSIONS["other"] = object()
        await sessions.close_sessions(asyncio.get_running_loop())

        try:
            assert mine.closed is True
            assert "other" in sessions._SESSIONS
        finally:
            sessions._SESSIONS.clear()

    @pytest.mark.asyncio
    async def test_tolerates_a_session_that_will_not_close(self):
        """A session whose close raises does not stop the rest."""

        class _Stubborn:
            closed = False

            async def close(self):
                raise RuntimeError("no")

        sessions._SESSIONS["stubborn"] = _Stubborn()
        await sessions.close_sessions()

        assert not sessions._SESSIONS

    @pytest.mark.asyncio
    async def test_empty_pools(self):
        """Closing empty pools does nothing at all."""
        await sessions.close_sessions()

        assert not sessions._SESSIONS


class TestLoopHook:
    """A loop closes its own sessions when it shuts down."""

    def test_hooks_once(self):
        """A loop is hooked the first time and left alone after."""
        loop = asyncio.new_event_loop()

        try:
            original = loop.close
            sessions._hook_loop_close(loop)
            hooked = loop.close
            sessions._hook_loop_close(loop)

            assert hooked is not original
            assert loop.close is hooked
        finally:
            loop.close()

    def test_closes_the_pool_on_shutdown(self):
        """The sessions a loop opened are closed when the loop is."""
        loop = asyncio.new_event_loop()
        session = loop.run_until_complete(_open(loop))

        assert session.closed is False

        loop.close()

        assert session.closed is True
        assert not sessions._SESSIONS

    def test_tolerates_a_pool_that_will_not_close_on_shutdown(self, monkeypatch):
        """A loop whose pool cannot be drained still closes."""

        async def _close(loop=None):
            raise RuntimeError("the pool is wedged")

        monkeypatch.setattr(sessions, "close_sessions", _close)
        loop = asyncio.new_event_loop()
        sessions._hook_loop_close(loop)
        loop.close()

        assert loop.is_closed()

    def test_tolerates_a_loop_that_rejects_the_hook(self):
        """A loop whose close cannot be replaced is left to the caller."""

        class _Frozen:
            __slots__ = ()

            def close(self):
                return None

        sessions._hook_loop_close(_Frozen())


async def _open(loop):
    """Open one pooled session on the given loop."""
    return await sessions.get_session()
