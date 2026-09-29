"""Pooled HTTP sessions for the TMX hosts."""

from contextlib import suppress
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from aiohttp_client_cache.session import CachedSession

_SESSIONS: dict = {}
_CACHED_SESSIONS: dict = {}
_JARS: dict = {}


def _cookie_jar(loop):
    """Return the cookie jar shared by both of a loop's sessions."""
    from aiohttp import CookieJar

    jar = _JARS.get(loop)

    if jar is None:
        jar = CookieJar(unsafe=True)
        _JARS[loop] = jar

    return jar


def _hook_loop_close(loop) -> None:
    """Close this loop's sessions when the loop itself is closed."""
    if getattr(loop, "_tmx_close_hooked", False):
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
        loop._tmx_close_hooked = True
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
        session = ClientSession(cookie_jar=_cookie_jar(loop))
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

    from openbb_tmx.utils.cache import get_cache_backend, sweep_cache

    loop = asyncio.get_running_loop()
    session = _CACHED_SESSIONS.get(loop)

    if session is None or session.closed:
        backend = get_cache_backend()
        session = CachedSession(cache=backend, cookie_jar=_cookie_jar(loop))
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
    for pool in (_SESSIONS, _CACHED_SESSIONS, _JARS):
        keys = [loop] if loop is not None else list(pool)

        for key in keys:
            session = pool.pop(key, None)

            if session is not None and not getattr(session, "closed", True):
                with suppress(Exception):
                    await session.close()


async def prime(url: str = "https://money.tmx.com/", **kwargs) -> bool:
    """Warm the session against a host, collecting any cookie it sets.

    Parameters
    ----------
    url : str
        The URL to request.

    Returns
    -------
    bool
        Whether the request succeeded.
    """
    from openbb_tmx.utils.cache import get_headers

    session = await get_session()

    try:
        response = await session.get(url, headers=get_headers("text"), **kwargs)
        response.release()

        return response.status == 200
    except Exception:  # noqa: BLE001
        return False
