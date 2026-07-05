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


# ===========================================================================
# SDMX catalog accessors (get_catalog, list_cubes, lookup_cube,
# lookup_series_by_vector, search_series, list_subjects)
# ===========================================================================
class TestCatalogAccessors:
    """Cover the SDMX catalog accessor functions."""

    def test_get_catalog_returns_empty_for_no_catalog(self, empty_meta):
        from openbb_government_ca.statscan.utils import get_catalog

        assert get_catalog(empty_meta.statscan) == {}

    def test_get_catalog_returns_dict_when_present(self, seeded_meta):
        from openbb_government_ca.statscan.utils import get_catalog

        cache = seeded_meta.statscan
        cache["catalog"] = {"cubes": {}, "subjects": {}}
        result = get_catalog(cache)
        assert "cubes" in result

    def test_list_cubes_returns_empty_for_no_catalog(self, empty_meta):
        from openbb_government_ca.statscan.utils import list_cubes

        assert list_cubes(empty_meta.statscan) == []

    def test_list_cubes_returns_cubes_list(self, seeded_meta):
        from openbb_government_ca.statscan.utils import list_cubes

        cache = seeded_meta.statscan
        cache["catalog"] = {
            "cubes": {
                "10100139": {"pid": "10100139", "title_en": "GDP"},
                "20100008": {"pid": "20100008", "title_en": "CPI"},
            }
        }
        cubes = list_cubes(cache)
        assert len(cubes) == 2

    def test_lookup_cube_returns_entry(self, seeded_meta):
        from openbb_government_ca.statscan.utils import lookup_cube

        cache = seeded_meta.statscan
        cache["catalog"] = {"cubes": {"10100139": {"pid": "10100139"}}}
        cube = lookup_cube("10100139", cache)
        assert cube["pid"] == "10100139"

    def test_lookup_cube_unknown_pid_raises(self, seeded_meta):
        from openbb_government_ca.statscan.utils import lookup_cube

        cache = seeded_meta.statscan
        cache["catalog"] = {"cubes": {"10100139": {"pid": "10100139"}}}
        with pytest.raises(KeyError, match="not found in catalog"):
            lookup_cube("99999999", cache)

    def test_lookup_series_by_vector_returns_match(self, seeded_meta):
        from openbb_government_ca.statscan.utils import lookup_series_by_vector

        cache = seeded_meta.statscan
        cache["catalog"] = {
            "cubes": {
                "10100139": {
                    "pid": "10100139",
                    "title_en": "GDP",
                    "series": [
                        {
                            "vector_id": "V1",
                            "label_en": "GDP, monthly",
                            "coordinate": "1.1.1.1",
                        }
                    ],
                }
            }
        }
        series = lookup_series_by_vector("V1", cache)
        assert series["vector_id"] == "V1"
        assert series["cube_pid"] == "10100139"
        assert series["cube_title_en"] == "GDP"

    def test_lookup_series_by_vector_handles_lowercase_v(self, seeded_meta):
        from openbb_government_ca.statscan.utils import lookup_series_by_vector

        cache = seeded_meta.statscan
        cache["catalog"] = {
            "cubes": {
                "10100139": {
                    "pid": "10100139",
                    "series": [{"vector_id": "V1"}],
                }
            }
        }
        assert lookup_series_by_vector("v1", cache)["vector_id"] == "V1"

    def test_lookup_series_by_vector_unknown_raises(self, seeded_meta):
        from openbb_government_ca.statscan.utils import lookup_series_by_vector

        cache = seeded_meta.statscan
        cache["catalog"] = {"cubes": {"10100139": {"pid": "10100139", "series": []}}}
        with pytest.raises(KeyError, match="not found in catalog"):
            lookup_series_by_vector("V999", cache)

    def test_search_series_returns_matches(self, seeded_meta):
        from openbb_government_ca.statscan.utils import search_series

        cache = seeded_meta.statscan
        cache["catalog"] = {
            "cubes": {
                "10100139": {
                    "pid": "10100139",
                    "title_en": "GDP",
                    "series": [
                        {"vector_id": "V1", "label_en": "GDP, monthly"},
                        {"vector_id": "V2", "label_en": "GDP, quarterly"},
                    ],
                },
                "20100008": {
                    "pid": "20100008",
                    "title_en": "CPI",
                    "series": [{"vector_id": "V3", "label_en": "CPI All-items"}],
                },
            }
        }
        results = search_series("GDP", cache)
        assert len(results) == 2
        for r in results:
            assert "GDP" in r["label_en"]

    def test_search_series_empty_query_returns_empty(self, seeded_meta):
        from openbb_government_ca.statscan.utils import search_series

        cache = seeded_meta.statscan
        cache["catalog"] = {"cubes": {"10100139": {"pid": "10100139", "series": []}}}
        assert search_series("", cache) == []

    def test_list_subjects_returns_dict(self, seeded_meta):
        from openbb_government_ca.statscan.utils import list_subjects

        cache = seeded_meta.statscan
        cache["catalog"] = {"subjects": {"13": "Economic accounts"}}
        subjects = list_subjects(cache)
        assert subjects == {"13": "Economic accounts"}

    def test_list_subjects_returns_empty_for_no_catalog(self, empty_meta):
        from openbb_government_ca.statscan.utils import list_subjects

        assert list_subjects(empty_meta.statscan) == {}
