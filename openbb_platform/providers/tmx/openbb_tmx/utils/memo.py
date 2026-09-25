"""A disk-backed result cache for the work that is costly to repeat."""

from collections.abc import Callable
from functools import wraps
from typing import Any


def _name(func: Any) -> str:
    """Return the fully qualified name a function caches under."""
    return f"{func.__module__}.{func.__qualname__}"


CACHE_NAME = "tmx_results"

CACHE_DIR_ENV = "OPENBB_TMX_RESULT_CACHE"


def cache_directory() -> str:
    """Return the directory the result cache is kept in.

    Returns
    -------
    str
        The directory path.
    """
    import os

    from openbb_core.app.utils import get_user_cache_directory

    return os.environ.get(CACHE_DIR_ENV) or f"{get_user_cache_directory()}/{CACHE_NAME}"


def _cache():
    """Open the shared on-disk result cache."""
    from diskcache import Cache

    return Cache(cache_directory())


def _key(func: Callable, args: tuple, kwargs: dict) -> str:
    """Build the key one call is stored under."""
    parts = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in sorted(kwargs.items())]

    return f"{_name(func)}({','.join(parts)})"


def memoize(ttl: float | None = None) -> Callable:
    """Hold an async function's result on disk.

    Parameters
    ----------
    ttl : float or None
        Seconds a result stays usable, or None to keep it until it is cleared.

    Returns
    -------
    Callable
        The decorator.
    """

    def decorate(func: Callable) -> Callable:
        prefix = f"{_name(func)}("

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            import asyncio

            key = _key(func, args, kwargs)

            def read() -> Any:
                with _cache() as cache:
                    return cache.get(key, default=_MISSING)

            stored = await asyncio.to_thread(read)

            if stored is not _MISSING:
                return stored

            value = await func(*args, **kwargs)

            def write() -> None:
                with _cache() as cache:
                    cache.set(key, value, expire=ttl)

            await asyncio.to_thread(write)

            return value

        def cache_clear() -> None:
            """Forget every result this function stored."""
            with _cache() as cache:
                for key in list(cache.iterkeys()):
                    if str(key).startswith(prefix):
                        cache.pop(key, default=None)

        wrapper.cache_clear = cache_clear  # ty: ignore[unresolved-attribute]

        return wrapper

    return decorate


class _Missing:
    """The sentinel returned when a key is absent."""


_MISSING = _Missing()
