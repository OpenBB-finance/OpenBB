"""Tests for the on-disk FRED response cache."""

import pytest

from openbb_fred.utils import cache


class TestRedact:
    """Keeping the API key out of the cache key."""

    def test_the_key_is_replaced(self):
        assert cache.redact("https://x/a?api_key=secret") == (
            "https://x/a?api_key=__redacted__"
        )

    def test_a_key_among_others_is_replaced(self):
        assert cache.redact("https://x/a?b=1&api_key=secret&c=2") == (
            "https://x/a?b=1&api_key=__redacted__&c=2"
        )

    def test_a_url_without_a_key_is_untouched(self):
        assert cache.redact("https://x/a?b=1") == "https://x/a?b=1"

    def test_two_keys_share_one_entry(self):
        assert cache.redact("https://x/a?api_key=one") == cache.redact(
            "https://x/a?api_key=two"
        )


class TestTtlFor:
    """The lifetime each endpoint's responses are held for."""

    def test_an_endpoint_takes_its_own_lifetime(self):
        assert (
            cache.ttl_for("https://api.stlouisfed.org/fred/series/observations?a=1")
            == 4 * cache.HOUR
        )

    def test_the_longest_matching_path_wins(self):
        assert (
            cache.ttl_for("https://api.stlouisfed.org/fred/series/search?a=1")
            == cache.DAY
        )

    def test_a_shorter_path_still_matches(self):
        assert cache.ttl_for("https://api.stlouisfed.org/fred/series?a=1") == cache.DAY

    def test_a_geographic_endpoint_is_held_longest(self):
        assert (
            cache.ttl_for("https://api.stlouisfed.org/geofred/series/group?a=1")
            == 7 * cache.DAY
        )

    def test_an_unknown_endpoint_takes_the_default(self):
        assert cache.ttl_for("https://api.stlouisfed.org/fred/unknown") == (
            cache.DEFAULT_TTL
        )

    def test_a_url_without_a_query_is_read(self):
        assert cache.ttl_for("https://api.stlouisfed.org/fred/releases") == cache.DAY

    def test_every_lifetime_is_scaled(self, monkeypatch):
        monkeypatch.setenv("OPENBB_FRED_DISK_TTL_MULTIPLIER", "2")

        assert cache.ttl_for("https://api.stlouisfed.org/fred/unknown") == (
            2 * cache.DEFAULT_TTL
        )

    def test_an_unreadable_multiplier_falls_back(self, monkeypatch):
        monkeypatch.setenv("OPENBB_FRED_DISK_TTL_MULTIPLIER", "soon")

        assert cache.ttl_for("https://api.stlouisfed.org/fred/unknown") == (
            cache.DEFAULT_TTL
        )


class TestConfiguration:
    """The environment the cache reads its settings from."""

    def test_the_cache_is_on_by_default(self, monkeypatch):
        monkeypatch.delenv("OPENBB_FRED_DISK_CACHE", raising=False)

        assert cache.enabled() is True

    @pytest.mark.parametrize("value", ["0", "false", "False"])
    def test_the_cache_can_be_switched_off(self, monkeypatch, value):
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE", value)

        assert cache.enabled() is False

    def test_the_size_limit_is_read(self, monkeypatch):
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE_SIZE", "1024")

        assert cache.size_limit() == 1024

    def test_an_unreadable_size_limit_falls_back(self, monkeypatch):
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE_SIZE", "plenty")

        assert cache.size_limit() == cache.DEFAULT_SIZE_LIMIT

    def test_an_empty_setting_falls_back(self, monkeypatch):
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE_SIZE", "")

        assert cache.size_limit() == cache.DEFAULT_SIZE_LIMIT

    def test_the_directory_is_read(self, monkeypatch, tmp_path):
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE_DIR", str(tmp_path))

        assert cache.cache_directory() == str(tmp_path)

    def test_without_a_setting_the_user_cache_is_used(self, monkeypatch):
        monkeypatch.delenv("OPENBB_FRED_DISK_CACHE_DIR", raising=False)

        assert cache.cache_directory().endswith("/fred")


class TestDiskCache:
    """Reading and writing payloads."""

    async def test_a_payload_survives_a_round_trip(self):
        await cache.disk_set("https://x/round?api_key=one", {"ok": True})

        assert await cache.disk_get("https://x/round?api_key=two") == {"ok": True}

    async def test_an_absent_payload_reads_as_nothing(self):
        assert await cache.disk_get("https://x/never-written") is None

    async def test_nothing_is_written_when_the_cache_is_off(self, monkeypatch):
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE", "0")
        await cache.disk_set("https://x/off", {"ok": True})

        assert await cache.disk_get("https://x/off") is None

    def test_no_cache_is_built_when_the_cache_is_off(self, monkeypatch):
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE", "0")

        assert cache.get_disk_cache() is None

    def test_the_cache_is_rebuilt_when_the_directory_moves(self, monkeypatch, tmp_path):
        first = cache.get_disk_cache()
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE_DIR", str(tmp_path / "moved"))
        second = cache.get_disk_cache()

        assert second is not first
        assert second.directory == str(tmp_path / "moved")


class TestStats:
    """What the cache reports about itself."""

    async def test_an_entry_is_counted(self):
        before = cache.stats()["items"]
        await cache.disk_set("https://x/counted", {"ok": True})
        after = cache.stats()

        assert after["enabled"] is True
        assert after["items"] == before + 1
        assert after["bytes"] > 0
        assert after["directory"]

    def test_a_cache_that_is_off_reports_nothing(self, monkeypatch):
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE", "0")

        assert cache.stats() == {"enabled": False, "items": 0, "bytes": 0}


class TestLifecycle:
    """Emptying and releasing the cache."""

    async def test_clearing_drops_every_entry(self, monkeypatch, tmp_path):
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE_DIR", str(tmp_path / "cleared"))
        await cache.disk_set("https://x/dropped", {"ok": True})
        cache.clear()

        assert cache.stats()["items"] == 0

    async def test_clearing_a_cache_that_is_off_does_nothing(
        self, monkeypatch, tmp_path
    ):
        """Nothing is opened, and every entry written before is still there."""
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE_DIR", str(tmp_path / "switched-off"))
        await cache.disk_set("https://x/held-through-a-clear", {"ok": True})
        held = cache.stats()["items"]
        cache.close()
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE", "0")
        cache.clear()

        assert held == 1
        assert cache._cache is None

        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE", "1")

        assert cache.stats()["items"] == held
        assert await cache.disk_get("https://x/held-through-a-clear") == {"ok": True}

    async def test_a_released_cache_opens_again(self, monkeypatch, tmp_path):
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE_DIR", str(tmp_path / "reopened"))
        await cache.disk_set("https://x/kept", {"ok": True})
        cache.close()

        assert await cache.disk_get("https://x/kept") == {"ok": True}

    async def test_releasing_twice_is_harmless(self, monkeypatch, tmp_path):
        """The second release finds nothing to release and leaves the entries."""
        monkeypatch.setenv("OPENBB_FRED_DISK_CACHE_DIR", str(tmp_path / "released"))
        await cache.disk_set("https://x/released", {"ok": True})

        assert cache._cache is not None

        cache.close()
        cache.close()

        assert cache._cache is None
        assert cache._cache_directory == ""
        assert await cache.disk_get("https://x/released") == {"ok": True}
