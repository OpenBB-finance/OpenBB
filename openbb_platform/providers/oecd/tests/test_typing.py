"""Tests for the _MixinBase typing scaffold."""

from __future__ import annotations

from pathlib import Path

import pytest

from openbb_oecd.utils.metadata._typing import _MixinBase


@pytest.fixture
def base() -> _MixinBase:
    """Return a bare _MixinBase instance with no mixins layered on top."""
    return _MixinBase()


class TestMixinBaseStubs:
    """Every stub method raises NotImplementedError when called directly."""

    def test_read_cache_file(self):
        with pytest.raises(NotImplementedError):
            _MixinBase._read_cache_file(Path("/tmp/x"))

    def test_apply_blob(self, base):
        with pytest.raises(NotImplementedError):
            base._apply_blob({})

    def test_infer_orphan_parents(self, base):
        with pytest.raises(NotImplementedError):
            base._infer_orphan_parents()

    def test_closest_common_ancestor(self):
        with pytest.raises(NotImplementedError):
            _MixinBase._closest_common_ancestor(["A"], {"A": "B"})

    def test_load_from_cache(self, base):
        with pytest.raises(NotImplementedError):
            base._load_from_cache()

    def test_save_cache(self, base):
        with pytest.raises(NotImplementedError):
            base._save_cache()

    def test_ensure_dataflows(self, base):
        with pytest.raises(NotImplementedError):
            base._ensure_dataflows()

    def test_rebuild_short_id_map(self, base):
        with pytest.raises(NotImplementedError):
            base._rebuild_short_id_map()

    def test_ensure_taxonomy(self, base):
        with pytest.raises(NotImplementedError):
            base._ensure_taxonomy()

    def test_resolve_dataflow_id(self, base):
        with pytest.raises(NotImplementedError):
            base._resolve_dataflow_id("DF_X")

    def test_ensure_description(self, base):
        with pytest.raises(NotImplementedError):
            base._ensure_description("DSD_X@DF_X")

    def test_ensure_structure(self, base):
        with pytest.raises(NotImplementedError):
            base._ensure_structure("DF_X")

    def test_list_dataflows(self, base):
        with pytest.raises(NotImplementedError):
            base.list_dataflows()

    def test_get_dataflow_parameters(self, base):
        with pytest.raises(NotImplementedError):
            base.get_dataflow_parameters("DF_X")

    def test_get_dimension_order(self, base):
        with pytest.raises(NotImplementedError):
            base.get_dimension_order("DF_X")

    def test_get_dimension_info(self, base):
        with pytest.raises(NotImplementedError):
            base.get_dimension_info("DF_X")

    def test_get_table_groups(self, base):
        with pytest.raises(NotImplementedError):
            base.get_table_groups("DF_X")

    def test_get_constrained_values(self, base):
        with pytest.raises(NotImplementedError):
            base.get_constrained_values("DF_X")

    def test_table_map(self, base):
        with pytest.raises(NotImplementedError):
            base.table_map()

    def test_find_tables(self, base):
        with pytest.raises(NotImplementedError):
            base.find_tables("query")

    def test_get_codelist(self, base):
        with pytest.raises(NotImplementedError):
            base._get_codelist("CL_X")

    def test_get_indicator_dim(self, base):
        with pytest.raises(NotImplementedError):
            base._get_indicator_dim("DSD_X@DF_X")

    def test_find_indicator_dimension(self, base):
        with pytest.raises(NotImplementedError):
            base._find_indicator_dimension("DF_X")

    def test_get_codelist_for_dimension(self, base):
        with pytest.raises(NotImplementedError):
            base.get_codelist_for_dimension("DF_X", "DIM")

    def test_get_indicator_tree(self, base):
        with pytest.raises(NotImplementedError):
            base.get_indicator_tree("DF_X")

    def test_describe_dataflow(self, base):
        with pytest.raises(NotImplementedError):
            base.describe_dataflow("DF_X")

    def test_fetch_availability(self, base):
        with pytest.raises(NotImplementedError):
            base.fetch_availability("DF_X")
