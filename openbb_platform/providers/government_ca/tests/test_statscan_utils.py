"""Tests for ``openbb_government_ca.statscan.utils``."""

from __future__ import annotations

import pytest

from openbb_government_ca.statscan.utils import (
    STATSCAN_PRODUCTS_OF_INTEREST,
    is_degraded,
    list_indicators,
    lookup_product,
)


class TestLookupProduct:
    """``lookup_product`` resolves both the homepage section and individual vectors."""

    def test_lookup_ind_econ_returns_section(self, seeded_meta):
        """The ``"ind-econ"`` token returns the whole statscan section."""
        section = lookup_product("ind-econ", seeded_meta.statscan)
        assert section is seeded_meta.statscan
        assert "indicators" in section

    def test_lookup_vector_id_returns_indicator(self, seeded_meta):
        """A numeric vector ID resolves to the matching indicator entry."""
        ind = lookup_product("2280069", seeded_meta.statscan)
        assert ind["source"] == "2280069"
        assert ind["title_en"] == "Imports"

    def test_lookup_unknown_vector_raises_with_hint(self, seeded_meta):
        """An unknown vector ID raises ``KeyError`` with a helpful hint."""
        # 2280087 starts with "228" — same prefix as 2280069.
        with pytest.raises(KeyError, match="Did you mean"):
            lookup_product("2280088", seeded_meta.statscan)

    def test_lookup_unknown_no_hint_when_no_candidates(self, seeded_meta):
        """When no candidates share a prefix, the error has no hint."""
        with pytest.raises(KeyError, match="not found in cache"):
            lookup_product("9999999", seeded_meta.statscan)

    def test_lookup_ind_econ_in_empty_cache_raises(self, empty_meta):
        """Looking up ``ind-econ`` in an empty cache raises a clear error."""
        with pytest.raises(KeyError, match="not found in cache"):
            lookup_product("ind-econ", empty_meta.statscan)


class TestListIndicators:
    """``list_indicators`` is a safe accessor for the indicators list."""

    def test_returns_indicators_from_seeded_cache(self, seeded_meta):
        """A seeded cache returns its indicators."""
        inds = list_indicators(seeded_meta.statscan)
        assert len(inds) == 2
        titles = [i["title_en"] for i in inds]
        assert "Imports" in titles
        assert "Employment" in titles

    def test_returns_empty_list_for_missing_key(self, empty_meta):
        """A cache without ``indicators`` returns an empty list."""
        assert list_indicators({}) == []
        assert list_indicators({"homepage_url": "x"}) == []

    def test_returns_copy_not_reference(self, seeded_meta):
        """``list_indicators`` returns a fresh list — mutating it doesn't affect the cache."""
        inds = list_indicators(seeded_meta.statscan)
        inds.clear()
        # The cache is untouched.
        assert len(seeded_meta.statscan["indicators"]) == 2


class TestIsDegraded:
    """``is_degraded`` detects degraded-mode cache sections."""

    def test_returns_false_for_ok_status(self, seeded_meta):
        """A cache with ``status='ok'`` is not degraded."""
        assert is_degraded(seeded_meta.statscan) is False

    def test_returns_true_for_degraded_status(self):
        """A cache with ``status='degraded'`` is degraded."""
        assert is_degraded({"status": "degraded"}) is True

    def test_returns_false_for_missing_status(self):
        """A cache without a ``status`` key is treated as not degraded."""
        assert is_degraded({}) is False


class TestConstants:
    """The constants tuple contains the brief-required entry."""

    def test_products_of_interest_contains_ind_econ(self):
        """The ``STATSCAN_PRODUCTS_OF_INTEREST`` tuple contains the homepage key."""
        assert "ind-econ" in STATSCAN_PRODUCTS_OF_INTEREST
