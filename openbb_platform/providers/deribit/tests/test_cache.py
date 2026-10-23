"""Tests for the Deribit response cache."""

import pytest

from openbb_deribit.utils import cache


class _Store:
    """A stand-in for the backend's response store."""

    def __init__(self, keys):
        self._keys = list(keys)
        self.deleted: list = []

    async def keys(self):
        """Yield every stored key."""
        for key in self._keys:
            yield key

    async def size(self):
        """Return how many responses are stored."""
        return len(self._keys)

    async def bulk_delete(self, keys):
        """Forget the named responses."""
        self.deleted.append(set(keys))
        self._keys = [key for key in self._keys if key not in keys]


class _Backend:
    """A stand-in for the SQLite backend."""

    def __init__(self, keys=()):
        self.responses = _Store(keys)
        self.expired = 0

    async def delete_expired_responses(self):
        """Mark the expired responses for deletion."""
        self.expired += 1


@pytest.fixture(autouse=True)
def _reset_sweep():
    """Let each test sweep once, as the first caller in a process would."""
    cache._swept = False
    yield
    cache._swept = False


class TestConfiguration:
    """The cache is bounded by a TTL per endpoint and a size cap."""

    def test_path_lives_under_the_user_cache(self):
        """The cache file is kept with the other OpenBB HTTP caches."""
        assert cache.cache_path().endswith("/http/deribit")

    def test_backend_carries_the_ttl_map(self, tmp_path, monkeypatch):
        """The backend is built with the per-endpoint expiries."""
        monkeypatch.setattr(cache, "cache_path", lambda: str(tmp_path / "deribit"))
        backend = cache.get_cache_backend()

        assert backend.expire_after == cache.CACHE_TTL_DEFAULT
        assert backend.urls_expire_after

    def test_live_endpoints_are_never_cached(self):
        """A quote or a book is read fresh every time."""
        for pattern in (
            "*/public/get_order_book*",
            "*/public/ticker*",
            "*/public/get_time*",
            "*/public/status*",
        ):
            assert cache.URL_CACHE_TTL[pattern] == 0

    def test_reference_endpoints_are_held_longest(self):
        """A listing that barely changes is held for a day."""
        assert cache.URL_CACHE_TTL["*/public/get_currencies*"] == cache.DAY


class TestSweep:
    """The sweep drops what expired, then trims what is still too big."""

    @pytest.mark.asyncio
    async def test_deletes_expired_and_vacuums(self, monkeypatch, tmp_path):
        """A file under the cap is swept once and left alone."""
        stored = tmp_path / "deribit.sqlite"
        stored.write_bytes(b"x")
        monkeypatch.setattr(cache, "cache_path", lambda: str(tmp_path / "deribit"))
        vacuums: list = []

        async def _vacuum(backend):
            vacuums.append(backend)

        monkeypatch.setattr(cache, "_vacuum", _vacuum)
        backend = _Backend(["a", "b"])
        await cache.sweep_cache(backend)

        assert backend.expired == 1
        assert len(vacuums) == 1
        assert backend.responses.deleted == []

    @pytest.mark.asyncio
    async def test_trims_by_the_share_that_overshoots(self, monkeypatch, tmp_path):
        """A file over the cap loses the oldest share of its rows."""
        stored = tmp_path / "deribit.sqlite"
        stored.write_bytes(b"x" * 400)
        monkeypatch.setattr(cache, "cache_path", lambda: str(tmp_path / "deribit"))
        monkeypatch.setattr(cache, "CACHE_MAX_BYTES", 100)
        backend = _Backend([f"key-{index}" for index in range(8)])

        async def _vacuum(_):
            if backend.responses.deleted:
                stored.write_bytes(b"x" * 50)

        monkeypatch.setattr(cache, "_vacuum", _vacuum)
        await cache.sweep_cache(backend)

        assert backend.responses.deleted
        assert len(backend.responses.deleted[0]) == 6

    @pytest.mark.asyncio
    async def test_stops_when_nothing_is_left_to_drop(self, monkeypatch, tmp_path):
        """A file still too big with nothing stored gives up."""
        stored = tmp_path / "deribit.sqlite"
        stored.write_bytes(b"x" * 400)
        monkeypatch.setattr(cache, "cache_path", lambda: str(tmp_path / "deribit"))
        monkeypatch.setattr(cache, "CACHE_MAX_BYTES", 100)

        async def _vacuum(backend):
            return None

        monkeypatch.setattr(cache, "_vacuum", _vacuum)
        backend = _Backend([])
        await cache.sweep_cache(backend)

        assert backend.responses.deleted == []

    @pytest.mark.asyncio
    async def test_missing_file(self, monkeypatch, tmp_path):
        """A cache that was never written is swept without error."""
        monkeypatch.setattr(cache, "cache_path", lambda: str(tmp_path / "deribit"))

        async def _vacuum(backend):
            return None

        monkeypatch.setattr(cache, "_vacuum", _vacuum)
        backend = _Backend([])
        await cache.sweep_cache(backend)

        assert backend.expired == 1

    @pytest.mark.asyncio
    async def test_sweeps_once_per_process(self, monkeypatch, tmp_path):
        """A second caller does not sweep again."""
        monkeypatch.setattr(cache, "cache_path", lambda: str(tmp_path / "deribit"))

        async def _vacuum(backend):
            return None

        monkeypatch.setattr(cache, "_vacuum", _vacuum)
        backend = _Backend([])
        await cache.sweep_cache(backend)
        await cache.sweep_cache(backend)

        assert backend.expired == 1

    @pytest.mark.asyncio
    async def test_oldest_stops_at_the_count(self):
        """The trim reads only as many keys as it means to drop."""
        backend = _Backend([f"key-{index}" for index in range(10)])

        assert len(await cache._oldest(backend, 3)) == 3


class TestVacuum:
    """Vacuuming gives back the pages the deleted responses held."""

    @pytest.mark.asyncio
    async def test_skips_a_foreign_backend(self):
        """A store that is not SQLite is left alone."""
        assert await cache._vacuum(_Backend([])) is None

    @pytest.mark.asyncio
    async def test_runs_against_sqlite(self, tmp_path, monkeypatch):
        """A real SQLite store is vacuumed."""
        monkeypatch.setattr(cache, "cache_path", lambda: str(tmp_path / "deribit"))
        backend = cache.get_cache_backend()
        await backend.responses.write("key", b"value")
        await cache._vacuum(backend)

        assert (tmp_path / "deribit.sqlite").exists()
