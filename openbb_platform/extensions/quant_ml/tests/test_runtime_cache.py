from __future__ import annotations

from openbb_quant_ml.service.runtime_cache import RuntimeTTLCache


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, bytes | str] = {}

    def get(self, key: str):
        return self.store.get(key)

    def set(self, key: str, value: str, nx: bool = False):
        if nx and key in self.store:
            return False
        self.store[key] = value
        return True

    def setex(self, key: str, ttl: int, value: bytes):
        self.store[key] = value
        return True

    def incr(self, key: str) -> int:
        current = self.store.get(key)
        current_int = int(current.decode("utf-8")) if isinstance(current, bytes) else int(current or 0)
        next_value = current_int + 1
        self.store[key] = str(next_value)
        return next_value

    def delete(self, key: str) -> int:
        return 1 if self.store.pop(key, None) is not None else 0


def test_runtime_ttl_cache_uses_local_storage_without_redis(monkeypatch) -> None:
    monkeypatch.delenv("OPENBB_QUANT_ML_CACHE_REDIS_URL", raising=False)
    monkeypatch.delenv("OPENBB_QUANT_ML_REDIS_URL", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)
    cache = RuntimeTTLCache(namespace="unit:no-redis", maxsize=4, ttl=60, redis_client=None)

    cache["alpha"] = {"value": 1}

    assert cache["alpha"] == {"value": 1}
    assert cache.get("missing") is None
    assert len(cache) == 1

    cache.clear()

    assert cache.get("alpha") is None


def test_runtime_ttl_cache_shares_entries_and_invalidation_with_redis() -> None:
    shared_redis = FakeRedis()
    cache_a = RuntimeTTLCache(
        namespace="unit:shared",
        maxsize=4,
        ttl=60,
        redis_client=shared_redis,
        cache_prefix="test-cache",
    )
    cache_b = RuntimeTTLCache(
        namespace="unit:shared",
        maxsize=4,
        ttl=60,
        redis_client=shared_redis,
        cache_prefix="test-cache",
    )
    cache_key = ("run-1", "lgbm_ranker")

    cache_a[cache_key] = {"status": "ok", "value": 42}

    assert cache_b[cache_key] == {"status": "ok", "value": 42}

    cache_a.clear()

    assert cache_a.get(cache_key) is None
    assert cache_b.get(cache_key) is None
