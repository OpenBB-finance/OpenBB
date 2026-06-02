"""Process-wide FRED API rate limiter, in-memory cache, and request helper.

Every FRED API request in this provider should be routed through `fred_get`.
The helper provides:

* A global minimum-interval throttle (default 600 ms ≈ 100 req/min), well
  below FRED's 120 req/min ceiling.
* Auto-retry on HTTP 429 with `Retry-After` / exponential backoff, so
  transient throttling does not surface as an error.
* An in-memory TTL LRU cache so that repeated identical requests (typical
  when a user refreshes or re-opens widgets) reuse the prior response.
* Single-flight de-duplication: concurrent callers asking for the same URL
  share a single in-flight request instead of fanning out duplicates.
"""

# pylint: disable=import-outside-toplevel

from __future__ import annotations

import asyncio
import copy
import os
import re
import threading
import time
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError


def _float_env(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


MIN_INTERVAL_SECONDS = _float_env("OPENBB_FRED_MIN_INTERVAL", 0.6)
MAX_RETRIES = _int_env("OPENBB_FRED_MAX_RETRIES", 4)
DEFAULT_BACKOFF_SECONDS = _float_env("OPENBB_FRED_BACKOFF", 2.0)
MAX_BACKOFF_SECONDS = _float_env("OPENBB_FRED_MAX_BACKOFF", 30.0)
CACHE_TTL_SECONDS = _float_env("OPENBB_FRED_CACHE_TTL", 300.0)
CACHE_MAX_ENTRIES = _int_env("OPENBB_FRED_CACHE_SIZE", 512)

_RATE_LIMIT_MESSAGE = (
    "FRED API rate limit exceeded (HTTP 429). Please wait a moment and try again."
)

_throttle_lock = threading.Lock()
_last_request_at: float = 0.0

_cache_lock = threading.Lock()
_cache: OrderedDict[str, tuple[float, Any]] = OrderedDict()

_inflight_lock = threading.Lock()
_inflight: dict[tuple[int, str], asyncio.Future] = {}

_API_KEY_RE = re.compile(r"([?&])api_key=[^&]*")


class _RateLimitedResponse(Exception):
    """Internal sentinel raised when a 429 is observed on a FRED response."""

    def __init__(self, retry_after: float | None = None) -> None:
        super().__init__(_RATE_LIMIT_MESSAGE)
        self.retry_after = retry_after


def _cache_key(url: str) -> str:
    """Build a cache key from a URL, stripping the API key."""
    return _API_KEY_RE.sub(r"\1api_key=__redacted__", url)


def _cache_get(key: str) -> Any:
    """Return a cached value if present and not expired, else None.

    Returns a deep copy so downstream mutation of dicts / lists does not
    corrupt subsequent cache hits.
    """
    if CACHE_TTL_SECONDS <= 0 or CACHE_MAX_ENTRIES <= 0:
        return None
    with _cache_lock:
        entry = _cache.get(key)
        if entry is None:
            return None
        stored_at, value = entry
        if time.monotonic() - stored_at > CACHE_TTL_SECONDS:
            _cache.pop(key, None)
            return None
        _cache.move_to_end(key)
        cached_value = value
    return copy.deepcopy(cached_value)


def _cache_set(key: str, value: Any) -> None:
    """Insert a deep-copied value into the cache and evict oldest entries when full."""
    if CACHE_TTL_SECONDS <= 0 or CACHE_MAX_ENTRIES <= 0:
        return
    snapshot = copy.deepcopy(value)
    with _cache_lock:
        _cache[key] = (time.monotonic(), snapshot)
        _cache.move_to_end(key)
        while len(_cache) > CACHE_MAX_ENTRIES:
            _cache.popitem(last=False)


def cache_clear() -> None:
    """Clear the in-memory FRED response cache (useful for tests)."""
    with _cache_lock:
        _cache.clear()


async def acquire() -> None:
    """Enforce a minimum gap between successive FRED API requests."""
    global _last_request_at  # noqa: PLW0603  # pylint: disable=global-statement
    while True:
        with _throttle_lock:
            now = time.monotonic()
            wait_for = _last_request_at + MIN_INTERVAL_SECONDS - now
            if wait_for <= 0:
                _last_request_at = now
                return
        await asyncio.sleep(wait_for)


def _parse_retry_after(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return max(float(value), 0.0)
    except (TypeError, ValueError):
        return None


def _check_payload_rate_limit(payload: Any) -> None:
    if not isinstance(payload, dict):
        return
    code = payload.get("error_code") or payload.get("status_code")
    message = payload.get("error_message") or payload.get("message") or ""
    if str(code) == "429" or "too many requests" in str(message).lower():
        raise _RateLimitedResponse()


async def _fetch(
    url: str,
    response_callback: Callable[[Any, Any], Awaitable[dict | list[dict]]] | None,
    retries: int,
    **kwargs: Any,
) -> Any:
    """Perform a single throttled fetch with retry-on-429."""
    from openbb_core.provider.utils.helpers import amake_request

    async def _wrapped_callback(response, session):
        status = getattr(response, "status", None)
        if status == 429:
            retry_after = _parse_retry_after(
                response.headers.get("Retry-After")
                if hasattr(response, "headers")
                else None
            )
            raise _RateLimitedResponse(retry_after)
        if response_callback is not None:
            return await response_callback(response, session)
        payload = await response.json()
        _check_payload_rate_limit(payload)
        return payload

    attempt = 0
    while True:
        await acquire()
        try:
            return await amake_request(
                url, response_callback=_wrapped_callback, **kwargs
            )
        except _RateLimitedResponse as rl:
            attempt += 1
            if attempt > retries:
                raise OpenBBError(ValueError(_RATE_LIMIT_MESSAGE)) from rl
            backoff = (
                rl.retry_after
                if rl.retry_after is not None
                else min(
                    DEFAULT_BACKOFF_SECONDS * (2 ** (attempt - 1)),
                    MAX_BACKOFF_SECONDS,
                )
            )
            await asyncio.sleep(max(backoff, MIN_INTERVAL_SECONDS))


def _is_cacheable(value: Any) -> bool:
    """Don't cache empty / falsy payloads — they're usually transient errors."""
    if value is None:
        return False
    return not (isinstance(value, (list, dict, str, bytes)) and len(value) == 0)


async def fred_get(
    url: str,
    *,
    response_callback: Callable[[Any, Any], Awaitable[dict | list[dict]]] | None = None,
    max_retries: int | None = None,
    use_cache: bool = True,
    **kwargs: Any,
) -> Any:
    """Throttled, retrying, cached GET wrapper around `amake_request` for FRED.

    Concurrent calls for the same URL share a single in-flight request so
    duplicates collapse into one upstream API call.
    """
    retries = MAX_RETRIES if max_retries is None else max_retries
    cache_key = _cache_key(url) if use_cache else None

    if cache_key is not None:
        cached = _cache_get(cache_key)
        if cached is not None:
            return cached

    inflight_key: tuple[int, str] | None = None
    future: asyncio.Future | None = None
    owner = False
    if cache_key is not None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop is not None:
            inflight_key = (id(loop), cache_key)
            with _inflight_lock:
                existing = _inflight.get(inflight_key)
                if existing is not None:
                    future = existing
                else:
                    future = loop.create_future()
                    _inflight[inflight_key] = future
                    owner = True

    if future is not None and not owner:
        shared = await future
        return copy.deepcopy(shared)

    try:
        result = await _fetch(
            url,
            response_callback=response_callback,
            retries=retries,
            **kwargs,
        )
    except BaseException as exc:
        if future is not None and owner and not future.done():
            future.set_exception(exc)
        raise
    finally:
        if inflight_key is not None and owner:
            with _inflight_lock:
                _inflight.pop(inflight_key, None)

    if cache_key is not None and _is_cacheable(result):
        _cache_set(cache_key, result)

    if future is not None and owner and not future.done():
        future.set_result(result)

    return result


async def fred_get_many(
    urls: list[str],
    *,
    response_callback: Callable[[Any, Any], Awaitable[dict | list[dict]]] | None = None,
    return_exceptions: bool = False,
    use_cache: bool = True,
    **kwargs: Any,
) -> list[Any]:
    """Issue many FRED requests under the global rate limit and cache."""
    tasks = [
        fred_get(
            url,
            response_callback=response_callback,
            use_cache=use_cache,
            **kwargs,
        )
        for url in urls
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    cleaned: list[Any] = []
    first_error: Exception | None = None
    for result in results:
        if isinstance(result, Exception):
            if return_exceptions:
                cleaned.append(result)
            elif first_error is None:
                first_error = result
            continue
        cleaned.append(result)

    if first_error is not None and not cleaned:
        raise first_error

    return cleaned
