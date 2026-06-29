"""Tests for the ``GovernmentCaMetadata`` singleton and cache mixin.

These are pure unit tests — no network, no filesystem. The seeded
fixture in ``conftest.py`` pre-loads a small but realistic cache blob.
"""

from __future__ import annotations

import threading

import pytest

from openbb_government_ca.utils.metadata import (
    GovernmentCaMetadata,
    GovernmentCaMetadataDependency,
)


class TestSingleton:
    """Singleton behavior — the heart of the V5 metadata pattern."""

    def test_singleton_returns_same_instance(self, seeded_meta):
        """Two calls to ``GovernmentCaMetadata()`` return the same object."""
        again = GovernmentCaMetadata()
        assert again is seeded_meta

    def test_singleton_thread_safe(self, seeded_meta):
        """Concurrent instantiation doesn't produce two instances."""
        results: list[GovernmentCaMetadata] = []

        def _make() -> None:
            results.append(GovernmentCaMetadata())

        threads = [threading.Thread(target=_make) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(r is seeded_meta for r in results)

    def test_reset_destroys_singleton(self, seeded_meta):
        """``_reset`` clears the singleton so the next call builds fresh."""
        GovernmentCaMetadata._reset()
        fresh = GovernmentCaMetadata()  # __init__ runs again — but _load is patched
        assert fresh is not seeded_meta

    def test_deepcopy_returns_self(self, seeded_meta):
        """Singletons are not deep-copyable — ``deepcopy`` returns ``self``."""
        import copy

        assert copy.deepcopy(seeded_meta) is seeded_meta
        assert copy.copy(seeded_meta) is seeded_meta


class TestCacheAccess:
    """Tests for the cache accessor properties."""

    def test_boc_property_returns_series_and_groups(self, seeded_meta):
        """``.boc`` exposes both ``series`` and ``groups`` sub-maps."""
        assert "series" in seeded_meta.boc
        assert "groups" in seeded_meta.boc
        assert "FXUSDCAD" in seeded_meta.boc["series"]
        assert "FX_RATES_DAILY" in seeded_meta.boc["groups"]

    def test_statscan_property_returns_indicators(self, seeded_meta):
        """``.statscan`` exposes the ``indicators`` list and ``geo_lookup`` map."""
        assert "indicators" in seeded_meta.statscan
        assert "geo_lookup" in seeded_meta.statscan
        assert len(seeded_meta.statscan["indicators"]) == 2

    def test_generated_at_is_string(self, seeded_meta):
        """``generated_at`` is the ISO 8601 timestamp from the blob."""
        assert isinstance(seeded_meta.generated_at, str)
        assert seeded_meta.generated_at == "2026-06-28T04:17:00Z"

    def test_source_is_string(self, seeded_meta):
        """``source`` is the cache source label."""
        assert seeded_meta.source == "test-fixture"


class TestEmptyState:
    """Tests for the empty-cache path — useful for error-message coverage."""

    def test_empty_boc_returns_empty_dict(self, empty_meta):
        """An empty singleton exposes empty ``.boc`` / ``.statscan`` dicts.

        The canonical sub-maps (``series``, ``groups``, ``indicators``,
        ``geo_lookup``) are only materialised by ``_apply_blob`` — an
        empty singleton starts with bare ``{}`` so callers can detect
        "no data loaded" by checking ``not meta.boc``.
        """
        assert empty_meta.boc == {}
        assert empty_meta.statscan == {}


class TestDependency:
    """FastAPI ``Depends`` wiring — make sure the type is usable as a dependency."""

    def test_dependency_is_annotated_type(self):
        """``GovernmentCaMetadataDependency`` is an ``Annotated`` type."""
        # Annotated types carry their metadata in ``__metadata__``.
        # We don't import typing.Annotated here to keep the test robust
        # against Python 3.10 vs 3.12 differences.
        assert hasattr(GovernmentCaMetadataDependency, "__metadata__")

    def test_dependency_callable_returns_singleton(self, seeded_meta):
        """Calling the dependency returns the singleton instance."""
        instance = GovernmentCaMetadata()
        assert instance() is seeded_meta


@pytest.mark.parametrize(
    "blob",
    [
        {},
        {"boc": {}},
        {"statscan": {}},
        {"boc": {"series": {}}, "statscan": {"indicators": []}},
    ],
)
def test_apply_blob_handles_partial_blobs(empty_meta, blob):
    """``_apply_blob`` should never crash on a partial blob — it should
    fill in sensible defaults for missing sections."""
    empty_meta._apply_blob(blob)
    assert "series" in empty_meta.boc
    assert "groups" in empty_meta.boc
    assert "indicators" in empty_meta.statscan
    assert "geo_lookup" in empty_meta.statscan
