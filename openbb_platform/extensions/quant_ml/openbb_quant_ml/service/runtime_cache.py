"""Runtime cache helpers with optional Redis-backed sharing."""

from __future__ import annotations

import hashlib
import importlib
import logging
import os
import pickle
from collections.abc import Iterator, MutableMapping
from threading import RLock
from typing import Any

from cachetools import TTLCache

LOGGER = logging.getLogger(__name__)
_REDIS_IMPORT_WARNING_EMITTED = False
_REDIS_RUNTIME_WARNING_EMITTED = False


def _get_redis_url() -> str | None:
    for key in (
        "OPENBB_QUANT_ML_CACHE_REDIS_URL",
        "OPENBB_QUANT_ML_REDIS_URL",
        "REDIS_URL",
    ):
        value = str(os.getenv(key, "")).strip()
        if value:
            return value
    return None


def _get_cache_prefix() -> str:
    return (
        str(os.getenv("OPENBB_QUANT_ML_CACHE_PREFIX", "")).strip()
        or "openbb:quant-ml:cache"
    )


def _load_redis_client(redis_url: str | None) -> Any | None:
    global _REDIS_IMPORT_WARNING_EMITTED
    if not redis_url:
        return None
    try:
        redis = importlib.import_module("redis")
    except ModuleNotFoundError:
        if not _REDIS_IMPORT_WARNING_EMITTED:
            LOGGER.warning(
                "Redis cache is configured but the 'redis' package is not installed. "
                "Falling back to in-process TTLCache."
            )
            _REDIS_IMPORT_WARNING_EMITTED = True
        return None
    return redis.Redis.from_url(redis_url)


class RuntimeTTLCache(MutableMapping[Any, Any]):
    """TTL cache with optional Redis-backed sharing and namespace invalidation."""

    def __init__(
        self,
        *,
        namespace: str,
        maxsize: int,
        ttl: int | float,
        redis_client: Any | None = None,
        cache_prefix: str | None = None,
    ) -> None:
        self.namespace = namespace
        self.ttl = max(float(ttl), 1.0)
        self._local = TTLCache(maxsize=maxsize, ttl=self.ttl)
        self._lock = RLock()
        self._cache_prefix = cache_prefix or _get_cache_prefix()
        self._redis = (
            redis_client
            if redis_client is not None
            else _load_redis_client(_get_redis_url())
        )
        self._namespace_version = "0"
        self._version_key = f"{self._cache_prefix}:version:{self.namespace}"

    def _emit_runtime_warning(self, action: str) -> None:
        global _REDIS_RUNTIME_WARNING_EMITTED
        if _REDIS_RUNTIME_WARNING_EMITTED:
            return
        LOGGER.warning(
            "Redis cache operation failed during %s for namespace %s. "
            "Falling back to in-process TTLCache.",
            action,
            self.namespace,
            exc_info=True,
        )
        _REDIS_RUNTIME_WARNING_EMITTED = True

    def _serialize_key(self, key: Any) -> str:
        digest = hashlib.sha256(
            pickle.dumps(key, protocol=pickle.HIGHEST_PROTOCOL)
        ).hexdigest()
        return f"{self._cache_prefix}:items:{self.namespace}:{self._namespace_version}:{digest}"

    def _sync_namespace_version(self) -> None:
        if self._redis is None:
            return
        try:
            version = self._redis.get(self._version_key)
            if version is None:
                self._redis.set(self._version_key, "1", nx=True)
                version = self._redis.get(self._version_key) or b"1"
            normalized = (
                version.decode("utf-8")
                if isinstance(version, (bytes, bytearray))
                else str(version)
            )
            if normalized != self._namespace_version:
                self._local.clear()
                self._namespace_version = normalized
        except Exception:
            self._emit_runtime_warning("version-sync")
            self._redis = None

    def __getitem__(self, key: Any) -> Any:
        with self._lock:
            self._sync_namespace_version()
            try:
                return self._local[key]
            except KeyError:
                pass
            if self._redis is None:
                raise KeyError(key) from None
            redis_key = self._serialize_key(key)
            try:
                payload = self._redis.get(redis_key)
            except Exception:
                self._emit_runtime_warning("read")
                self._redis = None
                raise KeyError(key) from None
            if payload is None:
                raise KeyError(key)
            value = pickle.loads(payload)
            self._local[key] = value
            return value

    def __setitem__(self, key: Any, value: Any) -> None:
        with self._lock:
            self._sync_namespace_version()
            self._local[key] = value
            if self._redis is None:
                return
            redis_key = self._serialize_key(key)
            try:
                self._redis.setex(
                    redis_key,
                    int(max(1, round(self.ttl))),
                    pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL),
                )
            except Exception:
                self._emit_runtime_warning("write")
                self._redis = None

    def __delitem__(self, key: Any) -> None:
        with self._lock:
            self._sync_namespace_version()
            del self._local[key]
            if self._redis is None:
                return
            redis_key = self._serialize_key(key)
            try:
                self._redis.delete(redis_key)
            except Exception:
                self._emit_runtime_warning("delete")
                self._redis = None

    def __iter__(self) -> Iterator[Any]:
        with self._lock:
            self._sync_namespace_version()
            return iter(list(self._local.keys()))

    def __len__(self) -> int:
        with self._lock:
            self._sync_namespace_version()
            return len(self._local)

    def clear(self) -> None:
        with self._lock:
            self._local.clear()
            if self._redis is None:
                return
            try:
                self._namespace_version = str(self._redis.incr(self._version_key))
            except Exception:
                self._emit_runtime_warning("clear")
                self._redis = None

    def get(self, key: Any, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default


def build_runtime_ttl_cache(
    *,
    namespace: str,
    maxsize: int,
    ttl: int | float,
) -> RuntimeTTLCache:
    return RuntimeTTLCache(namespace=namespace, maxsize=maxsize, ttl=ttl)
