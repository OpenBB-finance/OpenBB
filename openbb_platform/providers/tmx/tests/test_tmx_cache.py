"""Tests for the TMX cache and transport layer."""

import pytest

from openbb_tmx.utils import cache


async def _nothing(backend):
    """Stand in for the vacuum, which needs a real SQLite file."""
    return None


class TestHeaders:
    """The request headers sent to the TMX hosts."""

    @pytest.mark.parametrize("accept", ["json", "text", "binary"])
    def test_accept_types(self, accept):
        headers = cache.get_headers(accept)
        assert "Accept" in headers
        assert headers["Referer"] == "https://money.tmx.com/"
        assert headers["User-Agent"]

    def test_referer_drives_origin(self):
        headers = cache.get_headers("json", referer="https://www.m-x.ca/")
        assert headers["Origin"] == "https://www.m-x.ca"

    def test_invalid_accept_type(self):
        with pytest.raises(ValueError, match="Invalid accept_type"):
            cache.get_headers("xml")


class TestTtlMaps:
    """The cache expiry tables."""

    def test_url_patterns_are_globs(self):
        assert all(p.startswith("*") for p in cache.URL_CACHE_TTL)

    def test_ttls_are_positive(self):
        assert all(v > 0 for v in cache.URL_CACHE_TTL.values())
        assert all(v > 0 for v in cache.GQL_TTL.values())

    def test_quotes_expire_faster_than_reference_data(self):
        assert cache.GQL_TTL["getQuoteBySymbol"] < cache.GQL_TTL["getIndexConstituents"]

    def test_ciro_pattern_targets_the_live_host(self):
        assert any("bondtradedata.ciro.ca" in p for p in cache.URL_CACHE_TTL)
        assert not any("iiroc" in p for p in cache.URL_CACHE_TTL)

    def test_every_gql_operation_is_known(self):
        from openbb_tmx.utils import gql

        documents = {
            v for k, v in vars(gql).items() if k.isupper() and isinstance(v, str)
        }
        assert documents
        for operation in cache.GQL_TTL:
            assert isinstance(operation, str)


class TestCacheKeys:
    """What the cached responses are filed under."""

    LOOKUP = (
        "https://app.quotemedia.com/datatool/lookup.json?q=b&limit=20000&countryCode=CA"
    )

    def test_a_rotating_token_is_left_out_of_the_key(self):
        """QuoteMedia issues a new token per session, on the same query."""
        backend = cache.get_cache_backend()

        assert backend.create_key("GET", f"{self.LOOKUP}&token=aaaa") == (
            backend.create_key("GET", f"{self.LOOKUP}&token=bbbb")
        )

    def test_the_query_itself_still_tells_them_apart(self):
        backend = cache.get_cache_backend()

        assert backend.create_key("GET", f"{self.LOOKUP}&token=aaaa") != (
            backend.create_key("GET", self.LOOKUP.replace("q=b", "q=c") + "&token=aaaa")
        )

    def test_the_token_is_the_only_thing_ignored(self):
        assert cache.IGNORED_PARAMS == ("token",)


class TestCacheSweep:
    """The cache is bounded by age and by size."""

    @staticmethod
    def _backend(size, keys, dropped, stored=None):
        from types import SimpleNamespace
        from unittest.mock import AsyncMock

        async def bulk_delete(taken):
            dropped.append(len(taken))

            if stored is not None:
                stored.write_bytes(b"x" * 10)

        async def held():
            for index in range(keys):
                yield f"key{index}"

        return SimpleNamespace(
            delete_expired_responses=AsyncMock(),
            responses=SimpleNamespace(
                size=AsyncMock(return_value=size),
                keys=held,
                bulk_delete=bulk_delete,
            ),
        )

    def test_expired_responses_are_deleted_not_just_ignored(
        self, monkeypatch, tmp_path
    ):
        """An expiry alone leaves the row behind and the file grows forever."""
        import asyncio

        monkeypatch.setattr(cache, "_swept", False)
        monkeypatch.setattr(cache, "cache_path", lambda: str(tmp_path / "absent"))
        monkeypatch.setattr(cache, "_vacuum", _nothing)
        backend = self._backend(0, 0, [])
        asyncio.run(cache.sweep_cache(backend))

        backend.delete_expired_responses.assert_awaited_once()

    def test_it_sweeps_once_for_the_whole_process(self, monkeypatch, tmp_path):
        import asyncio

        monkeypatch.setattr(cache, "_swept", False)
        monkeypatch.setattr(cache, "cache_path", lambda: str(tmp_path / "absent"))
        monkeypatch.setattr(cache, "_vacuum", _nothing)
        backend = self._backend(0, 0, [])
        asyncio.run(cache.sweep_cache(backend))
        asyncio.run(cache.sweep_cache(backend))

        backend.delete_expired_responses.assert_awaited_once()

    def test_a_file_over_the_limit_drops_its_oldest(self, monkeypatch, tmp_path):
        """What the sweep leaves over the limit is trimmed by the overshoot."""
        import asyncio

        stored = tmp_path / "probe.sqlite"
        stored.write_bytes(b"x" * 1000)
        dropped: list = []

        monkeypatch.setattr(cache, "_swept", False)
        monkeypatch.setattr(cache, "cache_path", lambda: str(tmp_path / "probe"))
        monkeypatch.setattr(cache, "_vacuum", _nothing)
        monkeypatch.setattr(cache, "CACHE_MAX_BYTES", 500)
        asyncio.run(cache.sweep_cache(self._backend(10, 10, dropped, stored)))

        assert dropped == [5]

    def test_a_file_under_the_limit_is_left_alone(self, monkeypatch, tmp_path):
        import asyncio

        stored = tmp_path / "probe.sqlite"
        stored.write_bytes(b"x" * 100)
        dropped: list = []

        monkeypatch.setattr(cache, "_swept", False)
        monkeypatch.setattr(cache, "cache_path", lambda: str(tmp_path / "probe"))
        monkeypatch.setattr(cache, "_vacuum", _nothing)
        monkeypatch.setattr(cache, "CACHE_MAX_BYTES", 500)
        asyncio.run(cache.sweep_cache(self._backend(10, 10, dropped, stored)))

        assert dropped == []

    def test_a_file_with_nothing_left_to_drop_is_left_alone(
        self, monkeypatch, tmp_path
    ):
        """A file over the limit whose rows have all already gone."""
        import asyncio

        stored = tmp_path / "probe.sqlite"
        stored.write_bytes(b"x" * 1000)
        dropped: list = []

        monkeypatch.setattr(cache, "_swept", False)
        monkeypatch.setattr(cache, "cache_path", lambda: str(tmp_path / "probe"))
        monkeypatch.setattr(cache, "_vacuum", _nothing)
        monkeypatch.setattr(cache, "CACHE_MAX_BYTES", 500)
        asyncio.run(cache.sweep_cache(self._backend(10, 0, dropped, stored)))

        assert dropped == []
        assert stored.stat().st_size == 1000


class TestVacuum:
    """Giving back the pages the deleted responses were held in."""

    def test_a_backend_without_a_sqlite_store_is_left_alone(self):
        import asyncio
        from types import SimpleNamespace

        asyncio.run(cache._vacuum(SimpleNamespace(responses=object())))

    def test_a_sqlite_store_is_vacuumed(self, tmp_path):
        import asyncio

        from aiohttp_client_cache.backends.sqlite import SQLiteBackend

        backend = SQLiteBackend(cache_name=str(tmp_path / "probe"))
        executed: list = []

        async def run():
            await backend.responses.write("k", b"v")
            await cache._vacuum(backend)
            executed.append(True)

        asyncio.run(run())

        assert executed == [True]


class TestDatabasePreparation:
    """The pragmas that let the cache survive concurrent use."""

    def test_the_file_is_set_to_write_ahead_logging(self, monkeypatch, tmp_path):
        import sqlite3

        monkeypatch.setattr(cache, "cache_path", lambda: str(tmp_path / "probe"))
        cache.prepare_database()
        connection = sqlite3.connect(tmp_path / "probe.sqlite")

        try:
            journal = connection.execute("PRAGMA journal_mode").fetchone()[0]
            vacuum = connection.execute("PRAGMA auto_vacuum").fetchone()[0]
        finally:
            connection.close()

        assert journal == "wal"
        assert vacuum == cache.INCREMENTAL

    def test_an_already_prepared_file_is_left_alone(self, monkeypatch, tmp_path):
        monkeypatch.setattr(cache, "cache_path", lambda: str(tmp_path / "probe"))
        cache.prepare_database()
        cache.prepare_database()

        assert (tmp_path / "probe.sqlite").exists()

    def test_an_unusable_file_is_tolerated(self, monkeypatch, tmp_path):
        blocked = tmp_path / "blocked"
        blocked.mkdir()
        monkeypatch.setattr(cache, "cache_path", lambda: str(blocked))
        cache.prepare_database()


class TestCacheFallback:
    """A cache that cannot be written to costs a stored response, not the answer."""

    async def test_a_locked_cache_falls_back_to_the_plain_session(self):
        import sqlite3

        attempts: list = []

        async def send(cached):
            attempts.append(cached)

            if cached:
                raise sqlite3.OperationalError("database is locked")

            return "answered"

        assert await cache._uncached_on_cache_error(send, True) == "answered"
        assert attempts == [True, False]

    async def test_the_cache_is_skipped_when_it_was_not_asked_for(self):
        attempts: list = []

        async def send(cached):
            attempts.append(cached)

            return "answered"

        assert await cache._uncached_on_cache_error(send, False) == "answered"
        assert attempts == [False]

    async def test_another_failure_is_not_swallowed(self):
        async def send(cached):
            raise ValueError("not a cache problem")

        with pytest.raises(ValueError, match="not a cache problem"):
            await cache._uncached_on_cache_error(send, True)
