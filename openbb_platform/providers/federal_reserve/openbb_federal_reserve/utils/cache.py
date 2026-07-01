"""Unified on-disk cache for Federal Reserve data downloads.

A single ``diskcache.Cache`` persists raw upstream payloads so repeat requests
within a dataset's release window avoid re-downloading. The cache directory is
resolved from, highest priority first:

1. the ``OPENBB_FEDERAL_RESERVE_CACHE_DIR`` environment variable,
2. ``preferences.cache_directory`` from the layered OpenBB config
   (``UserService().default_user_settings.preferences``), and
3. the OpenBB default user cache directory.

Each entry is stored with a time-to-live aligned to its dataset's real release
cadence (see ``seconds_until_next_release``) so it expires when fresh data is
expected to be available rather than on a flat timer.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from diskcache import Cache

CACHE_DIR_ENV_VAR = "OPENBB_FEDERAL_RESERVE_CACHE_DIR"
CACHE_SUBDIR = "federal_reserve"
EASTERN = ZoneInfo("America/New_York")

_cache: Cache | None = None
_MISS = object()


def cache_directory() -> Path:
    """Resolve the cache directory from the env var, layered config, then default.

    Returns
    -------
    Path
        The ``federal_reserve`` cache directory, created if absent.
    """
    override = os.environ.get(CACHE_DIR_ENV_VAR)
    if override:
        base = Path(override).expanduser()
    else:
        from openbb_core.app.service.user_service import UserService

        preferences = UserService().default_user_settings.preferences
        base = Path(preferences.cache_directory).expanduser()

    path = base / CACHE_SUBDIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_cache() -> Cache:
    """Return the process-wide ``diskcache.Cache`` for the provider."""
    global _cache  # noqa: PLW0603
    if _cache is None:
        _cache = Cache(str(cache_directory()))
    return _cache


def reset_cache() -> None:
    """Close and drop the cached handle so the next ``get_cache`` re-resolves it."""
    global _cache  # noqa: PLW0603
    if _cache is not None:
        _cache.close()
        _cache = None


def now_eastern() -> datetime:
    """Return the current time in US/Eastern, the Fed's publication timezone."""
    return datetime.now(tz=EASTERN)


def seconds_until_next_release(cadence: str, *, now: datetime | None = None) -> float:
    """Return seconds until the next expected release for a cadence.

    Parameters
    ----------
    cadence : str
        One of ``"daily"``, ``"weekly"``, or ``"quarterly"``. Daily expires at
        the next US/Eastern midnight, weekly seven days out, quarterly at the
        start of the next calendar quarter. Any other value falls back to daily.
    now : datetime | None
        Reference time; defaults to the current US/Eastern time.

    Returns
    -------
    float
        Seconds until the next release boundary, floored at 60.
    """
    current = now or now_eastern()
    midnight = current.replace(hour=0, minute=0, second=0, microsecond=0)

    if cadence == "weekly":
        target = midnight + timedelta(days=7)
    elif cadence == "quarterly":
        quarter_start_month = ((current.month - 1) // 3) * 3 + 1
        next_quarter_month = quarter_start_month + 3
        year = current.year + (next_quarter_month > 12)
        month = (
            next_quarter_month - 12 if next_quarter_month > 12 else next_quarter_month
        )
        target = midnight.replace(year=year, month=month, day=1)
    else:
        target = midnight + timedelta(days=1)

    return max((target - current).total_seconds(), 60.0)


def cached(
    key: Any, ttl: float | Callable[[], float], producer: Callable[[], Any]
) -> Any:
    """Return the cached value for ``key`` or produce, store, and return it.

    The ``ttl`` (seconds) may be a callable evaluated only on a cache miss, so
    an availability lookup runs at most once per stored entry. Falsy producer
    results are not cached, so a failed or empty upstream response is retried
    on the next call.
    """
    cache = get_cache()
    value = cache.get(key, default=_MISS)
    if value is not _MISS:
        return value

    produced = producer()
    if produced:
        expire = ttl if isinstance(ttl, (int, float)) else ttl()
        cache.set(key, produced, expire=expire)
    return produced


def disk_cached(
    key: str,
    *,
    cadence: str = "daily",
    ttl: float | Callable[[], float] | None = None,
) -> Callable:
    """Decorate a download helper to cache its result on disk by release cadence.

    Parameters
    ----------
    key : str
        Stable base cache key; call arguments are appended to it.
    cadence : str
        Release cadence passed to ``seconds_until_next_release`` when ``ttl``
        is not given.
    ttl : float | Callable[[], float] | None
        Explicit time-to-live (or a zero-argument callable returning one) that
        overrides ``cadence``.
    """

    def decorator(func: Callable) -> Callable:
        """Wrap ``func`` with the on-disk cache."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Return ``func``'s cached result, keyed by its arguments."""
            cache_key: Any = key
            if args or kwargs:
                cache_key = (key, args, tuple(sorted(kwargs.items())))
            expire = (
                ttl
                if ttl is not None
                else (lambda: seconds_until_next_release(cadence))
            )
            return cached(cache_key, expire, lambda: func(*args, **kwargs))

        return wrapper

    return decorator
