"""Tests for the BoC Valet fetcher in ``utils/generate_cache.py``.

The fetcher makes three HTTP calls per build:

1. ``GET /lists/series/json`` — full catalog of 15,642 series.
2. ``GET /lists/groups/json`` — full catalog of 2,445 groups.
3. For each group of interest: ``GET /groups/<NAME>/json`` to resolve
   members.

All HTTP calls go through ``openbb_government_ca.utils._http.http_get_json``,
which we mock at the module level. The tests cover:

- Happy path (all 3 calls succeed)
- Top-level series list fails → degraded mode
- Top-level groups list fails → partial success (series cached, groups empty)
- Group member resolution fails → group entry has empty ``members``
- Series-of-interest not found in catalog → ``missing_series`` populated
- All entries are normalized with the right derived fields
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from openbb_government_ca.utils import generate_cache
from openbb_government_ca.utils._http import NetworkError

_FIXTURE_DIR = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Fixture loaders
# ---------------------------------------------------------------------------
@pytest.fixture
def boc_series_list_sample() -> dict:
    """Load the synthetic BoC /lists/series/json sample."""
    with (_FIXTURE_DIR / "boc_series_list_sample.json").open() as f:
        return json.load(f)


@pytest.fixture
def boc_groups_list_sample() -> dict:
    """Load the synthetic BoC /lists/groups/json sample."""
    with (_FIXTURE_DIR / "boc_groups_list_sample.json").open() as f:
        return json.load(f)


@pytest.fixture
def boc_group_members_sample() -> dict:
    """Load the synthetic BoC /groups/FX_RATES_DAILY/json sample."""
    with (_FIXTURE_DIR / "boc_group_fx_rates_daily_members.json").open() as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# _normalize_boc_series_entry
# ---------------------------------------------------------------------------
class TestParseBondTenor:
    """``_parse_bond_tenor`` extracts tenor info from BoC bond series names.

    This is the field that lets the Phase 5 yields fetcher map series
    directly to ``treasury_rates.year_<N>`` fields without parsing
    the series name in the fetcher itself.
    """

    @pytest.mark.parametrize(
        "name,expected_tenor,expected_years",
        [
            ("BD.CDN.2YR.DQ.YLD", "2Y", 2),
            ("BD.CDN.3YR.DQ.YLD", "3Y", 3),
            ("BD.CDN.5YR.DQ.YLD", "5Y", 5),
            ("BD.CDN.7YR.DQ.YLD", "7Y", 7),
            ("BD.CDN.10YR.DQ.YLD", "10Y", 10),
            ("BD.CDN.LONG.DQ.YLD", "LONG", 30),  # canonical long-term benchmark
            ("BD.CDN.RRB.DQ.YLD", "RRB", None),  # Real Return Bonds — no nominal tenor
        ],
    )
    def test_bond_series_get_tenor(self, name, expected_tenor, expected_years):
        """Bond series get the right tenor label and years."""
        tenor, years = generate_cache._parse_bond_tenor(name)
        assert tenor == expected_tenor
        assert years == expected_years

    @pytest.mark.parametrize(
        "name",
        [
            "FXUSDCAD",
            "V39079",
            "V39078",
            "CBC20210",
            "AVG.INTWO",
            "A.BCPI",
            "M.BCPI",
            "UNKNOWN.SERIES",
            "",
        ],
    )
    def test_non_bond_series_get_none(self, name):
        """Non-bond series get ``(None, None)``."""
        tenor, years = generate_cache._parse_bond_tenor(name)
        assert tenor is None
        assert years is None

    def test_case_insensitive_match(self):
        """Tenor parsing is case-insensitive (handles lowercase input)."""
        tenor, years = generate_cache._parse_bond_tenor("bd.cdn.10yr.dq.yld")
        assert tenor == "10Y"
        assert years == 10

    def test_only_canonical_bond_pattern_matches(self):
        """Series that don't match the canonical ``BD.CDN.<N>YR.DQ.YLD`` pattern return None.

        For example, ``BD.CDN.25YR.MONTHLY`` doesn't match because the
        regex requires the ``.DQ.YLD`` suffix. This is intentional —
        we only catalog tenors for the actual benchmark series the BoC
        publishes, not hypothetical variants.
        """
        tenor, years = generate_cache._parse_bond_tenor("BD.CDN.25YR.MONTHLY")
        assert tenor is None
        assert years is None


class TestNormalizeSeriesEntry:
    """``_normalize_boc_series_entry`` produces the cache shape Phase 5 expects."""

    def test_preserves_label_description_link(self):
        """The raw Valet fields are preserved verbatim."""
        raw = {
            "label": "USD/CAD",
            "description": "Daily average exchange rate...",
            "link": "https://www.bankofcanada.ca/valet/series/FXUSDCAD",
        }
        result = generate_cache._normalize_boc_series_entry("FXUSDCAD", raw)
        assert result["label"] == "USD/CAD"
        assert result["description"] == "Daily average exchange rate..."
        assert result["link"] == "https://www.bankofcanada.ca/valet/series/FXUSDCAD"

    def test_builds_observations_url(self):
        """The ``observations_url`` is pre-built for the Phase 5 fetcher."""
        result = generate_cache._normalize_boc_series_entry(
            "FXUSDCAD", {"label": "", "description": "", "link": ""}
        )
        assert (
            result["observations_url"]
            == "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json"
        )

    @pytest.mark.parametrize(
        "name,expected_freq",
        [
            ("FXUSDCAD", "daily"),
            ("FXEURCAD", "daily"),
            ("BD.CDN.10YR.DQ.YLD", "daily"),
            ("BD.CDN.LONG.DQ.YLD", "daily"),
            ("V39076", "daily"),
            ("V39079", "daily"),
            ("CBC20210", "unknown"),  # doesn't match any prefix
            ("AVG.INTWO", "daily"),  # CORRA-style daily average
            ("A.BCPI", "annual"),
            ("M.BCPI", "monthly"),
            ("UNKNOWN.SERIES", "unknown"),
        ],
    )
    def test_frequency_heuristic(self, name, expected_freq):
        """The frequency is guessed from the series name prefix."""
        result = generate_cache._normalize_boc_series_entry(
            name, {"label": "", "description": "", "link": ""}
        )
        assert result["frequency"] == expected_freq

    def test_cataloged_at_is_iso8601(self):
        """``cataloged_at`` is an ISO 8601 UTC timestamp."""
        result = generate_cache._normalize_boc_series_entry(
            "FXUSDCAD", {"label": "", "description": "", "link": ""}
        )
        assert result["cataloged_at"].endswith("Z")
        assert len(result["cataloged_at"]) == 20

    def test_handles_missing_optional_fields(self):
        """Missing fields default to empty strings (no KeyError)."""
        result = generate_cache._normalize_boc_series_entry("X", {})
        assert result["label"] == ""
        assert result["description"] == ""
        assert result["link"] == ""

    def test_bond_series_get_tenor_fields(self):
        """Bond series get populated ``tenor`` and ``tenor_years`` fields."""
        result = generate_cache._normalize_boc_series_entry(
            "BD.CDN.10YR.DQ.YLD",
            {
                "label": "Benchmark bond yield: 10 year",
                "description": "...",
                "link": "",
            },
        )
        assert result["tenor"] == "10Y"
        assert result["tenor_years"] == 10

    def test_non_bond_series_get_none_tenor(self):
        """Non-bond series get ``tenor=None`` and ``tenor_years=None``."""
        result = generate_cache._normalize_boc_series_entry(
            "FXUSDCAD", {"label": "USD/CAD", "description": "...", "link": ""}
        )
        assert result["tenor"] is None
        assert result["tenor_years"] is None

    def test_rrb_bond_gets_tenor_but_no_years(self):
        """RRB (Real Return Bonds) gets tenor label but ``tenor_years=None``."""
        result = generate_cache._normalize_boc_series_entry(
            "BD.CDN.RRB.DQ.YLD",
            {
                "label": "Real Return Bonds yield: long-term",
                "description": "...",
                "link": "",
            },
        )
        assert result["tenor"] == "RRB"
        assert result["tenor_years"] is None


# ---------------------------------------------------------------------------
# _normalize_boc_group_entry
# ---------------------------------------------------------------------------
class TestNormalizeGroupEntry:
    """``_normalize_boc_group_entry`` produces the cache shape for groups."""

    def test_preserves_label_description_link(self):
        """The raw Valet fields are preserved verbatim."""
        raw = {
            "label": "Daily exchange rates",
            "description": "All daily FX rates...",
            "link": "https://www.bankofcanada.ca/valet/groups/FX_RATES_DAILY",
        }
        result = generate_cache._normalize_boc_group_entry("FX_RATES_DAILY", raw)
        assert result["label"] == "Daily exchange rates"
        assert result["description"] == "All daily FX rates..."

    def test_builds_members_and_observations_urls(self):
        """The ``members_url`` and ``observations_url`` are pre-built."""
        result = generate_cache._normalize_boc_group_entry(
            "FX_RATES_DAILY", {"label": "", "description": "", "link": ""}
        )
        assert (
            result["members_url"]
            == "https://www.bankofcanada.ca/valet/groups/FX_RATES_DAILY/json"
        )
        assert (
            result["observations_url"]
            == "https://www.bankofcanada.ca/valet/observations/group/FX_RATES_DAILY/json"
        )

    def test_members_starts_empty(self):
        """``members`` starts as an empty list (filled later by _resolve_group_members)."""
        result = generate_cache._normalize_boc_group_entry(
            "FX_RATES_DAILY", {"label": "", "description": "", "link": ""}
        )
        assert result["members"] == []


# ---------------------------------------------------------------------------
# _fetch_boc_list
# ---------------------------------------------------------------------------
class TestFetchBocList:
    """``_fetch_boc_list`` is the shared helper for both list endpoints."""

    def test_extracts_series_dict_from_payload(self, boc_series_list_sample):
        """A ``{"terms": ..., "series": {...}}`` payload yields the inner series dict."""
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            return_value=boc_series_list_sample,
        ):
            result = generate_cache._fetch_boc_list(
                "https://www.bankofcanada.ca/valet/lists/series/json", "series list"
            )
        assert "FXUSDCAD" in result
        assert "V39079" in result
        assert len(result) == 19  # 7 FX + 5 V390/CBC + 7 BD.CDN

    def test_extracts_groups_dict_from_payload(self, boc_groups_list_sample):
        """A ``{"terms": ..., "groups": {...}}`` payload yields the inner groups dict."""
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            return_value=boc_groups_list_sample,
        ):
            result = generate_cache._fetch_boc_list(
                "https://www.bankofcanada.ca/valet/lists/groups/json", "groups list"
            )
        assert "FX_RATES_DAILY" in result

    def test_raises_network_error_on_non_dict_payload(self):
        """A non-dict payload raises ``NetworkError``."""
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            return_value=["unexpected", "list"],
        ):
            with pytest.raises(NetworkError, match="not a dict"):
                generate_cache._fetch_boc_list("https://example.com", "test")

    def test_raises_network_error_when_inner_not_dict(self):
        """A payload with a non-dict inner field raises ``NetworkError``."""
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            return_value={"series": ["unexpected"]},
        ):
            with pytest.raises(NetworkError, match="inner payload is not a dict"):
                generate_cache._fetch_boc_list("https://example.com", "test")


# ---------------------------------------------------------------------------
# _resolve_group_members
# ---------------------------------------------------------------------------
class TestResolveGroupMembers:
    """``_resolve_group_members`` extracts the member list for a group."""

    def test_returns_sorted_member_list(self, boc_group_members_sample):
        """A successful call returns the member series names, sorted."""
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            return_value=boc_group_members_sample,
        ):
            members = generate_cache._resolve_group_members("FX_RATES_DAILY")
        # The fixture has 8 FX* members + the group itself (which we filter out).
        assert len(members) == 8
        assert "FXUSDCAD" in members
        assert "FXEURCAD" in members
        # Sorted alphabetically.
        assert members == sorted(members)
        # The group's own key is NOT in the member list.
        assert "FX_RATES_DAILY" not in members

    def test_returns_empty_list_on_network_failure(self):
        """A ``NetworkError`` is caught and returns an empty list."""
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            side_effect=NetworkError("https://...", "down"),
        ):
            members = generate_cache._resolve_group_members("FX_RATES_DAILY")
        assert members == []

    def test_returns_empty_list_for_unknown_group(self):
        """A group with no members returns an empty list (no error)."""
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            return_value={"groups": {}},
        ):
            members = generate_cache._resolve_group_members("UNKNOWN_GROUP")
        assert members == []


# ---------------------------------------------------------------------------
# _fetch_boc (the full BoC section builder)
# ---------------------------------------------------------------------------
class TestFetchBoc:
    """``_fetch_boc`` orchestrates the 3-step BoC fetch with graceful degradation."""

    def test_happy_path(
        self,
        boc_series_list_sample,
        boc_groups_list_sample,
        boc_group_members_sample,
    ):
        """All 3 calls succeed — full cache produced."""
        # The order of http_get_json calls in _fetch_boc is:
        # 1. /lists/series/json
        # 2. /lists/groups/json
        # 3. /groups/FX_RATES_DAILY/json
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            side_effect=[
                boc_series_list_sample,
                boc_groups_list_sample,
                boc_group_members_sample,
            ],
        ):
            result = generate_cache._fetch_boc()

        assert result["status"] == "ok"
        assert result["series_count"] == 19  # 7 FX + 5 V390/CBC + 7 BD.CDN
        assert result["groups_count"] == 1

        # Series are normalized with observations_url.
        usd = result["series"]["FXUSDCAD"]
        assert usd["label"] == "USD/CAD"
        assert (
            "Target for the overnight rate" in result["series"]["V39079"]["description"]
        )
        assert (
            usd["observations_url"]
            == "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json"
        )

        # Group has members resolved.
        group = result["groups"]["FX_RATES_DAILY"]
        assert "FXUSDCAD" in group["members"]
        assert len(group["members"]) == 8

    def test_series_list_failure_returns_degraded(self):
        """When the series list fails, the whole BoC section is degraded.

        Without the series list we can't verify anything exists, so
        there's nothing useful to cache. The degraded blob carries a
        ``warning`` so the Phase 5 fetcher can detect this.
        """
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            side_effect=NetworkError("https://...", "series list down"),
        ):
            result = generate_cache._fetch_boc()
        assert result["status"] == "degraded"
        assert result["series"] == {}
        assert result["groups"] == {}
        assert "warning" in result
        assert "series list down" in result["warning"]

    def test_groups_list_failure_keeps_series(
        self,
        boc_series_list_sample,
    ):
        """When the groups list fails, series are still cached.

        This is partial-success: we lose the ability to iterate group
        members, but individual series lookups still work. A
        ``warning`` field records the failure.
        """
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            side_effect=[
                boc_series_list_sample,  # series list OK
                NetworkError("https://...", "groups list down"),  # groups list fails
            ],
        ):
            result = generate_cache._fetch_boc()

        assert result["status"] == "ok"
        assert result["series_count"] == 19
        assert result["groups_count"] == 0  # groups empty
        assert "warning" in result
        assert "groups list unreachable" in result["warning"]

    def test_group_member_failure_keeps_group_entry(
        self,
        boc_series_list_sample,
        boc_groups_list_sample,
    ):
        """When member resolution fails, the group entry has empty ``members``."""
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            side_effect=[
                boc_series_list_sample,  # series list OK
                boc_groups_list_sample,  # groups list OK
                NetworkError("https://...", "members resolution down"),
            ],
        ):
            result = generate_cache._fetch_boc()

        assert result["status"] == "ok"
        assert result["groups_count"] == 1
        # Group entry exists but members is empty.
        group = result["groups"]["FX_RATES_DAILY"]
        assert group["members"] == []
        assert group["label"] == "Daily exchange rates"

    def test_missing_series_recorded(
        self,
        boc_groups_list_sample,
        boc_group_members_sample,
    ):
        """When a series-of-interest isn't in the catalog, it's recorded.

        The Phase 5 fetcher can check ``missing_series`` to give a clear
        error if asked for a series the BoC no longer publishes.
        """
        # Build a series list that's missing FXJPYCAD and BD.CDN.RRB.DQ.YLD
        # (which are in BOC_INDIVIDUAL_SERIES).
        full_sample = json.loads(
            json.dumps(json.load((_FIXTURE_DIR / "boc_series_list_sample.json").open()))
        )
        del full_sample["series"]["FXJPYCAD"]
        del full_sample["series"]["BD.CDN.RRB.DQ.YLD"]

        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            side_effect=[
                full_sample,
                boc_groups_list_sample,
                boc_group_members_sample,
            ],
        ):
            result = generate_cache._fetch_boc()

        assert result["status"] == "ok"
        assert "FXJPYCAD" in result["missing_series"]
        assert "BD.CDN.RRB.DQ.YLD" in result["missing_series"]
        # Series count reflects only what was actually cataloged.
        assert result["series_count"] == 17  # 19 - 2 missing

    def test_blob_has_valet_url(self, boc_series_list_sample):
        """The blob carries the Valet base URL for reference."""
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            side_effect=[
                boc_series_list_sample,
                NetworkError("https://...", "groups down"),
            ],
        ):
            result = generate_cache._fetch_boc()
        assert result["valet_url"] == "https://www.bankofcanada.ca/valet"


# ---------------------------------------------------------------------------
# Integration: full build_blob with both sections
# ---------------------------------------------------------------------------
class TestBuildBlobIntegration:
    """End-to-end ``build_blob`` with both BoC and StatsCan mocked."""

    @pytest.fixture(autouse=True)
    def _mock_statscan(self, monkeypatch):
        """Mock the StatsCan fetcher so ``build_blob`` doesn't hit the network."""
        monkeypatch.setattr(
            generate_cache,
            "_fetch_statscan",
            lambda: {
                "homepage_url": generate_cache.STATSCAN_HOMEPAGE_URL,
                "indicators": [],
                "geo_lookup": {},
                "themes_en": {},
                "themes_fr": {},
                "indicator_count": 0,
                "status": "ok",
            },
        )

    def test_build_blob_with_boc_success(
        self,
        monkeypatch,
        boc_series_list_sample,
        boc_groups_list_sample,
        boc_group_members_sample,
    ):
        """``build_blob`` with both sections succeeding produces a full cache."""
        # Replace _fetch_boc with a mock that returns a synthetic OK blob.
        monkeypatch.setattr(
            generate_cache,
            "_fetch_boc",
            lambda: {
                "valet_url": "https://www.bankofcanada.ca/valet",
                "series": {"FXUSDCAD": {"name": "FXUSDCAD"}},
                "groups": {},
                "series_count": 1,
                "groups_count": 0,
                "status": "ok",
            },
        )
        blob = generate_cache.build_blob()
        assert blob["boc"]["status"] == "ok"
        assert blob["statscan"]["status"] == "ok"

    def test_build_blob_with_both_degraded(self, monkeypatch):
        """When both sections fail, the blob still has the right shape."""
        monkeypatch.setattr(
            generate_cache,
            "_fetch_boc",
            lambda: {
                "valet_url": "https://www.bankofcanada.ca/valet",
                "series": {},
                "groups": {},
                "series_count": 0,
                "groups_count": 0,
                "status": "degraded",
                "warning": "boc down",
            },
        )
        monkeypatch.setattr(
            generate_cache,
            "_fetch_statscan",
            lambda: {
                "homepage_url": generate_cache.STATSCAN_HOMEPAGE_URL,
                "indicators": [],
                "geo_lookup": {},
                "indicator_count": 0,
                "status": "degraded",
                "warning": "statscan down",
            },
        )
        blob = generate_cache.build_blob()
        assert blob["boc"]["status"] == "degraded"
        assert blob["statscan"]["status"] == "degraded"
        assert "warning" in blob["boc"]
        assert "warning" in blob["statscan"]
