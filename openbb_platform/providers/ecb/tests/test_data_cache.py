import asyncio

from openbb_ecb.utils import data_cache


def test_make_key_is_stable():
    k1 = data_cache.make_key("exr", symbol="EURUSD", start="2024-01-01")
    k2 = data_cache.make_key("exr", start="2024-01-01", symbol="EURUSD")
    assert k1 == k2 and k1.startswith("exr:")


def test_ttl_for():
    assert data_cache.ttl_for("eligible_assets") == 12 * 3600
    assert data_cache.ttl_for("exr") == 6 * 3600
    assert data_cache.ttl_for("unknown") == data_cache.ttl_for("indicators")


def test_cache_disabled(monkeypatch):
    monkeypatch.setenv("OPENBB_ECB_NO_CACHE", "yes")
    assert data_cache.cache_disabled() is True
    monkeypatch.setenv("OPENBB_ECB_NO_CACHE", "")
    assert data_cache.cache_disabled() is False


def test_cache_directory_override(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENBB_ECB_CACHE_DIR", str(tmp_path / "c"))
    data_cache.reset_cache()
    assert data_cache._cache_directory() == str(tmp_path / "c")


def test_cache_directory_layered(monkeypatch):
    monkeypatch.delenv("OPENBB_ECB_CACHE_DIR", raising=False)
    directory = data_cache._cache_directory()
    assert directory.replace("\\", "/").endswith("ecb/data")


def test_cached_records_hit_miss_bypass(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENBB_ECB_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.delenv("OPENBB_ECB_NO_CACHE", raising=False)
    data_cache.reset_cache()
    calls = {"n": 0}

    async def loader():
        calls["n"] += 1
        return [{"v": 1}]

    key = data_cache.make_key("exr", x=1)
    a = asyncio.run(data_cache.cached_records("exr", key, loader, use_cache=True))
    b = asyncio.run(data_cache.cached_records("exr", key, loader, use_cache=True))
    assert a == b == [{"v": 1}]
    assert calls["n"] == 1

    asyncio.run(data_cache.cached_records("exr", key, loader, use_cache=False))
    assert calls["n"] == 2
    data_cache.reset_cache()


def test_cached_records_disabled_and_empty(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENBB_ECB_CACHE_DIR", str(tmp_path / "c2"))
    data_cache.reset_cache()
    monkeypatch.setenv("OPENBB_ECB_NO_CACHE", "1")
    calls = {"n": 0}

    async def loader():
        calls["n"] += 1
        return []

    key = data_cache.make_key("exr", x=2)
    asyncio.run(data_cache.cached_records("exr", key, loader, use_cache=True))
    asyncio.run(data_cache.cached_records("exr", key, loader, use_cache=True))
    assert calls["n"] == 2

    monkeypatch.delenv("OPENBB_ECB_NO_CACHE")
    asyncio.run(data_cache.cached_records("exr", key, loader, use_cache=True))
    asyncio.run(data_cache.cached_records("exr", key, loader, use_cache=True))
    assert calls["n"] == 4
    data_cache.reset_cache()
