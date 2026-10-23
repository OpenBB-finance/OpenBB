"""Unified disk cache for the SEC provider."""

import asyncio
import contextlib
import os
import threading
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from diskcache import FanoutCache

SIZE_LIMIT_ENV_VAR = "OPENBB_SEC_CACHE_SIZE_LIMIT"

CACHE_DIR_ENV_VAR = "OPENBB_SEC_CACHE_DIR"

DEFAULT_SIZE_LIMIT = 8 * 1024**3

_CACHE_SHARDS = 8

_CACHE_TIMEOUT = 1.0

_cache: "FanoutCache | None" = None
_cache_lock = threading.Lock()


def _parse_size(value: "str | int | None") -> int:
    """Parse a size limit given as bytes or a ``"<number><unit>"`` string."""
    if value is None or value == "":
        return DEFAULT_SIZE_LIMIT
    if isinstance(value, int):
        return value if value > 0 else DEFAULT_SIZE_LIMIT
    text = str(value).strip().upper().replace(" ", "")
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
    for suffix, factor in sorted(units.items(), key=lambda item: -len(item[0])):
        if text.endswith(suffix):
            try:
                return max(int(float(text[: -len(suffix)]) * factor), 1)
            except ValueError:
                return DEFAULT_SIZE_LIMIT
    try:
        return max(int(float(text)), 1)
    except ValueError:
        return DEFAULT_SIZE_LIMIT


def get_size_limit() -> int:
    """Return the configured cache size limit, in bytes."""
    return _parse_size(os.environ.get(SIZE_LIMIT_ENV_VAR))


def get_cache_directory() -> str:
    """Return the root directory of the unified SEC cache."""
    override = os.environ.get(CACHE_DIR_ENV_VAR)
    if override:
        return os.path.abspath(os.path.expanduser(override))

    from openbb_core.app.utils import get_user_cache_directory

    return os.path.join(get_user_cache_directory(), "sec")


def get_cache() -> "FanoutCache":
    """Return the process-wide SEC cache, creating it on first use."""
    global _cache  # noqa: PLW0603
    if _cache is None:
        with _cache_lock:
            if _cache is None:
                from diskcache import FanoutCache

                _cache = FanoutCache(
                    directory=get_cache_directory(),
                    shards=_CACHE_SHARDS,
                    timeout=_CACHE_TIMEOUT,
                    size_limit=get_size_limit(),
                    eviction_policy="least-recently-used",
                )
    return _cache


def _make_key(url: str, method: str = "GET", suffix: str = "") -> str:
    """Build a stable cache key for a request."""
    return f"{method.upper()} {url}{suffix}"


def _is_empty(value: Any) -> bool:
    """Return True for responses not worth caching."""
    return value is None or value in ({}, [])


def _cache_set(key: str, value: Any, expire: "float | None") -> None:
    """Write a value to the cache, swallowing backend errors."""
    with contextlib.suppress(Exception):
        get_cache().set(key, value, expire=expire, retry=True)


def _cache_get(key: str) -> Any:
    """Read a value from the cache, swallowing backend errors."""
    with contextlib.suppress(Exception):
        return get_cache().get(key)
    return None


async def cached_request(
    url: str,
    *,
    use_cache: bool = True,
    expire: "float | None" = None,
    method: Literal["GET", "POST"] = "GET",
    **kwargs: Any,
) -> Any:
    """Make a request through ``amake_request`` with unified disk caching.

    Parameters
    ----------
    url : str
        The URL to request.
    use_cache : bool
        When False, bypass the cache entirely and call ``amake_request`` directly.
    expire : float | None
        Seconds until the cached entry expires. ``None`` persists until evicted.
    method : str
        HTTP method, by default ``"GET"``.
    **kwargs
        Forwarded to ``amake_request`` (e.g. ``headers``, ``timeout``,
        ``response_callback``).

    Returns
    -------
    Any
        The parsed response.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_sec.utils.ratelimit import sec_amake_request as amake_request

    user_callback = kwargs.pop("response_callback", None)

    async def _checked_callback(response: Any, session: Any) -> Any:
        status = getattr(response, "status", 200)
        if status >= 400:
            raise OpenBBError(f"SEC request failed with HTTP {status}: {url}")
        if user_callback is not None:
            return await user_callback(response, session)
        return await response.json()

    kwargs["response_callback"] = _checked_callback

    if not use_cache:
        return await amake_request(url, method=method, **kwargs)

    key = _make_key(url, method)
    cached = await asyncio.to_thread(_cache_get, key)
    if cached is not None:
        return cached

    result = await amake_request(url, method=method, **kwargs)
    if not _is_empty(result):
        await asyncio.to_thread(_cache_set, key, result, expire)
    return result


def cached_text(
    url: str,
    *,
    use_cache: bool = True,
    expire: "float | None" = None,
    raise_for_status: bool = True,
    **kwargs: Any,
) -> str:
    """Fetch a URL's text body through ``make_request`` with disk caching.

    Parameters
    ----------
    url : str
        The URL to request.
    use_cache : bool
        When False, bypass the cache entirely.
    expire : float | None
        Seconds until the cached entry expires. ``None`` persists until evicted.
    raise_for_status : bool
        Raise for non-2xx responses before caching.
    **kwargs
        Forwarded to ``make_request`` (e.g. ``headers``, ``timeout``).

    Returns
    -------
    str
        The response body text.
    """
    from openbb_sec.utils.ratelimit import sec_make_request as make_request

    key = _make_key(url, suffix=" ::text")
    if use_cache:
        cached = _cache_get(key)
        if cached is not None:
            return cached

    response = make_request(url, **kwargs)
    if raise_for_status:
        response.raise_for_status()
    text = response.text
    if use_cache and text:
        _cache_set(key, text, expire)
    return text


def cached_bytes(
    url: str,
    *,
    use_cache: bool = True,
    expire: "float | None" = None,
    raise_for_status: bool = True,
    **kwargs: Any,
) -> bytes:
    """Fetch a URL's raw body (bytes) through ``make_request`` with disk caching.

    Parameters
    ----------
    url : str
        The URL to request.
    use_cache : bool
        When False, bypass the cache entirely.
    expire : float | None
        Seconds until the cached entry expires. ``None`` persists until evicted.
    raise_for_status : bool
        Raise for non-2xx responses before caching.
    **kwargs
        Forwarded to ``make_request`` (e.g. ``headers``, ``timeout``).

    Returns
    -------
    bytes
        The response body as raw bytes.
    """
    from openbb_sec.utils.ratelimit import sec_make_request as make_request

    key = _make_key(url, suffix=" ::bytes")
    if use_cache:
        cached = _cache_get(key)
        if cached is not None:
            return cached

    response = make_request(url, **kwargs)
    if raise_for_status:
        response.raise_for_status()
    content = response.content
    if use_cache and content:
        _cache_set(key, content, expire)
    return content


async def aget_cached(key: str) -> Any:
    """Read a value from the SEC cache by key, off the event loop."""
    return await asyncio.to_thread(_cache_get, key)


async def aset_cached(key: str, value: Any, expire: "float | None" = None) -> None:
    """Write a value to the SEC cache by key, off the event loop."""
    await asyncio.to_thread(_cache_set, key, value, expire)


def clear_cache() -> int:
    """Remove all entries from the SEC cache.

    Returns
    -------
    int
        The number of entries removed.
    """
    try:
        return get_cache().clear(retry=True)
    except Exception:  # noqa: BLE001
        return 0
