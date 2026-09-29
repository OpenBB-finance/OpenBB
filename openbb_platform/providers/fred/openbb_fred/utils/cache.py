"""On-disk response cache for the FRED API."""

import os
import re
from typing import Any

ROOT_URL = "https://api.stlouisfed.org"

HOUR = 60 * 60
DAY = 24 * HOUR

DEFAULT_TTL = HOUR

TTL_BY_PATH = {
    "/fred/series/observations": 4 * HOUR,
    "/fred/series/search": DAY,
    "/fred/series/updates": HOUR,
    "/fred/series": DAY,
    "/fred/release/tables": 6 * HOUR,
    "/fred/release/series": DAY,
    "/fred/releases": DAY,
    "/fred/category": 7 * DAY,
    "/geofred/series/group": 7 * DAY,
    "/geofred/series/data": DAY,
    "/geofred/regional/data": DAY,
}

_API_KEY_RE = re.compile(r"([?&])api_key=[^&]*")

_cache = None
_cache_directory = ""

DEFAULT_SIZE_LIMIT = 512 * 1024 * 1024


def _float_env(name: str, default: float) -> float:
    """Read a float from the environment, falling back to a default."""
    raw = os.environ.get(name)

    if not raw:
        return default

    try:
        return float(raw)
    except ValueError:
        return default


def enabled() -> bool:
    """Return whether responses are cached on disk.

    Returns
    -------
    bool
        False when ``OPENBB_FRED_DISK_CACHE`` switches the cache off.
    """
    return os.environ.get("OPENBB_FRED_DISK_CACHE", "1") not in ("0", "false", "False")


def size_limit() -> int:
    """Return the size the cache is held to, in bytes.

    Returns
    -------
    int
        The limit, from ``OPENBB_FRED_DISK_CACHE_SIZE``.
    """
    return int(_float_env("OPENBB_FRED_DISK_CACHE_SIZE", DEFAULT_SIZE_LIMIT))


def ttl_multiplier() -> float:
    """Return the factor every cache lifetime is scaled by.

    Returns
    -------
    float
        The multiplier, from ``OPENBB_FRED_DISK_TTL_MULTIPLIER``.
    """
    return _float_env("OPENBB_FRED_DISK_TTL_MULTIPLIER", 1.0)


def cache_directory() -> str:
    """Return the directory the cache is held in.

    Returns
    -------
    str
        The directory, from ``OPENBB_FRED_DISK_CACHE_DIR`` when it is set.
    """
    from openbb_core.app.utils import get_user_cache_directory

    return (
        os.environ.get("OPENBB_FRED_DISK_CACHE_DIR")
        or f"{get_user_cache_directory()}/fred"
    )


def redact(url: str) -> str:
    """Return a URL with the API key replaced.

    Parameters
    ----------
    url : str
        The request URL.

    Returns
    -------
    str
        The URL with any ``api_key`` value redacted.
    """
    return _API_KEY_RE.sub(r"\1api_key=__redacted__", url)


def ttl_for(url: str) -> float:
    """Return the cache lifetime for a FRED URL.

    Parameters
    ----------
    url : str
        The request URL.

    Returns
    -------
    float
        The time to live, in seconds.
    """
    path = url.split("?", 1)[0].replace(ROOT_URL, "")
    matches = [p for p in TTL_BY_PATH if path.startswith(p)]
    ttl = TTL_BY_PATH[max(matches, key=len)] if matches else DEFAULT_TTL

    return ttl * ttl_multiplier()


def get_disk_cache():
    """Return the process-wide on-disk cache.

    Returns
    -------
    Cache or None
        The cache, or None when disk caching is switched off. The cache is
        rebuilt when the configured directory changes.
    """
    global _cache, _cache_directory  # noqa: PLW0603

    if not enabled():
        return None

    directory = cache_directory()

    if _cache is None or _cache_directory != directory:
        from diskcache import Cache

        close()
        _cache = Cache(directory=directory, size_limit=size_limit())
        _cache_directory = directory

    return _cache


async def disk_get(url: str) -> Any:
    """Read a cached payload for a URL.

    Parameters
    ----------
    url : str
        The request URL.

    Returns
    -------
    Any
        The cached payload, or None when absent or expired.
    """
    import asyncio

    cache = get_disk_cache()

    if cache is None:
        return None

    return await asyncio.to_thread(cache.get, redact(url))


async def disk_set(url: str, value: Any) -> None:
    """Write a payload to the cache under its endpoint's lifetime.

    Parameters
    ----------
    url : str
        The request URL.
    value : Any
        The payload to store.
    """
    import asyncio

    cache = get_disk_cache()

    if cache is None:
        return

    await asyncio.to_thread(cache.set, redact(url), value, expire=ttl_for(url))


def clear() -> None:
    """Empty the on-disk cache."""
    cache = get_disk_cache()

    if cache is not None:
        cache.clear()


def close() -> None:
    """Release the on-disk cache, so the next read opens it again."""
    global _cache, _cache_directory  # noqa: PLW0603

    if _cache is not None:
        _cache.close()

    _cache = None
    _cache_directory = ""


def stats() -> dict:
    """Return the cache's size and item count.

    Returns
    -------
    dict
        Whether caching is on, and the directory, item count, and volume in
        bytes when it is.
    """
    cache = get_disk_cache()

    if cache is None:
        return {"enabled": False, "items": 0, "bytes": 0}

    return {
        "enabled": True,
        "directory": cache.directory,
        "items": len(cache),
        "bytes": cache.volume(),
    }
