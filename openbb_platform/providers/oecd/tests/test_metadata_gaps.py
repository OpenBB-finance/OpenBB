"""Gap-fill tests for the small remaining branches in metadata helpers."""

from __future__ import annotations

import gzip
import json
import lzma
import threading
import warnings
from unittest.mock import patch

import pytest

from openbb_oecd.utils.metadata import OecdMetadata
from openbb_oecd.utils.metadata._cache_mixin import CacheMixin
from openbb_oecd.utils.metadata._helpers import (
    _extract_codelist_id_from_urn,
    _get_user_cache_file,
)


class TestGetUserCacheFile:
    """Branches in ``_get_user_cache_file``."""

    def test_uses_openbb_core_directory(self, tmp_path):
        with patch(
            "openbb_core.app.utils.get_user_cache_directory",
            return_value=str(tmp_path),
        ):
            path = _get_user_cache_file()
        assert path == tmp_path / "oecd_cache.json.gz"

    def test_fallback_when_core_helper_raises(self):
        with patch(
            "openbb_core.app.utils.get_user_cache_directory",
            side_effect=RuntimeError("no core"),
        ):
            path = _get_user_cache_file()
        assert path.name == "oecd_cache.json.gz"
        assert ".openbb_platform" in str(path)


class TestExtractCodelistIdFromUrnRegexFallback:
    """The ``match2`` fallback when the full ``=...`` form is absent."""

    def test_partial_urn_matched_by_second_regex(self):
        result = _extract_codelist_id_from_urn("prefix:CL_FREQ(1.0)")
        assert result == "CL_FREQ"


class TestSingletonRaceGuard:
    """The second-thread ``_initialized`` check inside ``__init__``."""

    def test_init_returns_early_when_already_initialized(self, monkeypatch):
        OecdMetadata._reset()
        monkeypatch.setattr(OecdMetadata, "_load_from_cache", lambda self: True)
        first = OecdMetadata()
        first._token = "sentinel"  # noqa: S105
        OecdMetadata()
        assert first._token == "sentinel"  # noqa: S105
        OecdMetadata._reset()

    def test_call_returns_self(self, monkeypatch):
        OecdMetadata._reset()
        monkeypatch.setattr(OecdMetadata, "_load_from_cache", lambda self: True)
        inst = OecdMetadata()
        assert inst() is inst
        OecdMetadata._reset()


class _MiniCache(CacheMixin):
    """Tiny subclass for exercising raw CacheMixin methods in isolation."""

    def __init__(self):
        self.dataflows = {}
        self.datastructures = {}
        self.codelists = {}
        self._codelist_descriptions = {}
        self._codelist_parents = {}
        self._codelist_comp_rules = {}
        self._dataflow_constraints = {}
        self._table_map = {}
        self._dataflow_parameters_cache = {}
        self._dataflow_indicators_cache = {}
        self._short_id_map = {}
        self._taxonomy_tree = []
        self._df_to_categories = {}
        self._category_to_dfs = {}
        self._category_names = {}
        self._taxonomy_loaded = False
        self._cache_dirty = False
        self._codelist_lock = threading.Lock()
        self._full_catalogue_loaded = False


class TestReadCacheFile:
    """Coverage for ``CacheMixin._read_cache_file`` branches."""

    def test_returns_none_when_missing(self, tmp_path):
        assert CacheMixin._read_cache_file(tmp_path / "absent.gz") is None

    def test_returns_none_when_decompress_fails(self, tmp_path):
        bad = tmp_path / "bad.gz"
        bad.write_bytes(b"not gzipped data")
        assert CacheMixin._read_cache_file(bad) is None

    def test_reads_gzipped_json(self, tmp_path):
        target = tmp_path / "ok.gz"
        target.write_bytes(gzip.compress(json.dumps({"k": "v"}).encode()))
        assert CacheMixin._read_cache_file(target) == {"k": "v"}

    def test_reads_lzma_json(self, tmp_path):
        target = tmp_path / "ok.xz"
        target.write_bytes(lzma.compress(json.dumps({"k": "lz"}).encode()))
        assert CacheMixin._read_cache_file(target) == {"k": "lz"}


class TestApplyBlobParameters:
    """Parameter cache only stores truthy values."""

    def test_truthy_parameters_stored(self):
        mc = _MiniCache()
        mc._apply_blob({"dataflow_parameters": {"DF_A": {"REF_AREA": ["USA"]}}})
        assert mc._dataflow_parameters_cache == {"DF_A": {"REF_AREA": ["USA"]}}

    def test_empty_parameters_skipped(self):
        mc = _MiniCache()
        mc._apply_blob({"dataflow_parameters": {"DF_A": {}}})
        assert mc._dataflow_parameters_cache == {}

    def test_seen_indicator_codes_deduplicated(self):
        mc = _MiniCache()
        mc.dataflows["DSD@DF"] = {"short_id": "DF", "name": "Name"}
        mc._apply_blob(
            {
                "dataflow_indicators": {
                    "DSD@DF": {
                        "dims": [
                            {
                                "dim_id": "MEASURE",
                                "codes": [
                                    {"indicator": "X", "label": "X label"},
                                    {"indicator": "X", "label": "duplicate"},
                                ],
                            }
                        ]
                    }
                }
            }
        )
        cached = mc._dataflow_indicators_cache["DSD@DF"]
        assert len(cached) == 1

    def test_parent_propagated_in_dims_indicators(self):
        mc = _MiniCache()
        mc.dataflows["DSD@DF"] = {"short_id": "DF", "name": "Name"}
        mc._apply_blob(
            {
                "dataflow_indicators": {
                    "DSD@DF": {
                        "dims": [
                            {
                                "dim_id": "MEASURE",
                                "codes": [
                                    {
                                        "indicator": "Y",
                                        "label": "child",
                                        "parent": "P",
                                    },
                                ],
                            }
                        ]
                    }
                }
            }
        )
        assert mc._dataflow_indicators_cache["DSD@DF"][0]["parent"] == "P"

    def test_parent_propagated_in_codes_indicators(self):
        mc = _MiniCache()
        mc.dataflows["DSD@DF"] = {"short_id": "DF", "name": "Name"}
        mc._apply_blob(
            {
                "dataflow_indicators": {
                    "DSD@DF": {
                        "dim_id": "MEASURE",
                        "codes": [
                            {"indicator": "X", "label": "x"},
                            {"indicator": "Y", "label": "y", "parent": "X"},
                        ],
                    }
                }
            }
        )
        cached = mc._dataflow_indicators_cache["DSD@DF"]
        with_parent = next(c for c in cached if c["indicator"] == "Y")
        assert with_parent["parent"] == "X"

    def test_passthrough_indicator_payload_kept_verbatim(self):
        mc = _MiniCache()
        mc._apply_blob({"dataflow_indicators": {"DSD@DF": ["pre-expanded"]}})
        assert mc._dataflow_indicators_cache["DSD@DF"] == ["pre-expanded"]


class TestInferOrphanParents:
    """``_infer_orphan_parents`` derives ancestors from COMP_RULE annotations."""

    def test_orphan_gets_common_ancestor(self):
        mc = _MiniCache()
        mc._codelist_parents["CL"] = {"A": "P", "B": "P"}
        mc._codelist_comp_rules["CL"] = {"AGG": "A + B"}
        mc._apply_blob({})
        assert mc._codelist_parents["CL"]["AGG"] == "P"

    def test_skips_when_no_components(self):
        mc = _MiniCache()
        mc._codelist_parents["CL"] = {"A": "P"}
        mc._codelist_comp_rules["CL"] = {"X": "   "}
        mc._apply_blob({})
        assert "X" not in mc._codelist_parents["CL"]

    def test_skips_when_no_codelist_parents(self):
        mc = _MiniCache()
        mc._codelist_comp_rules["CL"] = {"X": "A + B"}
        mc._apply_blob({})
        assert mc._codelist_parents == {}

    def test_skips_when_code_already_has_parent(self):
        mc = _MiniCache()
        mc._codelist_parents["CL"] = {"X": "Existing", "A": "P", "B": "P"}
        mc._codelist_comp_rules["CL"] = {"X": "A + B"}
        mc._apply_blob({})
        assert mc._codelist_parents["CL"]["X"] == "Existing"


class TestClosestCommonAncestorEdges:
    """Empty input + empty chain branches."""

    def test_empty_codes_returns_none(self):
        assert CacheMixin._closest_common_ancestor([], {"A": "B"}) is None

    def test_no_chains_returns_none(self):
        # Codes with no parent mapping at all → empty chains for every code.
        assert CacheMixin._closest_common_ancestor(["A", "B"], {}) is None


class TestLoadFromCache:
    """Branches in ``_load_from_cache``."""

    def test_warns_when_no_cache_present(self, tmp_path, monkeypatch):
        mc = _MiniCache()
        monkeypatch.setattr(
            "openbb_oecd.utils.metadata._cache_mixin._SHIPPED_CACHE_FILE",
            tmp_path / "absent.gz",
        )
        monkeypatch.setattr(
            "openbb_oecd.utils.metadata._cache_mixin._get_user_cache_file",
            lambda: tmp_path / "also_absent.gz",
        )
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            assert mc._load_from_cache() is False
        assert any("No OECD metadata cache" in str(w.message) for w in caught)

    def test_user_cache_overlay(self, tmp_path, monkeypatch):
        mc = _MiniCache()
        shipped_blob = {"dataflows": {"S@DS": {"short_id": "DS", "name": "ship"}}}
        user_blob = {"dataflows": {"U@DU": {"short_id": "DU", "name": "user"}}}
        shipped = tmp_path / "ship.gz"
        user = tmp_path / "user.gz"
        shipped.write_bytes(gzip.compress(json.dumps(shipped_blob).encode()))
        user.write_bytes(gzip.compress(json.dumps(user_blob).encode()))
        monkeypatch.setattr(
            "openbb_oecd.utils.metadata._cache_mixin._SHIPPED_CACHE_FILE", shipped
        )
        monkeypatch.setattr(
            "openbb_oecd.utils.metadata._cache_mixin._get_user_cache_file",
            lambda: user,
        )
        monkeypatch.setattr(_MiniCache, "_rebuild_short_id_map", lambda self: None)
        assert mc._load_from_cache() is True
        assert "S@DS" in mc.dataflows
        assert "U@DU" in mc.dataflows

    def test_rebuilds_short_id_map_when_missing(self, tmp_path, monkeypatch):
        mc = _MiniCache()
        blob = {
            "dataflows": {"DSD@DF": {"short_id": "DF", "name": "X"}},
        }
        target = tmp_path / "shipped.gz"
        target.write_bytes(gzip.compress(json.dumps(blob).encode()))
        monkeypatch.setattr(
            "openbb_oecd.utils.metadata._cache_mixin._SHIPPED_CACHE_FILE", target
        )
        monkeypatch.setattr(
            "openbb_oecd.utils.metadata._cache_mixin._get_user_cache_file",
            lambda: tmp_path / "absent.gz",
        )

        called: dict[str, bool] = {}

        def _stub_rebuild(self):
            called["yes"] = True

        monkeypatch.setattr(_MiniCache, "_rebuild_short_id_map", _stub_rebuild)
        assert mc._load_from_cache() is True
        assert called == {"yes": True}
        assert mc._full_catalogue_loaded is True


class TestSaveCache:
    """Branches in ``_save_cache``."""

    def test_no_op_when_not_dirty(self, monkeypatch):
        mc = _MiniCache()
        mc._cache_dirty = False
        monkeypatch.setattr(
            "openbb_oecd.utils.metadata._cache_mixin._get_user_cache_file",
            lambda: (_ for _ in ()).throw(AssertionError("should not be called")),
        )
        mc._save_cache()

    def test_writes_to_user_cache(self, tmp_path, monkeypatch):
        mc = _MiniCache()
        mc.dataflows["DSD@DF"] = {"short_id": "DF"}
        mc._cache_dirty = True
        target = tmp_path / "u" / "cache.gz"
        monkeypatch.setattr(
            "openbb_oecd.utils.metadata._cache_mixin._get_user_cache_file",
            lambda: target,
        )
        mc._save_cache()
        assert target.exists()
        assert mc._cache_dirty is False
        decoded = json.loads(gzip.decompress(target.read_bytes()))
        assert "DSD@DF" in decoded["dataflows"]

    def test_warns_when_write_fails(self, monkeypatch):
        mc = _MiniCache()
        mc._cache_dirty = True

        class _BadPath:
            @property
            def parent(self):
                raise OSError("read-only filesystem")

        monkeypatch.setattr(
            "openbb_oecd.utils.metadata._cache_mixin._get_user_cache_file",
            _BadPath,
        )
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            mc._save_cache()
        assert any("Failed to persist" in str(w.message) for w in caught)


@pytest.mark.parametrize(
    "ancestor_codes,parents,expected",
    [
        (["A", "B"], {"A": "P", "B": "P"}, "P"),
        (["A"], {"A": "P", "P": "G"}, "P"),
    ],
)
def test_closest_common_ancestor_resolved(ancestor_codes, parents, expected):
    assert CacheMixin._closest_common_ancestor(ancestor_codes, parents) == expected
