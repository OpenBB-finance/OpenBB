"""Pooled HTTP sessions for the Deribit API.

One session is held per event loop so connections are kept alive across the
many parallel calls a chain or curve needs. The session is closed when its loop
shuts down, so nothing is left open once the work that opened it is done.
"""

from contextlib import suppress
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from aiohttp_client_cache.session import CachedSession

_SESSIONS: dict = {}
_CACHED_SESSIONS: dict = {}


def _hook_loop_close(loop) -> None:
    """Close this loop's sessions when the loop itself is closed.

    The Python interface runs every command in its own short-lived loop, so the
    pool is emptied there without waiting for an API shutdown that never comes.
    Loops that do not accept the hook, such as uvloop's, are left to the
    shutdown handler.
    """
    if getattr(loop, "_deribit_close_hooked", False):
        return

    original = loop.close

    def close() -> None:
        try:
            if not loop.is_closed() and not loop.is_running():
                loop.run_until_complete(close_sessions(loop))
        except Exception:  # noqa: BLE001, S110
            pass

        original()

    try:
        loop.close = close
        loop._deribit_close_hooked = True
    except (AttributeError, TypeError):
        pass


async def get_session() -> "ClientSession":
    """Return the uncached session for the running loop.

    Returns
    -------
    ClientSession
        A session shared by every caller on this loop.
    """
    import asyncio

    from aiohttp import ClientSession

    loop = asyncio.get_running_loop()
    session = _SESSIONS.get(loop)

    if session is None or session.closed:
        session = ClientSession()
        _SESSIONS[loop] = session
        _hook_loop_close(loop)

    return session


async def get_cached_session() -> "CachedSession":
    """Return the cache-backed session for the running loop.

    Returns
    -------
    CachedSession
        A cache-backed session shared by every caller on this loop.
    """
    import asyncio

    from aiohttp_client_cache.session import CachedSession

    from openbb_deribit.utils.cache import get_cache_backend, sweep_cache

    loop = asyncio.get_running_loop()
    session = _CACHED_SESSIONS.get(loop)

    if session is None or session.closed:
        backend = get_cache_backend()
        session = CachedSession(cache=backend)
        _CACHED_SESSIONS[loop] = session
        _hook_loop_close(loop)

        with suppress(Exception):
            await sweep_cache(backend)

    return session


async def close_sessions(loop=None) -> None:
    """Close pooled sessions and forget the loops that owned them.

    Parameters
    ----------
    loop : AbstractEventLoop or None
        Close only this loop's sessions, or every pooled session when None.
    """
    for pool in (_SESSIONS, _CACHED_SESSIONS):
        keys = [loop] if loop is not None else list(pool)

        for key in keys:
            session = pool.pop(key, None)

            if session is not None and not getattr(session, "closed", True):
                with suppress(Exception):
                    await session.close()
