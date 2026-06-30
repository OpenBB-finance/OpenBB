"""Raw-data disk cache for ECB fetchers (separate from the metadata cache).

Caches the *raw records a fetcher extracts* (the loader output, before
``transform_data`` standardizes it) — never the SDMX metadata catalog (that
ships in ``assets/ecb_cache.json.xz``). Backed by ``diskcache`` with per-dataset
TTLs grounded in ECB's actual release cadence.

Cache directory resolution (layered):
    1. ``OPENBB_ECB_CACHE_DIR`` environment variable, if set;
    2. else ``<get_user_cache_directory()>/ecb/data`` — and
       ``get_user_cache_directory()`` itself reads ``Preferences.cache_directory``
       from the V5 layered user settings (default ``~/OpenBBUserData/cache``).

Set ``OPENBB_ECB_NO_CACHE=1`` to disable caching globally.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from diskcache import Cache

# Time-to-live per dataset, in seconds, matched to ECB release cadence.
_HOUR = 3600
DATASET_TTL: dict[str, int] = {
    # Daily series published each TARGET business day (~16:00 CET).
    "exr": 6 * _HOUR,
    "fm": 6 * _HOUR,
    "estr": 6 * _HOUR,
    "yield_curve": 6 * _HOUR,
    # Eligible assets / collateral — refreshed daily at 18:15 CET.
    "eligible_assets": 12 * _HOUR,
    # Lower-frequency macro series (monthly / quarterly).
    "balance_of_payments": 24 * _HOUR,
    "mfi_interest_rates": 24 * _HOUR,
    "currency_reference_rates": 3 * _HOUR,
    # Feed/scrape sources.
    "releases": 1 * _HOUR,
    "calendar": 1 * _HOUR,
    # A published article's body never changes — cache it for a week.
    "release_body": 168 * _HOUR,
    # Generic SDMX series fetch.
    "indicators": 6 * _HOUR,
    # The set of series that exist in a dataflow (serieskeysonly) — changes rarely.
    "series": 24 * _HOUR,
}
_DEFAULT_TTL = 6 * _HOUR

_caches: dict[str, Cache] = {}


def _cache_directory() -> str:
    """Resolve the parsed-data cache directory (env var → layered config)."""
    override = os.environ.get("OPENBB_ECB_CACHE_DIR")
    if override:
        return override
    from openbb_core.app.utils import get_user_cache_directory

    return os.path.join(get_user_cache_directory(), "ecb", "data")


def cache_disabled() -> bool:
    """Return True when caching is globally disabled via env var."""
    return os.environ.get("OPENBB_ECB_NO_CACHE", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def ttl_for(dataset: str) -> int:
    """Return the TTL (seconds) for ``dataset``."""
    return DATASET_TTL.get(dataset, _DEFAULT_TTL)


def make_key(dataset: str, **params) -> str:
    """Build a stable cache key from a dataset name and query parameters."""
    payload = json.dumps({"d": dataset, "p": params}, sort_keys=True, default=str)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
    return f"{dataset}:{digest}"


def get_data_cache() -> Cache:
    """Return a (memoized per-directory) ``diskcache.Cache`` instance."""
    directory = _cache_directory()
    if directory not in _caches:
        from diskcache import Cache

        os.makedirs(directory, exist_ok=True)
        _caches[directory] = Cache(directory)
    return _caches[directory]


def reset_cache() -> None:
    """Close and forget all open cache handles (used by tests)."""
    for cache in _caches.values():
        with __import__("contextlib").suppress(Exception):
            cache.close()
    _caches.clear()


async def cached_records(
    dataset: str,
    key: str,
    loader: Callable[[], Awaitable[list[dict]]],
    *,
    use_cache: bool = True,
) -> list[dict]:
    """Return cached records for ``key`` or run ``loader`` and cache its result.

    ``loader`` is an async callable returning the parsed records. Empty results
    are not cached (so a transient miss isn't pinned for the whole TTL).
    """
    if not use_cache or cache_disabled():
        return await loader()
    cache = get_data_cache()
    cached = cache.get(key)
    if cached is not None:
        return cached
    records = await loader()
    if records:
        cache.set(key, records, expire=ttl_for(dataset))
    return records
