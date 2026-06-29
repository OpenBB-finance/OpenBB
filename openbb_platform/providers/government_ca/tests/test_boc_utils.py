"""Tests for ``openbb_government_ca.boc.utils`` — runtime lookups over the BoC cache."""

from __future__ import annotations

import pytest

from openbb_government_ca.boc.utils import (
    BOC_GROUPS_OF_INTEREST,
    BOC_SERIES_OF_INTEREST,
    is_degraded,
    list_groups,
    list_series,
    lookup_series,
    lookup_series_by_description,
    missing_series,
)


class TestConstants:
    """The constants tuple is the source of truth for cataloging scope."""

    def test_series_of_interest_contains_brief_required(self):
        """The brief-required series are all present."""
        # Brief-required series.
        for needle in ("FXUSDCAD", "CBC20210", "V39079", "BD.CDN.LONG.DQ.YLD"):
            assert needle in BOC_SERIES_OF_INTEREST, f"missing {needle}"

    def test_series_of_interest_contains_full_v390_family(self):
        """The full V390* family is cataloged (low/high/bank/target).

        Cataloging the whole family lets the Fase 5 fetcher pick the
        right one based on the official ``description`` field — that's
        the source of truth, not the series name.
        """
        for v in ("V39076", "V39077", "V39078", "V39079"):
            assert v in BOC_SERIES_OF_INTEREST

    def test_series_of_interest_contains_all_benchmark_tenors(self):
        """All benchmark bond tenors are cataloged."""
        for tenor in ("2YR", "3YR", "5YR", "7YR", "10YR", "LONG"):
            assert f"BD.CDN.{tenor}.DQ.YLD" in BOC_SERIES_OF_INTEREST

    def test_groups_of_interest_contains_fx_rates_daily(self):
        """``FX_RATES_DAILY`` group is cataloged."""
        assert "FX_RATES_DAILY" in BOC_GROUPS_OF_INTEREST


class TestLookupSeries:
    """``lookup_series`` resolves both individual series and groups."""

    def test_lookup_individual_series(self, seeded_meta):
        """A known series name resolves to its cache entry."""
        entry = lookup_series("FXUSDCAD", seeded_meta.boc)
        assert entry["name"] == "FXUSDCAD"
        assert entry["frequency"] == "daily"
        assert "label" in entry

    def test_lookup_group(self, seeded_meta):
        """A known group name resolves to its cache entry with ``kind='group'``."""
        entry = lookup_series("FX_RATES_DAILY", seeded_meta.boc)
        assert entry["kind"] == "group"
        assert "FXUSDCAD" in entry["members"]

    def test_lookup_v39079_has_target_description(self, seeded_meta):
        """V39079's description is the BoC's official target rate description."""
        entry = lookup_series("V39079", seeded_meta.boc)
        assert entry["description"] == "Target for the overnight rate"

    def test_lookup_cbc20210_is_alias_of_v39079(self, seeded_meta):
        """CBC20210 has the same label and description as V39079.

        This is the empirical evidence we collected in Fase 3: both
        series point to the same data (target overnight rate) and the
        Fase 5 fetcher can use either based on the description field.
        """
        cbc = lookup_series("CBC20210", seeded_meta.boc)
        v = lookup_series("V39079", seeded_meta.boc)
        assert cbc["description"] == v["description"] == "Target for the overnight rate"

    def test_lookup_v39078_is_bank_rate(self, seeded_meta):
        """V39078's description is 'Bank rate' (the upper band)."""
        entry = lookup_series("V39078", seeded_meta.boc)
        assert entry["description"] == "Bank rate"

    def test_lookup_unknown_raises_with_hint(self, seeded_meta):
        """An unknown name raises ``KeyError`` with a 'did you mean' hint."""
        with pytest.raises(KeyError, match="Did you mean"):
            lookup_series("FXUSDEUR", seeded_meta.boc)

    def test_lookup_unknown_no_hint_when_no_candidates(self, seeded_meta):
        """When no candidates share a prefix, the error has no hint."""
        with pytest.raises(KeyError, match="not found in cache"):
            lookup_series("ZZZNONE", seeded_meta.boc)


class TestLookupByDescription:
    """``lookup_series_by_description`` finds series by semantic role.

    This is the **recommended** way for the Fase 5 fetcher to pick a
    series: instead of hard-coding a series name (which might change
    in future Valet revisions), search by description substring. The
    description is the BoC's own semantic identifier.
    """

    def test_finds_target_overnight_rate(self, seeded_meta):
        """Searching 'Target for the overnight rate' finds both V39079 and CBC20210."""
        matches = lookup_series_by_description(
            "Target for the overnight rate", seeded_meta.boc
        )
        names = [m["name"] for m in matches]
        assert "V39079" in names
        assert "CBC20210" in names

    def test_finds_bank_rate(self, seeded_meta):
        """Searching 'Bank rate' finds V39078."""
        matches = lookup_series_by_description("Bank rate", seeded_meta.boc)
        names = [m["name"] for m in matches]
        assert "V39078" in names
        # V39079 should NOT match — its description is "Target", not "Bank rate".
        assert "V39079" not in names

    def test_finds_fx_series_by_partial_description(self, seeded_meta):
        """Searching 'exchange rate' finds all FX* series."""
        matches = lookup_series_by_description("exchange rate", seeded_meta.boc)
        names = [m["name"] for m in matches]
        assert "FXUSDCAD" in names

    def test_finds_benchmark_bonds(self, seeded_meta):
        """Searching 'Benchmark bond yield' finds the BD.CDN.* series."""
        matches = lookup_series_by_description("Benchmark bond yield", seeded_meta.boc)
        names = [m["name"] for m in matches]
        assert "BD.CDN.10YR.DQ.YLD" in names

    def test_empty_substring_returns_all_series(self, seeded_meta):
        """An empty substring matches all series (empty string is substring of any string)."""
        matches = lookup_series_by_description("", seeded_meta.boc)
        assert len(matches) == len(seeded_meta.boc["series"])

    def test_no_match_returns_empty_list(self, seeded_meta):
        """A substring that matches nothing returns an empty list (no error)."""
        matches = lookup_series_by_description("zzz_nonexistent_zzz", seeded_meta.boc)
        assert matches == []

    def test_case_insensitive_match(self, seeded_meta):
        """Search is case-insensitive."""
        upper = lookup_series_by_description(
            "TARGET FOR THE OVERNIGHT", seeded_meta.boc
        )
        lower = lookup_series_by_description(
            "target for the overnight", seeded_meta.boc
        )
        assert len(upper) == len(lower) > 0


class TestListAccessors:
    """``list_series`` and ``list_groups`` are safe accessors."""

    def test_list_series_returns_all_entries(self, seeded_meta):
        """``list_series`` returns every cataloged series as a list."""
        series_list = list_series(seeded_meta.boc)
        assert len(series_list) == 5
        names = {s["name"] for s in series_list}
        assert "FXUSDCAD" in names
        assert "V39079" in names

    def test_list_groups_returns_all_entries(self, seeded_meta):
        """``list_groups`` returns every cataloged group as a list."""
        groups_list = list_groups(seeded_meta.boc)
        assert len(groups_list) == 1
        assert groups_list[0]["name"] == "FX_RATES_DAILY"

    def test_list_series_returns_empty_for_empty_cache(self, empty_meta):
        """``list_series`` returns ``[]`` for an empty cache."""
        assert list_series(empty_meta.boc) == []
        assert list_groups(empty_meta.boc) == []


class TestDegradedMode:
    """``is_degraded`` and ``missing_series`` detect degraded-mode caches."""

    def test_is_degraded_false_for_ok_cache(self, seeded_meta):
        """A cache with ``status='ok'`` is not degraded."""
        assert is_degraded(seeded_meta.boc) is False

    def test_is_degraded_true_for_degraded_cache(self):
        """A cache with ``status='degraded'`` is degraded."""
        assert is_degraded({"status": "degraded"}) is True

    def test_is_degraded_false_for_missing_status(self):
        """A cache without a ``status`` key is treated as not degraded."""
        assert is_degraded({}) is False

    def test_missing_series_returns_empty_when_not_present(self, seeded_meta):
        """``missing_series`` returns ``[]`` when the key isn't in the cache."""
        assert missing_series(seeded_meta.boc) == []

    def test_missing_series_returns_list_when_present(self):
        """``missing_series`` returns the list when the key IS in the cache."""
        cache = {"missing_series": ["FOO", "BAR"]}
        assert missing_series(cache) == ["FOO", "BAR"]
