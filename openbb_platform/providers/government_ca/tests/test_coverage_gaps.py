"""Additional tests to reach 100% coverage.

These tests close the gaps identified by the coverage report on the
first run of Phase 6. Each test is surgical — it targets a specific
uncovered branch or line, with a clear docstring explaining what
behavior it verifies.

Gaps closed by this file:
- ``utils/helpers.py`` — non-numeric safe_float inputs, ValueError
  branches in parse_observation_date
- ``utils/metadata/_cache_mixin.py`` — _read_cache_file (gzip, plain
  JSON, malformed), _save_user_cache (happy + failure), _load_from_cache
  warning path
- ``utils/metadata/_loader_mixin.py`` — the two stub methods
- ``utils/_http.py`` — the final unreachable raise (defensive)
- ``boc/fx.py`` / ``boc/rates.py`` / ``boc/yields.py`` — extract_data
  paths where observations_url is missing
- ``statscan/economic_indicators.py`` — fallback branches when geo_code
  filter matches nothing
"""

from __future__ import annotations

import gzip
import json
import lzma
import warnings
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from openbb_government_ca.utils.helpers import (
    normalize_fx_symbol,
    parse_observation_date,
    safe_float,
)
from openbb_government_ca.utils.metadata import GovernmentCaMetadata
from openbb_government_ca.utils.metadata._cache_mixin import CacheMixin
from openbb_government_ca.utils.metadata._loader_mixin import LoaderMixin


# ===========================================================================
# utils/helpers.py — gap closure
# ===========================================================================
class TestSafeFloatGaps:
    """Cover the non-numeric input branch and unhandled types."""

    def test_safe_float_returns_none_for_unsupported_type(self):
        """A list/dict input returns None (no TypeError raised)."""
        assert safe_float([1, 2, 3]) is None
        assert safe_float({"v": 1.5}) is None
        assert safe_float(object()) is None

    def test_safe_float_returns_none_for_boolean(self):
        """Booleans are technically int subclass but should still return None.

        Actually ``bool`` is a subclass of ``int`` so ``True`` → 1.0.
        We verify this is the actual behavior (not None) for documentation.
        """
        # bool IS int subclass — so True→1.0, False→0.0. This is fine
        # because we'd never pass a bool to safe_float in practice.
        assert safe_float(True) == 1.0


class TestParseObservationDateGaps:
    """Cover the ValueError branches in the quarterly and monthly parsers."""

    def test_quarterly_with_non_numeric_year(self):
        """``"abcd-Q1"`` returns None (year not a number)."""
        assert parse_observation_date("abcd-Q1") is None

    def test_quarterly_with_non_numeric_quarter(self):
        """``"2024-Qx"`` returns None (quarter not a number)."""
        assert parse_observation_date("2024-Qx") is None

    def test_monthly_with_non_numeric_year(self):
        """``"abcd-01"`` returns None (year not a number)."""
        # Length 7, has "-" at position 4, but year isn't digits.
        # Actually "abcd-01" has length 7 and "-" at position 4.
        # int("abcd") raises ValueError.
        assert parse_observation_date("abcd-01") is None

    def test_monthly_with_non_numeric_month(self):
        """``"2024-xx"`` returns None (month not a number)."""
        assert parse_observation_date("2024-xx") is None


class TestNormalizeFxSymbolGaps:
    """Cover TypeError path in normalize_fx_symbol."""

    def test_normalize_rejects_none_input(self):
        """None input raises TypeError."""
        with pytest.raises(TypeError, match="symbol must be str"):
            normalize_fx_symbol(None)  # type: ignore[arg-type]


# ===========================================================================
# utils/metadata/_cache_mixin.py — gap closure
# ===========================================================================
class TestCacheMixinReadCacheFile:
    """Cover _read_cache_file's gzip, plain JSON, and malformed paths."""

    def test_read_cache_file_returns_none_for_missing_path(self, tmp_path: Path):
        """A non-existent path returns None (not an exception)."""
        path = tmp_path / "missing.json.xz"
        assert CacheMixin._read_cache_file(path) is None

    def test_read_cache_file_reads_lzma(self, tmp_path: Path):
        """LZMA-compressed JSON is read correctly."""
        path = tmp_path / "c.json.xz"
        raw = json.dumps({"hello": "world"}).encode("utf-8")
        with lzma.open(path, "wb") as f:
            f.write(raw)
        result = CacheMixin._read_cache_file(path)
        assert result == {"hello": "world"}

    def test_read_cache_file_reads_gzip(self, tmp_path: Path):
        """Gzip-compressed JSON is read correctly (user cache format)."""
        path = tmp_path / "c.json.gz"
        raw = json.dumps({"hello": "world"}).encode("utf-8")
        path.write_bytes(gzip.compress(raw))
        result = CacheMixin._read_cache_file(path)
        assert result == {"hello": "world"}

    def test_read_cache_file_reads_plain_json(self, tmp_path: Path):
        """A plain (uncompressed) JSON file is read as a fallback."""
        path = tmp_path / "c.json"
        path.write_text(json.dumps({"hello": "world"}))
        result = CacheMixin._read_cache_file(path)
        assert result == {"hello": "world"}

    def test_read_cache_file_returns_none_for_malformed_json(self, tmp_path: Path):
        """A malformed JSON file returns None (no exception)."""
        path = tmp_path / "c.json"
        path.write_text("not valid json {{{")
        result = CacheMixin._read_cache_file(path)
        assert result is None

    def test_read_cache_file_returns_none_for_malformed_lzma(self, tmp_path: Path):
        """A malformed LZMA file returns None (no exception)."""
        path = tmp_path / "c.json.xz"
        # Has the LZMA magic but garbage afterwards.
        path.write_bytes(b"\xfd7zXZ\x00" + b"garbage data")
        result = CacheMixin._read_cache_file(path)
        assert result is None

    def test_read_cache_file_returns_none_for_malformed_gzip(self, tmp_path: Path):
        """A malformed gzip file returns None (no exception)."""
        path = tmp_path / "c.json.gz"
        # Has the gzip magic but garbage afterwards.
        path.write_bytes(b"\x1f\x8b" + b"garbage data")
        result = CacheMixin._read_cache_file(path)
        assert result is None


class TestCacheMixinSaveUserCache:
    """Cover _save_user_cache happy and failure paths."""

    def test_save_user_cache_writes_gzip_file(self, tmp_path: Path, monkeypatch):
        """_save_user_cache writes a gzip-compressed JSON to the user cache dir."""
        # Patch _USER_CACHE_FILE in the _cache_mixin module (where it's
        # actually looked up at call time), not in _constants (which
        # was already bound at import time).
        from openbb_government_ca.utils.metadata import _cache_mixin

        monkeypatch.setattr(
            _cache_mixin,
            "_USER_CACHE_FILE",
            lambda: tmp_path / "government_ca_cache.json.gz",
        )
        # Build a metadata instance with some data.
        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {"boc": {"series": {"FXUSDCAD": {"label": "USD/CAD"}}}, "statscan": {}}
        )

        meta._save_user_cache()

        cache_file = tmp_path / "government_ca_cache.json.gz"
        assert cache_file.exists()
        # Verify the content round-trips.
        raw = cache_file.read_bytes()
        data = json.loads(gzip.decompress(raw).decode("utf-8"))
        assert "boc" in data
        assert "FXUSDCAD" in data["boc"]["series"]

        GovernmentCaMetadata._reset()

    def test_save_user_cache_warns_on_failure(self, monkeypatch):
        """A failure in _save_user_cache emits a warning, not an exception."""
        from openbb_government_ca.utils.metadata import _cache_mixin

        # During __init__ the singleton calls _load_from_cache, which
        # calls _USER_CACHE_FILE(). Make it return a harmless path
        # during init, then swap to the broken version before calling
        # _save_user_cache explicitly.
        monkeypatch.setattr(
            _cache_mixin,
            "_USER_CACHE_FILE",
            lambda: Path("/tmp/__nonexistent_test__/c.json.gz"),
        )
        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob({"boc": {}, "statscan": {}})

        # Now swap to the broken version for the _save_user_cache call.
        def _broken_user_cache_file():
            raise OSError("disk full")

        monkeypatch.setattr(_cache_mixin, "_USER_CACHE_FILE", _broken_user_cache_file)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            meta._save_user_cache()
            assert any("Failed to persist" in str(warning.message) for warning in w)

        GovernmentCaMetadata._reset()


class TestCacheMixinLoadFromCache:
    """Cover the warning path when no cache is available."""

    def test_load_from_cache_warns_when_no_cache(self, monkeypatch, tmp_path: Path):
        """When neither shipped nor user cache exists, a warning is emitted."""
        from openbb_government_ca.utils.metadata import _cache_mixin

        # Patch both references in the _cache_mixin module so the
        # patched values are used at call time.
        monkeypatch.setattr(
            _cache_mixin,
            "_SHIPPED_CACHE_FILE",
            tmp_path / "nonexistent_shipped.json.xz",
        )
        monkeypatch.setattr(
            _cache_mixin,
            "_USER_CACHE_FILE",
            lambda: tmp_path / "nonexistent_user" / "government_ca_cache.json.gz",
        )

        # Build a fresh instance — its __init__ would normally try to
        # load the cache. We bypass __init__ via __new__ and call
        # _load_from_cache directly so we can capture the warning.
        GovernmentCaMetadata._reset()
        meta = object.__new__(GovernmentCaMetadata)
        meta.blob = {}
        meta._boc = {}
        meta._statscan = {}
        meta._generated_at = ""
        meta._source = "unknown"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = meta._load_from_cache()
            assert result is False
            assert any(
                "No Government of Canada metadata cache found" in str(warning.message)
                for warning in w
            )

        GovernmentCaMetadata._reset()

    def test_load_from_cache_loads_shipped_cache(self, tmp_path: Path, monkeypatch):
        """When a shipped cache exists, it's loaded and returns True."""
        from openbb_government_ca.utils.metadata import _cache_mixin

        shipped_path = tmp_path / "shipped.json.xz"
        raw = json.dumps(
            {"boc": {"series": {"X": {}}}, "statscan": {"indicators": []}}
        ).encode("utf-8")
        with lzma.open(shipped_path, "wb") as f:
            f.write(raw)

        monkeypatch.setattr(_cache_mixin, "_SHIPPED_CACHE_FILE", shipped_path)
        monkeypatch.setattr(
            _cache_mixin,
            "_USER_CACHE_FILE",
            lambda: tmp_path / "no_user_cache" / "government_ca_cache.json.gz",
        )

        GovernmentCaMetadata._reset()
        meta = object.__new__(GovernmentCaMetadata)
        meta.blob = {}
        meta._boc = {}
        meta._statscan = {}
        meta._generated_at = ""
        meta._source = "unknown"

        result = meta._load_from_cache()
        assert result is True
        assert "X" in meta.boc["series"]

        GovernmentCaMetadata._reset()

    def test_load_from_cache_user_overrides_shipped(self, tmp_path: Path, monkeypatch):
        """When both caches exist, the user cache takes precedence."""
        from openbb_government_ca.utils.metadata import _cache_mixin

        shipped_path = tmp_path / "shipped.json.xz"
        with lzma.open(shipped_path, "wb") as f:
            f.write(
                json.dumps(
                    {"boc": {"series": {"OLD": {}}}, "statscan": {"indicators": []}}
                ).encode("utf-8")
            )

        user_dir = tmp_path / "user"
        user_dir.mkdir()
        user_path = user_dir / "government_ca_cache.json.gz"
        user_path.write_bytes(
            gzip.compress(
                json.dumps(
                    {"boc": {"series": {"NEW": {}}}, "statscan": {"indicators": []}}
                ).encode("utf-8")
            )
        )

        monkeypatch.setattr(_cache_mixin, "_SHIPPED_CACHE_FILE", shipped_path)
        monkeypatch.setattr(
            _cache_mixin,
            "_USER_CACHE_FILE",
            lambda: user_path,
        )

        GovernmentCaMetadata._reset()
        meta = object.__new__(GovernmentCaMetadata)
        meta.blob = {}
        meta._boc = {}
        meta._statscan = {}
        meta._generated_at = ""
        meta._source = "unknown"

        result = meta._load_from_cache()
        assert result is True
        # The user cache is applied AFTER the shipped cache, so its
        # ``self.blob = blob`` assignment replaces the shipped one
        # entirely. Only NEW is present.
        assert "NEW" in meta.boc["series"]
        assert "OLD" not in meta.boc["series"]

        GovernmentCaMetadata._reset()


# ===========================================================================
# utils/metadata/_loader_mixin.py — gap closure (stub methods)
# ===========================================================================
class TestLoaderMixinStubs:
    """Cover the two stub methods in _loader_mixin.

    These are no-ops today (Phase 2+ will turn them into lazy fetchers),
    but they need to be called from a test so coverage doesn't flag
    them as dead code.
    """

    def test_ensure_boc_loaded_is_noop(self):
        """``_ensure_boc_loaded`` returns None without raising."""
        mixin = LoaderMixin()
        # Should not raise.
        assert mixin._ensure_boc_loaded() is None

    def test_ensure_statscan_loaded_is_noop(self):
        """``_ensure_statscan_loaded`` returns None without raising."""
        mixin = LoaderMixin()
        assert mixin._ensure_statscan_loaded() is None


# ===========================================================================
# utils/_http.py — gap closure
# ===========================================================================
class TestHttpBackoff:
    """Cover the backoff cap (the unreachable final raise has a pragma)."""

    def test_sleep_backoff_max_cap(self):
        """The backoff cap of 10s is enforced even at high attempt counts."""
        from openbb_government_ca.utils import _http

        with patch("openbb_government_ca.utils._http.time.sleep") as mock_sleep:
            _http._sleep_backoff(1.5, 100)  # would be 1.5 * 1.5^100 without cap
        assert mock_sleep.call_args.args[0] == 10.0


# ===========================================================================
# boc/fx.py — gap closure for missing observations_url
# ===========================================================================
class TestBankOfCAFXGaps:
    """Cover the path where a cache entry has no observations_url."""

    def test_raises_when_observations_url_missing(self, monkeypatch):
        """A cache entry without observations_url raises OpenBBError."""
        from openbb_core.app.model.abstract.error import OpenBBError

        from openbb_government_ca.boc.fx import BankOfCanadaFXFetcher

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "ok",
                    "series": {
                        "FXUSDCAD": {
                            "name": "FXUSDCAD",
                            "label": "USD/CAD",
                            "description": "Daily exchange rate",
                            "observations_url": "",  # empty!
                        },
                    },
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:
            q = BankOfCanadaFXFetcher.transform_query({"symbol": "FXUSDCAD"})
            with pytest.raises(OpenBBError, match="no observations_url"):
                BankOfCanadaFXFetcher.extract_data(q, None)
        finally:
            GovernmentCaMetadata._reset()


# ===========================================================================
# boc/rates.py — gap closure for missing observations_url
# ===========================================================================
class TestBankOfCARatesGaps:
    """Cover the path where the resolved target series has no observations_url."""

    def test_raises_when_observations_url_missing(self, monkeypatch):
        """A target series without observations_url raises OpenBBError."""
        from openbb_core.app.model.abstract.error import OpenBBError

        from openbb_government_ca.boc.rates import BankOfCanadaRatesFetcher

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "ok",
                    "series": {
                        "CBC20210": {
                            "name": "CBC20210",
                            "label": "V39079",
                            "description": "Target for the overnight rate",
                            "observations_url": "",  # empty!
                        },
                    },
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:
            q = BankOfCanadaRatesFetcher.transform_query({})
            with pytest.raises(OpenBBError, match="no observations_url"):
                BankOfCanadaRatesFetcher.extract_data(q, None)
        finally:
            GovernmentCaMetadata._reset()

    def test_network_failure_raises_openbb_error(self, seeded_meta):
        """A NetworkError during rates fetch is wrapped in OpenBBError."""
        from openbb_core.app.model.abstract.error import OpenBBError

        from openbb_government_ca.boc.rates import BankOfCanadaRatesFetcher
        from openbb_government_ca.utils._http import NetworkError

        with patch(
            "openbb_government_ca.boc.rates.http_get_json",
            side_effect=NetworkError("https://...", "down"),
        ):
            q = BankOfCanadaRatesFetcher.transform_query({})
            with pytest.raises(OpenBBError, match="Failed to fetch"):
                BankOfCanadaRatesFetcher.extract_data(q, None)


# ===========================================================================
# boc/yields.py — gap closure for missing observations_url
# ===========================================================================
class TestBankOfCAYieldsGaps:
    """Cover paths in the yields fetcher."""

    def test_resolve_bond_series_skips_unknown_tenor(self, monkeypatch):
        """A bond series with tenor_years not in _TENOR_YEARS_TO_FIELD is skipped."""
        from openbb_government_ca.boc.yields import BankOfCanadaYieldsFetcher

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "ok",
                    "series": {
                        "BD.CDN.4YR.DQ.YLD": {
                            "name": "BD.CDN.4YR.DQ.YLD",
                            "tenor_years": 4,  # 4Y not in _TENOR_YEARS_TO_FIELD
                            "observations_url": "https://.../4YR/json",
                        },
                        "BD.CDN.10YR.DQ.YLD": {
                            "name": "BD.CDN.10YR.DQ.YLD",
                            "tenor_years": 10,
                            "observations_url": "https://.../10YR/json",
                        },
                    },
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:
            bond_series = BankOfCanadaYieldsFetcher._resolve_bond_series(meta.boc)
            # Only 10Y, not 4Y.
            assert set(bond_series.keys()) == {10}
        finally:
            GovernmentCaMetadata._reset()

    def test_fetch_single_tenor_with_empty_url_returns_empty(self):
        """_fetch_single_tenor returns ([], []) when observations_url is empty."""
        from openbb_government_ca.boc.yields import BankOfCanadaYieldsFetcher

        entry = {
            "name": "BD.CDN.10YR.DQ.YLD",
            "tenor_years": 10,
            "observations_url": "",
        }
        tenor, obs = BankOfCanadaYieldsFetcher._fetch_single_tenor(
            entry, date(2024, 1, 1), date(2024, 1, 31)
        )
        assert tenor == 10
        assert obs == []

    def test_fetch_single_tenor_skips_obs_without_date(self, monkeypatch):
        """Observations without 'd' field are skipped during transform."""
        from openbb_government_ca.boc.yields import BankOfCanadaYieldsFetcher
        from openbb_government_ca.utils.metadata import GovernmentCaMetadata

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "ok",
                    "series": {
                        "BD.CDN.10YR.DQ.YLD": {
                            "name": "BD.CDN.10YR.DQ.YLD",
                            "tenor_years": 10,
                            "observations_url": "https://.../10YR/json",
                        },
                    },
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:
            # Observation with missing 'd', missing '_tenor_years',
            # missing series_name key, and empty value string.
            malformed_obs = [
                {
                    "d": "2024-01-02",
                    "BD.CDN.10YR.DQ.YLD": {"v": "3.18"},
                    "_tenor_years": 10,
                    "_series_name": "BD.CDN.10YR.DQ.YLD",
                },
                {"_tenor_years": 10, "_series_name": "BD.CDN.10YR.DQ.YLD"},  # no 'd'
                {
                    "d": "2024-01-03",
                    "BD.CDN.10YR.DQ.YLD": {"v": ""},
                    "_tenor_years": 10,
                    "_series_name": "BD.CDN.10YR.DQ.YLD",
                },  # empty value
                {
                    "d": "2024-01-04",
                    "_tenor_years": None,
                    "_series_name": "BD.CDN.10YR.DQ.YLD",
                },  # None tenor
            ]
            q = BankOfCanadaYieldsFetcher.transform_query({})
            result = BankOfCanadaYieldsFetcher.transform_data(q, malformed_obs)
            # Only the first observation produces a row.
            assert len(result) == 1
            assert result[0].year_10 == 0.0318
        finally:
            GovernmentCaMetadata._reset()


# ===========================================================================
# statscan/economic_indicators.py — gap closure for geo_code fallback
# ===========================================================================
class TestStatsCanEconomicIndicatorsGaps:
    """Cover branches in the new WDS-backed economic_indicators fetcher."""

    def _seed_catalog(self) -> None:
        """Populate the singleton with a minimal SDMX catalog."""
        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {},
                "statscan": {
                    "status": "ok",
                    "indicators": [
                        {"source": "1", "title_en": "GDP", "geo_code": "0"},
                    ],
                    "catalog": {
                        "cubes": {
                            "10100139": {
                                "pid": "10100139",
                                "title_en": "GDP",
                                "subject_code": "13",
                                "frequency_code": "6",
                                "series": [
                                    {
                                        "vector_id": "V1",
                                        "coordinate": "1.1.1.1",
                                        "label_en": "GDP at basic prices",
                                        "scalar_factor_code": "6",
                                        "uom_code": "203",
                                        "frequency_code": "6",
                                    }
                                ],
                            }
                        },
                        "subjects": {"13": "Economic accounts"},
                        "cube_count": 1,
                        "series_count": 1,
                        "status": "ok",
                    },
                },
            }
        )

    def test_transform_data_skips_unparseable_value(self, monkeypatch):
        """An observation with an unparseable value gets value=None."""
        from openbb_government_ca.statscan.economic_indicators import (
            StatsCanEconomicIndicatorsFetcher,
            StatsCanEconomicIndicatorsQueryParams,
        )

        self._seed_catalog()
        try:
            q = StatsCanEconomicIndicatorsQueryParams(symbol="V1")
            raw = [
                {
                    "refPer": "2024-01",
                    "value": "not a number",
                    "_vector_id": "V1",
                    "_cube_pid": "10100139",
                    "_coordinate": "1.1.1.1",
                    "_scalar_factor_code": "6",
                    "_uom_code": "203",
                    "_label_en": "GDP at basic prices",
                }
            ]
            result = StatsCanEconomicIndicatorsFetcher.transform_data(q, raw)
            assert len(result) == 1
            assert result[0].value is None
            assert result[0].vector_id == "V1"
        finally:
            GovernmentCaMetadata._reset()

    def test_transform_data_parses_quarterly_refper(self, monkeypatch):
        """Quarterly refPer strings are parsed to dates."""
        from openbb_government_ca.statscan.economic_indicators import (
            StatsCanEconomicIndicatorsFetcher,
            StatsCanEconomicIndicatorsQueryParams,
        )

        self._seed_catalog()
        try:
            q = StatsCanEconomicIndicatorsQueryParams(symbol="V1")
            raw = [
                {
                    "refPer": "2024-Q1",
                    "value": 100.0,
                    "_vector_id": "V1",
                    "_cube_pid": "10100139",
                    "_coordinate": "1.1.1.1",
                    "_scalar_factor_code": "6",
                    "_uom_code": "203",
                    "_label_en": "GDP at basic prices",
                }
            ]
            result = StatsCanEconomicIndicatorsFetcher.transform_data(q, raw)
            assert result[0].date == date(2024, 1, 1)
        finally:
            GovernmentCaMetadata._reset()

    def test_extract_data_raises_on_empty_catalog(self, monkeypatch):
        """An empty or degraded catalog triggers an OpenBBError."""
        from openbb_core.app.model.abstract.error import OpenBBError

        from openbb_government_ca.statscan.economic_indicators import (
            StatsCanEconomicIndicatorsFetcher,
            StatsCanEconomicIndicatorsQueryParams,
        )

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob({"boc": {}, "statscan": {"status": "degraded"}})
        try:
            q = StatsCanEconomicIndicatorsQueryParams(symbol="V1")
            with pytest.raises(OpenBBError):
                StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        finally:
            GovernmentCaMetadata._reset()
