"""Tests for the unified on-disk cache utility."""

from datetime import datetime

from openbb_federal_reserve.utils import cache


class TestCacheDirectory:
    """Tests for ``cache_directory`` resolution."""

    def test_env_var_override_wins(self, tmp_path, monkeypatch):
        """The env var takes priority and the federal_reserve subdir is created."""
        monkeypatch.setenv(cache.CACHE_DIR_ENV_VAR, str(tmp_path / "envcache"))
        resolved = cache.cache_directory()
        assert resolved == tmp_path / "envcache" / cache.CACHE_SUBDIR
        assert resolved.is_dir()

    def test_falls_back_to_layered_preferences(self, tmp_path, monkeypatch):
        """Without the env var the layered ``cache_directory`` preference is used."""
        from openbb_core.app.service.user_service import UserService

        monkeypatch.delenv(cache.CACHE_DIR_ENV_VAR, raising=False)
        preferences = UserService().default_user_settings.preferences
        monkeypatch.setattr(preferences, "cache_directory", str(tmp_path / "prefcache"))
        resolved = cache.cache_directory()
        assert resolved == tmp_path / "prefcache" / cache.CACHE_SUBDIR
        assert resolved.is_dir()


class TestCacheHandle:
    """Tests for ``get_cache`` / ``reset_cache``."""

    def test_get_cache_is_singleton(self):
        """Repeated calls return the same cache handle."""
        first = cache.get_cache()
        assert cache.get_cache() is first

    def test_reset_cache_drops_handle(self):
        """``reset_cache`` closes and clears the cached handle."""
        cache.get_cache()
        cache.reset_cache()
        assert cache._cache is None

    def test_now_eastern_is_timezone_aware(self):
        """``now_eastern`` returns an aware US/Eastern timestamp."""
        assert cache.now_eastern().tzinfo is cache.EASTERN


class TestSecondsUntilNextRelease:
    """Tests for the cadence-aligned expiry calculation."""

    def test_daily_expires_at_next_midnight(self):
        """Daily cadence expires at the next US/Eastern midnight."""
        now = datetime(2026, 2, 10, 12, 0, tzinfo=cache.EASTERN)
        assert cache.seconds_until_next_release("daily", now=now) == 12 * 3600

    def test_weekly_expires_seven_days_out(self):
        """Weekly cadence targets midnight seven days ahead."""
        now = datetime(2026, 2, 10, 0, 0, tzinfo=cache.EASTERN)
        assert cache.seconds_until_next_release("weekly", now=now) == 7 * 86400

    def test_quarterly_targets_next_quarter_start(self):
        """Quarterly cadence targets the first day of the next calendar quarter."""
        now = datetime(2026, 2, 10, 12, 0, tzinfo=cache.EASTERN)
        target = datetime(2026, 4, 1, 0, 0, tzinfo=cache.EASTERN)
        assert (
            cache.seconds_until_next_release("quarterly", now=now)
            == (target - now).total_seconds()
        )

    def test_quarterly_rolls_into_next_year(self):
        """A Q4 reference rolls the quarter start into January of next year."""
        now = datetime(2026, 11, 5, 0, 0, tzinfo=cache.EASTERN)
        target = datetime(2027, 1, 1, 0, 0, tzinfo=cache.EASTERN)
        assert (
            cache.seconds_until_next_release("quarterly", now=now)
            == (target - now).total_seconds()
        )

    def test_unknown_cadence_falls_back_to_daily(self):
        """An unrecognized cadence behaves like daily."""
        now = datetime(2026, 2, 10, 6, 0, tzinfo=cache.EASTERN)
        assert cache.seconds_until_next_release("hourly", now=now) == 18 * 3600

    def test_result_is_floored_at_sixty_seconds(self):
        """A reference moments before midnight still yields at least 60 seconds."""
        now = datetime(2026, 2, 10, 23, 59, 59, tzinfo=cache.EASTERN)
        assert cache.seconds_until_next_release("daily", now=now) == 60.0


class TestCached:
    """Tests for the ``cached`` get-or-produce helper."""

    def test_stores_and_returns_value(self):
        """A produced value is stored and returned, and reused on a hit."""
        calls: list[int] = []

        def producer():
            calls.append(1)
            return "value"

        assert cache.cached("key", 100, producer) == "value"
        assert cache.cached("key", 100, producer) == "value"
        assert calls == [1]

    def test_does_not_store_falsy_results(self):
        """Empty producer results are not cached so the next call retries."""
        calls: list[int] = []

        def producer():
            calls.append(1)
            return []

        assert cache.cached("empty", 100, producer) == []
        assert cache.cached("empty", 100, producer) == []
        assert calls == [1, 1]

    def test_callable_ttl_evaluated_once_on_miss(self):
        """A callable ttl is evaluated only when the value is stored."""
        ttl_calls: list[int] = []

        def ttl():
            ttl_calls.append(1)
            return 100.0

        cache.cached("ttl-key", ttl, lambda: "v")
        cache.cached("ttl-key", ttl, lambda: "v")
        assert ttl_calls == [1]


class TestDiskCached:
    """Tests for the ``disk_cached`` decorator."""

    def test_caches_by_argument(self):
        """Results are cached per call-argument signature."""
        calls: list[int] = []

        @cache.disk_cached("byarg", cadence="daily")
        def fn(value):
            calls.append(value)
            return f"v{value}"

        assert fn(1) == "v1"
        assert fn(1) == "v1"
        assert fn(2) == "v2"
        assert calls == [1, 2]

    def test_no_argument_function_uses_bare_key(self):
        """A zero-argument helper caches under the bare key."""
        calls: list[int] = []

        @cache.disk_cached("bare")
        def fn():
            calls.append(1)
            return "value"

        assert fn() == "value"
        assert fn() == "value"
        assert calls == [1]

    def test_explicit_ttl_callable_overrides_cadence(self):
        """An explicit ttl callable is honored over the cadence."""
        ttl_calls: list[int] = []

        @cache.disk_cached("explicit", ttl=lambda: ttl_calls.append(1) or 50.0)
        def fn():
            return "value"

        assert fn() == "value"
        assert ttl_calls == [1]
