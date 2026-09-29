"""Coverage tests for openbb_oecd.utils.table_builder."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.provider.utils.errors import OpenBBError

from openbb_oecd.utils.table_builder import OecdTableBuilder, _calculate_depth

_FULL_ID = "DSD_TEST@DF_TEST"
_SHORT_ID = "DF_TEST"


def _qb_stub(meta):
    """Return a query_builder stub with required methods on it."""
    qb = MagicMock()
    qb.metadata = meta
    qb.get_country_dimension.return_value = "REF_AREA"
    qb.get_frequency_dimension.return_value = "FREQ"
    qb.validate_dimension_constraints.return_value = None
    qb.fetch_data.return_value = {
        "data": [],
        "metadata": {"url": "http://example/data"},
    }
    return qb


def _seed_hierarchy(meta, indicators):
    """Stash a fake structure response on meta for get_dataflow_table_structure."""
    meta._stub_hierarchy = indicators


def _patch_meta(meta, monkeypatch, **overrides):
    """Patch metadata methods used by table_builder to deterministic stubs."""
    defaults = {
        "_resolve_dataflow_id": lambda did: _FULL_ID,
        "_detect_section_families": lambda: {},
        "_ensure_structure": lambda full_id: None,
        "get_dataflow_hierarchies": lambda did: [],
        "get_dataflow_table_structure": lambda did, tid: {
            "hierarchy_name": "Test Hierarchy",
            "indicators": [],
        },
        "_find_indicator_dimension": lambda did: "MEASURE",
        "resolve_country_codes": lambda did, raw: [],
        "fetch_availability": lambda did, pinned=None: {},
    }
    defaults.update(overrides)
    for name, fn in defaults.items():
        monkeypatch.setattr(meta, name, fn)


class TestCalculateDepth:
    """_calculate_depth pure utility."""

    def test_root_no_parent(self):
        """A node without a parent returns depth 0."""
        node = {"code": "A", "parent": None}
        assert _calculate_depth(node, {"A": node}) == 0

    def test_single_parent(self):
        """A child of a root has depth 1."""
        root = {"code": "P", "parent": None}
        child = {"code": "C", "parent": "P"}
        by_code = {"P": root, "C": child}
        assert _calculate_depth(child, by_code) == 1

    def test_multi_level(self):
        """Three-level chain returns depth 2 for leaf."""
        a = {"code": "A", "parent": None}
        b = {"code": "B", "parent": "A"}
        c = {"code": "C", "parent": "B"}
        by_code = {"A": a, "B": b, "C": c}
        assert _calculate_depth(c, by_code) == 2

    def test_missing_code_returns_zero(self):
        """Nodes without 'code' short-circuit to zero."""
        assert _calculate_depth({"code": ""}, {}) == 0

    def test_parent_not_in_map_returns_zero(self):
        """Unknown parent references stop the recursion."""
        node = {"code": "C", "parent": "MISSING"}
        assert _calculate_depth(node, {"C": node}) == 0

    def test_cycle_protection(self):
        """Visiting a previously-seen code short-circuits the recursion."""
        a = {"code": "A", "parent": "B"}
        b = {"code": "B", "parent": "A"}
        by_code = {"A": a, "B": b}
        assert _calculate_depth(a, by_code) <= 2


class TestInitDefaults:
    """OecdTableBuilder() default construction wires real instances."""

    def test_defaults_create_real_singletons(self, seeded_meta):
        """When metadata/query_builder are omitted, factories run."""
        tb = OecdTableBuilder()
        assert tb.metadata is not None
        assert tb.query_builder is not None

    def test_explicit_injection(self, seeded_meta):
        """Provided instances are used verbatim."""
        qb = _qb_stub(seeded_meta)
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        assert tb.metadata is seeded_meta
        assert tb.query_builder is qb


class TestGetTableArgumentHandling:
    """get_table argument parsing and dispatch."""

    def test_combined_table_id_splits_dataflow(self, seeded_meta, monkeypatch):
        """'DF::TID' parses cleanly when no dataflow argument given."""
        _patch_meta(seeded_meta, monkeypatch)
        qb = _qb_stub(seeded_meta)
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        with pytest.raises(OpenBBError, match="No indicators match"):
            tb.get_table(table_id="DF_TEST::T1")

    def test_combined_table_id_mismatch_raises(self, seeded_meta, monkeypatch):
        """Mismatched dataflow + parsed dataflow surfaces clear error."""
        _patch_meta(seeded_meta, monkeypatch)
        qb = _qb_stub(seeded_meta)
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        with pytest.raises(OpenBBError, match="Dataflow mismatch"):
            tb.get_table(dataflow="OTHER", table_id="DF_TEST::T1")

    def test_bare_table_id_promoted_to_dataflow(self, seeded_meta, monkeypatch):
        """Bare table_id with no dataflow becomes the dataflow value."""
        captured: dict = {}

        def _resolve(did):
            captured["did"] = did
            return _FULL_ID

        _patch_meta(seeded_meta, monkeypatch, _resolve_dataflow_id=_resolve)
        qb = _qb_stub(seeded_meta)
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        with pytest.raises(OpenBBError, match="No indicators match"):
            tb.get_table(table_id="DF_TEST")
        assert captured["did"] == "DF_TEST"

    def test_missing_dataflow_raises(self, seeded_meta, monkeypatch):
        """Both dataflow and table_id omitted is an error."""
        _patch_meta(seeded_meta, monkeypatch)
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=_qb_stub(seeded_meta))
        with pytest.raises(OpenBBError, match="dataflow is required"):
            tb.get_table()

    def test_section_family_redirects(self, seeded_meta, monkeypatch):
        """Section dataflows resolve up to their parent dataflow."""
        seeded_meta.dataflows["DSD_TEST@DF_TEST_SECTION"] = {
            "id": "DSD_TEST@DF_TEST_SECTION",
            "short_id": "DF_TEST_SECTION",
            "agency_id": "OECD",
            "version": "1.0",
            "name": "Section",
        }
        _patch_meta(
            seeded_meta,
            monkeypatch,
            _resolve_dataflow_id=lambda did: "DSD_TEST@DF_TEST_SECTION",
            _detect_section_families=lambda: {"DSD_TEST@DF_TEST_SECTION": _FULL_ID},
        )
        qb = _qb_stub(seeded_meta)
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        with pytest.raises(OpenBBError, match="No indicators match"):
            tb.get_table(dataflow="DF_TEST_SECTION")

    def test_auto_select_single_table(self, seeded_meta, monkeypatch):
        """When exactly one table exists it is auto-selected."""
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_hierarchies=lambda did: [{"id": "OnlyT"}],
        )
        qb = _qb_stub(seeded_meta)
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        with pytest.raises(OpenBBError, match="No indicators match"):
            tb.get_table(dataflow=_SHORT_ID)

    def test_zero_tables_keeps_table_id_none(self, seeded_meta, monkeypatch):
        """Zero hierarchies means we proceed without TABLE_IDENTIFIER pin."""
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_hierarchies=lambda did: [],
        )
        qb = _qb_stub(seeded_meta)
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        with pytest.raises(OpenBBError, match="No indicators match"):
            tb.get_table(dataflow=_SHORT_ID)


def _make_tb(seeded_meta, monkeypatch, hierarchy, data_rows, **kwargs):
    """Wire up an OecdTableBuilder with controlled hierarchy and data rows."""
    overrides = {
        "get_dataflow_table_structure": lambda did, tid: {
            "hierarchy_name": "H1",
            "indicators": hierarchy,
        },
    }
    overrides.update(kwargs)
    _patch_meta(seeded_meta, monkeypatch, **overrides)
    qb = _qb_stub(seeded_meta)
    qb.fetch_data.return_value = {
        "data": data_rows,
        "metadata": {"url": "http://example/data"},
    }
    return OecdTableBuilder(metadata=seeded_meta, query_builder=qb), qb


class TestFiltering:
    """Hierarchy filtering by indicators, parent_id, and depth."""

    def test_indicators_string_filter(self, seeded_meta, monkeypatch):
        """A single string indicator filters the hierarchy to that code."""
        hier = [
            {
                "code": "A",
                "label": "Alpha",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
            {
                "code": "B",
                "label": "Beta",
                "order": 1,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "MEASURE_label": "Alpha",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.5,
                "REF_AREA": "USA",
            },
        ]
        tb, qb = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID, indicators="A")
        codes = {r["code"] for r in result["data"]}
        assert codes == {"A"}

    def test_indicators_list_filter(self, seeded_meta, monkeypatch):
        """A list of indicator codes filters the hierarchy."""
        hier = [
            {
                "code": "A",
                "label": "Alpha",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
            {
                "code": "B",
                "label": "Beta",
                "order": 1,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {"MEASURE": "A", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0},
            {"MEASURE": "B", "TIME_PERIOD": "2024", "OBS_VALUE": 2.0},
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID, indicators=["A", "B"])
        assert len(result["data"]) == 2

    def test_parent_id_filter(self, seeded_meta, monkeypatch):
        """parent_id keeps only items whose parent matches."""
        hier = [
            {
                "code": "P",
                "label": "Parent",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": ["C"],
            },
            {
                "code": "C",
                "label": "Child",
                "order": 1,
                "level": 1,
                "parent": "P",
                "children": [],
            },
        ]
        rows = [{"MEASURE": "C", "TIME_PERIOD": "2024", "OBS_VALUE": 5.0}]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID, parent_id="P")
        assert all(r["code"] == "C" for r in result["data"])

    def test_depth_filter(self, seeded_meta, monkeypatch):
        """depth filter keeps only nodes at that hierarchy level."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
            {
                "code": "B",
                "label": "B",
                "order": 1,
                "level": 1,
                "parent": "A",
                "children": [],
            },
        ]
        rows = [{"MEASURE": "A", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0}]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID, depth=0)
        assert all(r["code"] == "A" for r in result["data"])


class TestIndicatorDimensionResolution:
    """Indicator-dim discovery and codelist-based fallback."""

    def test_fallback_indicator_dim_largest_codelist(self, seeded_meta, monkeypatch):
        """When _find_indicator_dimension returns None, we pick by codelist size."""
        hier = [
            {
                "code": "USA",
                "label": "USA",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [{"REF_AREA": "USA", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0}]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            _find_indicator_dimension=lambda did: None,
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.return_value = {
            "data": rows,
            "metadata": {"url": "u"},
        }
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"]

    def test_fallback_to_measure_when_no_dims(self, seeded_meta, monkeypatch):
        """No codelists at all → fallback returns 'MEASURE'."""
        seeded_meta.codelists = {}
        hier = [
            {
                "code": "X",
                "label": "X",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [{"MEASURE": "X", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0}]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            _find_indicator_dimension=lambda did: None,
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.return_value = {"data": rows, "metadata": {"url": "u"}}
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"]


class TestCountryFrequencyResolution:
    """Country / frequency pinning behaviour."""

    def test_country_resolution_pins_codes(self, seeded_meta, monkeypatch):
        """resolve_country_codes returns codes → REF_AREA gets joined codes."""
        captured: dict = {}

        def _fetch_data(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            resolve_country_codes=lambda did, raw: ["USA", "GBR"],
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch_data
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID, country="USA+GBR")
        except OpenBBError:
            pass
        assert captured.get("REF_AREA") == "USA+GBR"

    def test_country_skipped_when_no_codes(self, seeded_meta, monkeypatch):
        """resolve_country_codes returns [] → no REF_AREA injection."""
        captured: dict = {}

        def _fetch_data(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            resolve_country_codes=lambda did, raw: [],
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch_data
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID, country="UNKNOWN")
        except OpenBBError:
            pass
        assert "REF_AREA" not in captured or captured.get("REF_AREA") is None

    def test_frequency_pinned(self, seeded_meta, monkeypatch):
        """Frequency arg goes into the kwargs for fetch."""
        captured: dict = {}

        def _fetch_data(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch_data
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID, frequency="q")
        except OpenBBError:
            pass
        assert captured.get("FREQ") == "Q"


class TestTableGroupingDim:
    """TABLE_IDENTIFIER / CHAPTER dim pinning."""

    def test_table_identifier_pinned(self, seeded_meta, monkeypatch):
        """If DSD has TABLE_IDENTIFIER, it is set to the table_id."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "TABLE_IDENTIFIER",
                "position": 4,
                "codelist_id": "",
                "concept_id": "TABLE_IDENTIFIER",
                "name": "TID",
            }
        )
        captured: dict = {}

        def _fetch(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID, table_id="T1")
        except OpenBBError:
            pass
        assert captured.get("TABLE_IDENTIFIER") == "T1"


class TestAvailabilityAutoPin:
    """Availability-driven auto-pinning of dimensions."""

    def test_single_value_pinned(self, seeded_meta, monkeypatch):
        """A dim with exactly one available value is pinned to that value."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "UNIT_MEASURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "UNIT_MEASURE",
                "name": "Unit",
            }
        )
        captured: dict = {}

        def _fetch(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {"UNIT_MEASURE": ["USD"]},
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID)
        except OpenBBError:
            pass
        assert captured.get("UNIT_MEASURE") == "USD"

    def test_metadata_preference_picks_pref(self, seeded_meta, monkeypatch):
        """When multiple values available, prefer XDC first."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "UNIT_MEASURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "UNIT_MEASURE",
                "name": "Unit",
            }
        )
        captured: dict = {}

        def _fetch(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {
                "UNIT_MEASURE": ["EUR", "USD_PPP", "XDC"]
            },
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID)
        except OpenBBError:
            pass
        assert captured.get("UNIT_MEASURE") == "XDC"

    def test_metadata_no_pref_falls_back_to_first(self, seeded_meta, monkeypatch):
        """When prefs don't match any available, pin to first."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "UNIT_MEASURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "UNIT_MEASURE",
                "name": "Unit",
            }
        )
        captured: dict = {}

        def _fetch(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {
                "UNIT_MEASURE": ["EUR", "GBP"]
            },
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID)
        except OpenBBError:
            pass
        assert captured.get("UNIT_MEASURE") == "EUR"

    def test_structural_pref_pins_S1(self, seeded_meta, monkeypatch):
        """SECTOR with S1 in availability gets pinned to S1."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "SECTOR",
                "position": 4,
                "codelist_id": "",
                "concept_id": "SECTOR",
                "name": "Sector",
            }
        )
        captured: dict = {}

        def _fetch(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {
                "SECTOR": ["S1", "S11", "S12"]
            },
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID)
        except OpenBBError:
            pass
        assert captured.get("SECTOR") == "S1"

    def test_structural_data_carrying_skipped(self, seeded_meta, monkeypatch):
        """INSTR_ASSET with only neutral prefs and many values stays wildcard."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "INSTR_ASSET",
                "position": 4,
                "codelist_id": "",
                "concept_id": "INSTR_ASSET",
                "name": "Instr",
            }
        )
        captured: dict = {}

        def _fetch(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {
                "INSTR_ASSET": ["_Z", "F1", "F2", "F3"]
            },
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID)
        except OpenBBError:
            pass
        assert "INSTR_ASSET" not in captured

    def test_activity_dim_left_unpinned(self, seeded_meta, monkeypatch):
        """ACTIVITY may carry real series — left wildcard."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "ACTIVITY",
                "position": 4,
                "codelist_id": "",
                "concept_id": "ACTIVITY",
                "name": "Act",
            }
        )
        captured: dict = {}

        def _fetch(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {"ACTIVITY": ["X", "Y", "Z"]},
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID)
        except OpenBBError:
            pass
        assert "ACTIVITY" not in captured

    def test_counterpart_area_pinned_to_W(self, seeded_meta, monkeypatch):
        """Secondary country dims pin to 'W' aggregate when available."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "COUNTERPART_AREA",
                "position": 4,
                "codelist_id": "",
                "concept_id": "COUNTERPART_AREA",
                "name": "CParty",
            }
        )
        captured: dict = {}

        def _fetch(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {
                "COUNTERPART_AREA": ["W", "USA", "DEU"]
            },
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID)
        except OpenBBError:
            pass
        assert captured.get("COUNTERPART_AREA") == "W"

    def test_counterpart_area_first_value_fallback(self, seeded_meta, monkeypatch):
        """No aggregate values → take the first available value."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "COUNTERPART_AREA",
                "position": 4,
                "codelist_id": "",
                "concept_id": "COUNTERPART_AREA",
                "name": "CParty",
            }
        )
        captured: dict = {}

        def _fetch(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {
                "COUNTERPART_AREA": ["USA", "DEU"]
            },
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID)
        except OpenBBError:
            pass
        assert captured.get("COUNTERPART_AREA") == "USA"

    def test_skip_when_overlap_with_hierarchy(self, seeded_meta, monkeypatch):
        """Available codes intersecting hierarchy codes are NOT auto-pinned."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "TABLE_IDENTIFIER",
                "position": 4,
                "codelist_id": "",
                "concept_id": "TABLE_IDENTIFIER",
                "name": "T",
            }
        )
        captured: dict = {}

        def _fetch(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]

        def _avail(did, pinned=None):
            return {"MEASURE": ["A"]}

        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=_avail,
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID)
        except OpenBBError:
            pass
        assert "MEASURE" not in captured

    def test_availability_raises_falls_back_empty(self, seeded_meta, monkeypatch):
        """If fetch_availability raises, processing continues with empty dict."""

        def _avail(did, pinned=None):
            raise RuntimeError("boom")

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=_avail,
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.return_value = {
            "data": [{"MEASURE": "A", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0}],
            "metadata": {"url": "u"},
        }
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"]

    def test_empty_available_vals_continues(self, seeded_meta, monkeypatch):
        """Dimensions with empty availability arrays are silently skipped."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "ADJUSTMENT",
                "position": 4,
                "codelist_id": "",
                "concept_id": "ADJUSTMENT",
                "name": "Adj",
            }
        )
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "TRANSFORMATION",
                "position": 5,
                "codelist_id": "",
                "concept_id": "TRANSFORMATION",
                "name": "Trans",
            }
        )
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [{"MEASURE": "A", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0}]

        def _avail(did, pinned=None):
            return {"ADJUSTMENT": [], "TRANSFORMATION": ["LA"]}

        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=_avail,
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.return_value = {"data": rows, "metadata": {"url": "u"}}
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"]


class TestValidationWarnings:
    """Constraint validation pathway."""

    def test_value_error_propagates(self, seeded_meta, monkeypatch):
        """ValueError from validate_dimension_constraints propagates."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
        )
        qb = _qb_stub(seeded_meta)
        qb.validate_dimension_constraints.side_effect = ValueError("bad code")
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        with pytest.raises(ValueError, match="bad code"):
            tb.get_table(dataflow=_SHORT_ID, MEASURE="WRONG")

    def test_generic_exception_becomes_warning(self, seeded_meta, monkeypatch):
        """Non-ValueError exceptions surface as OpenBBWarning."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
        )
        qb = _qb_stub(seeded_meta)
        qb.validate_dimension_constraints.side_effect = RuntimeError("boom")
        qb.fetch_data.return_value = {
            "data": [{"MEASURE": "A", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0}],
            "metadata": {"url": "u"},
        }
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        with pytest.warns(OpenBBWarning, match="Constraint validation failed"):
            tb.get_table(dataflow=_SHORT_ID, MEASURE="A")

    def test_no_kwargs_skips_validation(self, seeded_meta, monkeypatch):
        """No filters at all → validation not called."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.return_value = {"data": [], "metadata": {"url": "u"}}
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID)
        except OpenBBError:
            pass
        qb.validate_dimension_constraints.assert_not_called()


class TestPostFilter:
    """Post-fetch indicator filtering against the hierarchy."""

    def test_rows_outside_hierarchy_dropped(self, seeded_meta, monkeypatch):
        """A row whose MEASURE is not in hierarchy is filtered out."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {"MEASURE": "A", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0},
            {"MEASURE": "ZZ", "TIME_PERIOD": "2024", "OBS_VALUE": 9.9},
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        codes = [r["code"] for r in result["data"]]
        assert "A" in codes
        assert "ZZ" not in codes


class TestSimpleEnrichment:
    """Non-ACCOUNTING_ENTRY simple enrichment branch."""

    def test_hierarchy_match_assigns_meta(self, seeded_meta, monkeypatch):
        """A direct hierarchy match populates label/level/order."""
        hier = [
            {
                "code": "A",
                "label": "Alpha",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "MEASURE_label": "Alpha",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.5,
            },
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        row = result["data"][0]
        assert row["label"] == "Alpha"
        assert row["code"] == "A"
        assert row["value"] == 1.5

    def test_indicator_prefix_match(self, seeded_meta, monkeypatch):
        """Row code A_X matches hierarchy entry 'A' through prefix logic."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "CHAPTER",
                "position": 4,
                "codelist_id": "",
                "concept_id": "CHAPTER",
                "name": "Ch",
            }
        )
        hier = [
            {
                "code": "A",
                "label": "Alpha",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A_X",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
                "CHAPTER": "C1",
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.return_value = {"data": rows, "metadata": {"url": "u"}}
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        result = tb.get_table(dataflow=_SHORT_ID, table_id="C1")
        assert any(r["code"] == "A_X" for r in result["data"])

    def test_no_hierarchy_match_row_dropped(self, seeded_meta, monkeypatch):
        """Row without hierarchy info is excluded from output."""
        hier = [
            {
                "code": "A",
                "label": "Alpha",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {"MEASURE": "A", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0},
            {"MEASURE": "", "TIME_PERIOD": "2024", "OBS_VALUE": 2.0},
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert len(result["data"]) == 1


class TestUnitMultExpansion:
    """OBS_VALUE multiplied by 10**UNIT_MULT."""

    def test_unit_mult_positive(self, seeded_meta, monkeypatch):
        """Positive UNIT_MULT scales value upward."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {"MEASURE": "A", "TIME_PERIOD": "2024", "OBS_VALUE": 2.0, "UNIT_MULT": "6"},
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"][0]["value"] == 2_000_000.0

    def test_unit_mult_zero_no_change(self, seeded_meta, monkeypatch):
        """UNIT_MULT=0 leaves the value alone."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {"MEASURE": "A", "TIME_PERIOD": "2024", "OBS_VALUE": 3.5, "UNIT_MULT": "0"},
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"][0]["value"] == 3.5

    def test_unit_mult_invalid_swallowed(self, seeded_meta, monkeypatch):
        """A non-numeric UNIT_MULT is ignored rather than crashing."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 5.0,
                "UNIT_MULT": "notanumber",
            },
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"][0]["value"] == 5.0


class TestFixedAndVaryingDims:
    """Detection of fixed vs varying dimensions."""

    def test_fixed_unit_measure_label(self, seeded_meta, monkeypatch):
        """When UNIT_MEASURE is constant it becomes a fixed dim label."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "UNIT_MEASURE": "XDC",
                "UNIT_MEASURE_label": "Local currency",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "A",
                "UNIT_MEASURE": "XDC",
                "UNIT_MEASURE_label": "Local currency",
                "TIME_PERIOD": "2025",
                "OBS_VALUE": 2.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "UNIT_MEASURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "UNIT_MEASURE",
                "name": "Unit",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["table_metadata"]["unit_measure"] == "Local currency"

    def test_varying_metadata_dim_becomes_column(self, seeded_meta, monkeypatch):
        """Varying ADJUSTMENT keeps as a regular column on each row."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "ADJUSTMENT": "Y",
                "ADJUSTMENT_label": "Adjusted",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "A",
                "ADJUSTMENT": "N",
                "ADJUSTMENT_label": "Non-adjusted",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 2.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "ADJUSTMENT",
                "position": 4,
                "codelist_id": "",
                "concept_id": "ADJUSTMENT",
                "name": "Adj",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        labels = {r.get("adjustment") for r in result["data"]}
        assert "Adjusted" in labels
        assert "Non-adjusted" in labels

    def test_use_labels_false_uses_codes(self, seeded_meta, monkeypatch):
        """use_labels=False puts raw codes in varying-dim columns."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "ADJUSTMENT": "Y",
                "ADJUSTMENT_label": "Adjusted",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "A",
                "ADJUSTMENT": "N",
                "ADJUSTMENT_label": "Non-adjusted",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 2.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "ADJUSTMENT",
                "position": 4,
                "codelist_id": "",
                "concept_id": "ADJUSTMENT",
                "name": "Adj",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID, use_labels=False)
        codes = {r.get("adjustment") for r in result["data"]}
        assert codes == {"Y", "N"}


class TestCompoundDimensions:
    """Content-varying dimensions folded into compound codes/labels."""

    def test_compound_dim_appended(self, seeded_meta, monkeypatch):
        """A varying content dim gets folded into code + label."""
        hier = [
            {
                "code": "A",
                "label": "Alpha",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "MEASURE_label": "Alpha",
                "EXPENDITURE": "P3",
                "EXPENDITURE_label": "Consumption",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "A",
                "MEASURE_label": "Alpha",
                "EXPENDITURE": "P5",
                "EXPENDITURE_label": "Investment",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 2.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "EXPENDITURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "EXPENDITURE",
                "name": "Exp",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        codes = {r["code"] for r in result["data"]}
        assert "A_P3" in codes
        assert "A_P5" in codes

    def test_neutral_compound_dim_skipped(self, seeded_meta, monkeypatch):
        """A _Z / _T value in a compound dim is not appended."""
        hier = [
            {
                "code": "A",
                "label": "Alpha",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "EXPENDITURE": "_Z",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "A",
                "EXPENDITURE": "P3",
                "EXPENDITURE_label": "Consumption",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 2.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "EXPENDITURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "EXPENDITURE",
                "name": "Exp",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        codes = {r["code"] for r in result["data"]}
        assert "A" in codes  # neutral row keeps plain code
        assert "A_P3" in codes

    def test_compound_with_codelist_hierarchy(self, seeded_meta, monkeypatch):
        """Compound dim codelist parents apply depth + hierarchy ordering."""
        hier = [
            {
                "code": "A",
                "label": "Alpha",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "EXPENDITURE": "TRA",
                "EXPENDITURE_label": "Transport",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "A",
                "EXPENDITURE": "SEA",
                "EXPENDITURE_label": "Sea transport",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 2.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "EXPENDITURE",
                "position": 4,
                "codelist_id": "OECD:CL_EXP(1.0)",
                "concept_id": "EXPENDITURE",
                "name": "Exp",
            }
        )
        seeded_meta._codelist_parents["OECD:CL_EXP(1.0)"] = {"SEA": "TRA"}
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        levels = {r["code"]: r["level"] for r in result["data"]}
        assert levels["A_SEA"] > levels["A_TRA"]

    def test_compound_codelist_no_parents(self, seeded_meta, monkeypatch):
        """Compound dim with no codelist parents leaves level untouched."""
        hier = [
            {
                "code": "A",
                "label": "Alpha",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "EXPENDITURE": "TRA",
                "EXPENDITURE_label": "Transport",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "A",
                "EXPENDITURE": "SEA",
                "EXPENDITURE_label": "Sea",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 2.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "EXPENDITURE",
                "position": 4,
                "codelist_id": "OECD:CL_NOPAR(1.0)",
                "concept_id": "EXPENDITURE",
                "name": "Exp",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert any(r["code"] == "A_TRA" for r in result["data"])

    def test_compound_no_codelist_id(self, seeded_meta, monkeypatch):
        """Compound dim with empty codelist_id is skipped for hierarchy."""
        hier = [
            {
                "code": "A",
                "label": "Alpha",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "EXPENDITURE": "TRA",
                "EXPENDITURE_label": "Transport",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "A",
                "EXPENDITURE": "SEA",
                "EXPENDITURE_label": "Sea",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 2.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "EXPENDITURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "EXPENDITURE",
                "name": "Exp",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert any(r["code"] == "A_TRA" for r in result["data"])

    def test_compound_no_data_for_dim(self, seeded_meta, monkeypatch):
        """Compound dim with empty present values is skipped."""
        hier = [
            {
                "code": "A",
                "label": "Alpha",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "EXPENDITURE": "",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "A",
                "EXPENDITURE": "TRA",
                "EXPENDITURE_label": "Transport",
                "TIME_PERIOD": "2025",
                "OBS_VALUE": 2.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "EXPENDITURE",
                "position": 4,
                "codelist_id": "OECD:CL_EXP(1.0)",
                "concept_id": "EXPENDITURE",
                "name": "Exp",
            }
        )
        seeded_meta._codelist_parents["OECD:CL_EXP(1.0)"] = {"SEA": "TRA"}
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"]


class TestAccountingEntry:
    """ACCOUNTING_ENTRY sub-hierarchy expansion."""

    def test_balance_entry_top_level(self, seeded_meta, monkeypatch):
        """A 'B' accounting entry is treated as the parent-level row."""
        hier = [
            {
                "code": "CA",
                "label": "Current Account",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "CA",
                "ACCOUNTING_ENTRY": "B",
                "ACCOUNTING_ENTRY_label": "Balance",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 100.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "ACCOUNTING_ENTRY",
                "position": 4,
                "codelist_id": "",
                "concept_id": "ACCOUNTING_ENTRY",
                "name": "AE",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        balance = next(r for r in result["data"] if r["code"] == "CA")
        assert balance["value"] == 100.0

    def test_acct_grouped_with_children(self, seeded_meta, monkeypatch):
        """Parent FA has A/L entries with matching child entries → nested."""
        hier = [
            {
                "code": "FA",
                "label": "Financial Account",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": ["DI"],
            },
            {
                "code": "DI",
                "label": "Direct Investment",
                "order": 1,
                "level": 1,
                "parent": "FA",
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "FA",
                "ACCOUNTING_ENTRY": "A",
                "ACCOUNTING_ENTRY_label": "Assets",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 50.0,
            },
            {
                "MEASURE": "FA",
                "ACCOUNTING_ENTRY": "L",
                "ACCOUNTING_ENTRY_label": "Liabilities",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 60.0,
            },
            {
                "MEASURE": "DI",
                "ACCOUNTING_ENTRY": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 10.0,
            },
            {
                "MEASURE": "DI",
                "ACCOUNTING_ENTRY": "L",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 12.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "ACCOUNTING_ENTRY",
                "position": 4,
                "codelist_id": "",
                "concept_id": "ACCOUNTING_ENTRY",
                "name": "AE",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        labels = [r["label"] for r in result["data"]]
        assert any("Assets" in lbl for lbl in labels)
        assert any("Liabilities" in lbl for lbl in labels)

    def test_acct_ungrouped(self, seeded_meta, monkeypatch):
        """Parent has C/D entries with no matching children → ungrouped path."""
        hier = [
            {
                "code": "GG",
                "label": "General Govt",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "GG",
                "ACCOUNTING_ENTRY": "C",
                "ACCOUNTING_ENTRY_label": "Revenue",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "GG",
                "ACCOUNTING_ENTRY": "D",
                "ACCOUNTING_ENTRY_label": "Expenditure",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 2.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "ACCOUNTING_ENTRY",
                "position": 4,
                "codelist_id": "",
                "concept_id": "ACCOUNTING_ENTRY",
                "name": "AE",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        labels = [r["label"] for r in result["data"]]
        assert any("Revenue" in lbl for lbl in labels)
        assert any("Expenditure" in lbl for lbl in labels)

    def test_acct_no_bn_synthetic_header(self, seeded_meta, monkeypatch):
        """When indicator has subs but no B/N, a synthetic header is emitted."""
        hier = [
            {
                "code": "FA",
                "label": "Financial Account",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "FA",
                "ACCOUNTING_ENTRY": "A",
                "ACCOUNTING_ENTRY_label": "Assets",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 10.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "ACCOUNTING_ENTRY",
                "position": 4,
                "codelist_id": "",
                "concept_id": "ACCOUNTING_ENTRY",
                "name": "AE",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        # The first row should be a synthetic header (is_category_header).
        header = result["data"][0]
        assert header["is_category_header"] is True

    def test_acct_filter_recursion_missing_parent_rows(self, seeded_meta, monkeypatch):
        """Grouped acct entry with no parent rows emits a synthetic header."""
        hier = [
            {
                "code": "FA",
                "label": "FA",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": ["DI"],
            },
            {
                "code": "DI",
                "label": "DI",
                "order": 1,
                "level": 1,
                "parent": "FA",
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "DI",
                "ACCOUNTING_ENTRY": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "ACCOUNTING_ENTRY",
                "position": 4,
                "codelist_id": "",
                "concept_id": "ACCOUNTING_ENTRY",
                "name": "AE",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"]


class TestCanonicalRootOrdering:
    """CA / KA root swap for Balance of Payments tables."""

    def test_ca_ka_order_swapped(self, seeded_meta, monkeypatch):
        """When CA is ordered after KA at root level the two swap."""
        hier = [
            {
                "code": "KA",
                "label": "Capital Account",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
            {
                "code": "CA",
                "label": "Current Account",
                "order": 1,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {"MEASURE": "CA", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0},
            {"MEASURE": "KA", "TIME_PERIOD": "2024", "OBS_VALUE": 2.0},
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        codes = [r["code"] for r in result["data"]]
        assert codes.index("CA") < codes.index("KA")


class TestLabelDerivation:
    """Useless / placeholder label substitution paths."""

    def test_useless_label_replaced_by_dim_label(self, seeded_meta, monkeypatch):
        """A 'total' label is replaced by the MEASURE_label dimension label."""
        hier = [
            {
                "code": "A",
                "label": "Total",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "MEASURE_label": "Gross Domestic Product",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"][0]["label"] == "Gross Domestic Product"

    def test_underscore_label_blanked(self, seeded_meta, monkeypatch):
        """Labels starting with '_' (neutral codes) are blanked."""
        hier = [
            {
                "code": "A",
                "label": "_Z",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {"MEASURE": "A", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0},
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"][0]["label"] in {"", "A"}

    def test_label_from_compound_dims_when_useless(self, seeded_meta, monkeypatch):
        """No indicator label, no fallback label → derive from compound dims."""
        hier = [
            {
                "code": "A",
                "label": "Total",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "EXPENDITURE": "P3",
                "EXPENDITURE_label": "Consumption",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "A",
                "EXPENDITURE": "P5",
                "EXPENDITURE_label": "Investment",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 2.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "EXPENDITURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "EXPENDITURE",
                "name": "Exp",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        labels = {r["label"] for r in result["data"]}
        assert "Consumption" in labels or any("Consumption" in lbl for lbl in labels)

    def test_label_from_indicator_code_when_no_compounds(
        self, seeded_meta, monkeypatch
    ):
        """No label, no fallback path → use indicator code."""
        hier = [
            {
                "code": "XYZ",
                "label": "_X",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {"MEASURE": "XYZ", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0},
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        # base_label starts with '_' → blanked → empty string
        assert result["data"][0]["label"] in {"", "XYZ"}

    def test_nan_float_label_blanked(self, seeded_meta, monkeypatch):
        """float labels (e.g. NaN) get blanked by _clean_label."""
        hier = [
            {
                "code": "A",
                "label": float("nan"),
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "MEASURE_label": "Alpha",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"][0]["label"] == "Alpha"


class TestPctGdpSubrows:
    """% of GDP supplementary row injection."""

    def test_pct_gdp_subrows_added(self, seeded_meta, monkeypatch):
        """When availability lists PT_B1GQ a second fetch injects sub-rows."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        primary_rows = [
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 100.0,
                "ACCOUNTING_ENTRY": "",
            },
        ]
        pct_rows = [
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 5.5,
                "ACCOUNTING_ENTRY": "",
                "UNIT_MULT": "0",
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "UNIT_MEASURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "UNIT_MEASURE",
                "name": "Unit",
            }
        )
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {
                "UNIT_MEASURE": ["XDC", "PT_B1GQ"]
            },
        )
        qb = _qb_stub(seeded_meta)
        call_count = {"n": 0}

        def _fetch(**kwargs):
            call_count["n"] += 1
            if (kwargs.get("dimension_filters") or {}).get("UNIT_MEASURE") == "PT_B1GQ":
                return {"data": pct_rows, "metadata": {"url": "u2"}}
            return {"data": primary_rows, "metadata": {"url": "u1"}}

        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        result = tb.get_table(dataflow=_SHORT_ID)
        labels = [r["label"] for r in result["data"]]
        assert "% of GDP" in labels
        assert call_count["n"] >= 2

    def test_dimension_filters_dict_merged_with_kwargs(self, seeded_meta, monkeypatch):
        """``dimension_filters`` param flattens into kwargs before fetch."""
        captured: dict = {}

        def _fetch_data(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch_data
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID, dimension_filters={"MEASURE": "CPI"})
        except OpenBBError:
            pass
        assert captured.get("MEASURE") == "CPI"

    def test_pct_gdp_unit_mult_applied(self, seeded_meta, monkeypatch):
        """% of GDP values get UNIT_MULT expansion."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        primary_rows = [
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 100.0,
                "ACCOUNTING_ENTRY": "",
            },
        ]
        pct_rows = [
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 3.0,
                "ACCOUNTING_ENTRY": "",
                "UNIT_MULT": "2",
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "UNIT_MEASURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "UNIT_MEASURE",
                "name": "Unit",
            }
        )
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {
                "UNIT_MEASURE": ["XDC", "PT_B1GQ"]
            },
        )
        qb = _qb_stub(seeded_meta)

        def _fetch(**kwargs):
            if (kwargs.get("dimension_filters") or {}).get("UNIT_MEASURE") == "PT_B1GQ":
                return {"data": pct_rows, "metadata": {"url": "u2"}}
            return {"data": primary_rows, "metadata": {"url": "u1"}}

        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        result = tb.get_table(dataflow=_SHORT_ID)
        pct_row = next(r for r in result["data"] if r["label"] == "% of GDP")
        assert pct_row["value"] == 300.0

    def test_pct_gdp_unit_mult_invalid(self, seeded_meta, monkeypatch):
        """Invalid UNIT_MULT on % of GDP row is silently ignored."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        primary_rows = [
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 100.0,
                "ACCOUNTING_ENTRY": "",
            },
        ]
        pct_rows = [
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 7.5,
                "ACCOUNTING_ENTRY": "",
                "UNIT_MULT": "bogus",
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "UNIT_MEASURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "UNIT_MEASURE",
                "name": "Unit",
            }
        )
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {
                "UNIT_MEASURE": ["XDC", "PT_B1GQ"]
            },
        )
        qb = _qb_stub(seeded_meta)

        def _fetch(**kwargs):
            if (kwargs.get("dimension_filters") or {}).get("UNIT_MEASURE") == "PT_B1GQ":
                return {"data": pct_rows, "metadata": {"url": "u2"}}
            return {"data": primary_rows, "metadata": {"url": "u1"}}

        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        result = tb.get_table(dataflow=_SHORT_ID)
        pct_row = next(r for r in result["data"] if r["label"] == "% of GDP")
        assert pct_row["value"] == 7.5

    def test_pct_gdp_already_primary_unit_skipped(self, seeded_meta, monkeypatch):
        """When primary is already PT_B1GQ no secondary fetch occurs."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        primary_rows = [
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 5.0,
                "ACCOUNTING_ENTRY": "",
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "UNIT_MEASURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "UNIT_MEASURE",
                "name": "Unit",
            }
        )
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {"UNIT_MEASURE": ["PT_B1GQ"]},
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.return_value = {"data": primary_rows, "metadata": {"url": "u"}}
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        result = tb.get_table(dataflow=_SHORT_ID)
        labels = [r["label"] for r in result["data"]]
        assert "% of GDP" not in labels

    def test_pct_gdp_secondary_fetch_failure(self, seeded_meta, monkeypatch):
        """Secondary fetch failure is swallowed silently."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        primary_rows = [
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 5.0,
                "ACCOUNTING_ENTRY": "",
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "UNIT_MEASURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "UNIT_MEASURE",
                "name": "Unit",
            }
        )
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {
                "UNIT_MEASURE": ["XDC", "PT_B1GQ"]
            },
        )
        qb = _qb_stub(seeded_meta)
        call_count = {"n": 0}

        def _fetch(**kwargs):
            call_count["n"] += 1
            if (kwargs.get("dimension_filters") or {}).get("UNIT_MEASURE") == "PT_B1GQ":
                raise RuntimeError("secondary fetch failed")
            return {"data": primary_rows, "metadata": {"url": "u"}}

        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        result = tb.get_table(dataflow=_SHORT_ID)
        labels = [r["label"] for r in result["data"]]
        assert "% of GDP" not in labels


class TestMetadataExtraction:
    """table_metadata output dict assembly."""

    def test_basic_metadata_fields(self, seeded_meta, monkeypatch):
        """Common metadata fields are present in the response."""
        hier = [
            {
                "code": "A",
                "label": "Alpha",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {"MEASURE": "A", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0},
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID, table_id="T1")
        meta = result["table_metadata"]
        assert meta["table_id"] == "T1"
        assert meta["dataflow_id"] == _FULL_ID
        assert meta["row_count"] >= 1

    def test_metadata_table_id_fallback(self, seeded_meta, monkeypatch):
        """When no table_id is set, fall back to short_id."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [{"MEASURE": "A", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0}]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["table_metadata"]["table_id"] == _SHORT_ID

    def test_attr_label_from_data_rows(self, seeded_meta, monkeypatch):
        """Unit-measure pulled from observation-level labels when not fixed."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
                "UNIT_MEASURE_label": "USD",
            },
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2025",
                "OBS_VALUE": 2.0,
                "UNIT_MEASURE_label": "EUR",
            },
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["table_metadata"]["unit_measure"] in {"USD", "EUR"}

    def test_attr_label_falls_back_to_value(self, seeded_meta, monkeypatch):
        """Without *_label key, falls back to the raw attribute value."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
                "UNIT_MEASURE": "USD",
            },
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2025",
                "OBS_VALUE": 2.0,
                "UNIT_MEASURE": "USD",
            },
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["table_metadata"]["unit_measure"] == "USD"

    def test_attr_code_lookup(self, seeded_meta, monkeypatch):
        """unit_multiplier_code resolves from a data-level attr when not fixed."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {"MEASURE": "A", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0, "UNIT_MULT": "6"},
            {"MEASURE": "A", "TIME_PERIOD": "2025", "OBS_VALUE": 2.0, "UNIT_MULT": "6"},
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["table_metadata"]["unit_multiplier_code"] == "6"


class TestCompoundLevelAdjustment:
    """level adjustment when there's no 'total' aggregate row."""

    def test_no_total_undoes_level_bump(self, seeded_meta, monkeypatch):
        """When no aggregate row exists, child level bump is reverted."""
        hier = [
            {
                "code": "A",
                "label": "Alpha",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "EXPENDITURE": "P3",
                "EXPENDITURE_label": "Consumption",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "A",
                "EXPENDITURE": "P5",
                "EXPENDITURE_label": "Investment",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 2.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "EXPENDITURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "EXPENDITURE",
                "name": "Exp",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        levels = {r["level"] for r in result["data"]}
        assert 0 in levels


class TestMissingHierarchyDepthFallback:
    """_calculate_depth used as fallback when entry lacks 'level'."""

    def test_depth_inferred_from_parent_chain(self, seeded_meta, monkeypatch):
        """Hierarchy entries missing 'level' get depth via _calculate_depth."""
        hier = [
            {
                "code": "P",
                "label": "Parent",
                "order": 0,
                "parent": None,
                "children": ["C"],
            },
            {"code": "C", "label": "Child", "order": 1, "parent": "P", "children": []},
        ]
        rows = [
            {"MEASURE": "C", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0},
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID, indicators=["C"])
        assert result["data"][0]["level"] == 1


class TestRemainingBranches:
    """Targeted tests for less-trodden code paths."""

    def test_indicator_fallback_skips_time_period(self, seeded_meta, monkeypatch):
        """Fallback indicator-dim selection skips TIME_PERIOD."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "TIME_PERIOD",
                "position": 4,
                "codelist_id": "OECD:CL_TIME(1.0)",
                "concept_id": "TIME_PERIOD",
                "name": "T",
            }
        )
        hier = [
            {
                "code": "USA",
                "label": "USA",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [{"REF_AREA": "USA", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0}]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            _find_indicator_dimension=lambda did: None,
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.return_value = {"data": rows, "metadata": {"url": "u"}}
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"]

    def test_availability_overlap_skips_dim(self, seeded_meta, monkeypatch):
        """A dim whose values overlap hierarchy codes is left wildcard."""
        captured: dict = {}

        def _fetch(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {"MEASURE": ["A", "B"]},
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID)
        except OpenBBError:
            pass
        assert "MEASURE" not in captured

    def test_second_pass_single_value_after_refresh(self, seeded_meta, monkeypatch):
        """After re-fetching availability a dim can shrink to one value."""
        for new in (
            {
                "id": "UNIT_MEASURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "UNIT_MEASURE",
                "name": "Unit",
            },
            {
                "id": "ADJUSTMENT",
                "position": 5,
                "codelist_id": "",
                "concept_id": "ADJUSTMENT",
                "name": "Adj",
            },
        ):
            seeded_meta.datastructures[_FULL_ID]["dimensions"].append(new)
        call_count = {"n": 0}

        def _avail(did, pinned=None):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return {
                    "UNIT_MEASURE": ["XDC", "USD"],
                    "ADJUSTMENT": ["Y", "N"],
                }
            return {
                "UNIT_MEASURE": ["XDC"],
                "ADJUSTMENT": ["Y"],
            }

        captured: dict = {}

        def _fetch(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=_avail,
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID)
        except OpenBBError:
            pass
        assert captured.get("UNIT_MEASURE") == "XDC"
        assert captured.get("ADJUSTMENT") == "Y"

    def test_hierarchy_entry_no_code_skipped(self, seeded_meta, monkeypatch):
        """Hierarchy entries with empty 'code' are silently dropped."""
        hier = [
            {
                "code": "A",
                "label": "Alpha",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
            {
                "code": "",
                "label": "Empty",
                "order": 1,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [{"MEASURE": "A", "TIME_PERIOD": "2024", "OBS_VALUE": 1.0}]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        codes = {r["code"] for r in result["data"]}
        assert "A" in codes
        assert "" not in codes

    def test_ungrouped_acct_children_no_match(self, seeded_meta, monkeypatch):
        """Children that lack the parent's acct entries → entry stays ungrouped."""
        hier = [
            {
                "code": "P",
                "label": "P",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": ["C"],
            },
            {
                "code": "C",
                "label": "C",
                "order": 1,
                "level": 1,
                "parent": "P",
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "P",
                "ACCOUNTING_ENTRY": "C",
                "ACCOUNTING_ENTRY_label": "Revenue",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "P",
                "ACCOUNTING_ENTRY": "D",
                "ACCOUNTING_ENTRY_label": "Expenditure",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 2.0,
            },
            {
                "MEASURE": "C",
                "ACCOUNTING_ENTRY": "B",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 3.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "ACCOUNTING_ENTRY",
                "position": 4,
                "codelist_id": "",
                "concept_id": "ACCOUNTING_ENTRY",
                "name": "AE",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        labels = [r["label"] for r in result["data"]]
        assert any("Revenue" in lbl for lbl in labels)
        assert any("Expenditure" in lbl for lbl in labels)

    def test_label_fallback_to_indicator_code(self, seeded_meta, monkeypatch):
        """When nothing else available, label falls back to the code."""
        hier = [
            {
                "code": "XYZ",
                "label": "Total",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "XYZ",
                "EXPENDITURE": "_Z",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "EXPENDITURE",
                "position": 4,
                "codelist_id": "",
                "concept_id": "EXPENDITURE",
                "name": "Exp",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert any(r["label"] == "XYZ" for r in result["data"])

    def test_compound_present_empty_skipped(self, seeded_meta, monkeypatch):
        """Compound dim with only empty values in data is skipped."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "EXPENDITURE": "",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "A",
                "EXPENDITURE": "_T",
                "TIME_PERIOD": "2025",
                "OBS_VALUE": 2.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "EXPENDITURE",
                "position": 4,
                "codelist_id": "OECD:CL_EXP(1.0)",
                "concept_id": "EXPENDITURE",
                "name": "Exp",
            }
        )
        seeded_meta._codelist_parents["OECD:CL_EXP(1.0)"] = {"X": "Y"}
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"]

    def test_compound_hier_skipped_for_other_dim(self, seeded_meta, monkeypatch):
        """Multiple compound dims, only one has codelist hierarchy."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "EXPENDITURE": "TRA",
                "EXPENDITURE_label": "Transport",
                "ACTIVITY": "ACT1",
                "ACTIVITY_label": "Activity 1",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "A",
                "EXPENDITURE": "SEA",
                "EXPENDITURE_label": "Sea",
                "ACTIVITY": "ACT2",
                "ACTIVITY_label": "Activity 2",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 2.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].extend(
            [
                {
                    "id": "EXPENDITURE",
                    "position": 4,
                    "codelist_id": "OECD:CL_EXP(1.0)",
                    "concept_id": "EXPENDITURE",
                    "name": "Exp",
                },
                {
                    "id": "ACTIVITY",
                    "position": 5,
                    "codelist_id": "OECD:CL_ACT(1.0)",
                    "concept_id": "ACTIVITY",
                    "name": "Act",
                },
            ]
        )
        seeded_meta._codelist_parents["OECD:CL_EXP(1.0)"] = {"SEA": "TRA"}
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"]

    def test_acct_grouped_recurse_grandchild(self, seeded_meta, monkeypatch):
        """Grouped acct entries propagate through a 3-level chain."""
        hier = [
            {
                "code": "FA",
                "label": "FA",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": ["DI"],
            },
            {
                "code": "DI",
                "label": "DI",
                "order": 1,
                "level": 1,
                "parent": "FA",
                "children": ["DIS"],
            },
            {
                "code": "DIS",
                "label": "DIS",
                "order": 2,
                "level": 2,
                "parent": "DI",
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "FA",
                "ACCOUNTING_ENTRY": "A",
                "ACCOUNTING_ENTRY_label": "Assets",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 10.0,
            },
            {
                "MEASURE": "DI",
                "ACCOUNTING_ENTRY": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 5.0,
            },
            {
                "MEASURE": "DIS",
                "ACCOUNTING_ENTRY": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "ACCOUNTING_ENTRY",
                "position": 4,
                "codelist_id": "",
                "concept_id": "ACCOUNTING_ENTRY",
                "name": "AE",
            }
        )
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        measures = [r.get("_acct_code") for r in result["data"]]
        assert "A" in measures

    def test_availability_overlap_skips_non_indicator_dim(
        self, seeded_meta, monkeypatch
    ):
        """A non-indicator dim whose values overlap hierarchy is left alone."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "SECTOR",
                "position": 4,
                "codelist_id": "",
                "concept_id": "SECTOR",
                "name": "Sector",
            }
        )
        captured: dict = {}

        def _fetch(**kwargs):
            captured.update(kwargs)
            captured.update(kwargs.get("dimension_filters") or {})
            return {"data": [], "metadata": {"url": "u"}}

        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {"SECTOR": ["A", "B", "C"]},
        )
        qb = _qb_stub(seeded_meta)
        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        try:
            tb.get_table(dataflow=_SHORT_ID)
        except OpenBBError:
            pass
        assert "SECTOR" not in captured

    def test_clean_label_handles_none(self, seeded_meta, monkeypatch):
        """A None hierarchy label flows through _clean_label to empty string."""
        hier = [
            {
                "code": "A",
                "label": None,
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "MEASURE_label": "Alpha",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
        ]
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        assert result["data"][0]["label"] == "Alpha"

    def test_compound_chain_skips_absent_ancestor(self, seeded_meta, monkeypatch):
        """A three-level codelist chain with the middle ancestor missing."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        rows = [
            {
                "MEASURE": "A",
                "EXPENDITURE": "GC",
                "EXPENDITURE_label": "Grandchild",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 1.0,
            },
            {
                "MEASURE": "A",
                "EXPENDITURE": "OTHER",
                "EXPENDITURE_label": "Other",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 2.0,
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "EXPENDITURE",
                "position": 4,
                "codelist_id": "OECD:CL_EXP(1.0)",
                "concept_id": "EXPENDITURE",
                "name": "Exp",
            }
        )
        seeded_meta._codelist_parents["OECD:CL_EXP(1.0)"] = {
            "GC": "MID",
            "MID": "ROOT",
        }
        tb, _ = _make_tb(seeded_meta, monkeypatch, hier, rows)
        result = tb.get_table(dataflow=_SHORT_ID)
        codes = {r["code"] for r in result["data"]}
        assert "A_GC" in codes

    def test_pct_gdp_copies_varying_dims(self, seeded_meta, monkeypatch):
        """% of GDP sub-rows copy varying-dim columns from base row."""
        hier = [
            {
                "code": "A",
                "label": "A",
                "order": 0,
                "level": 0,
                "parent": None,
                "children": [],
            },
        ]
        primary_rows = [
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 100.0,
                "ACCOUNTING_ENTRY": "",
                "ADJUSTMENT": "Y",
                "ADJUSTMENT_label": "Adjusted",
            },
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 90.0,
                "ACCOUNTING_ENTRY": "",
                "ADJUSTMENT": "N",
                "ADJUSTMENT_label": "Non-adjusted",
            },
        ]
        pct_rows = [
            {
                "MEASURE": "A",
                "TIME_PERIOD": "2024",
                "OBS_VALUE": 5.5,
                "ACCOUNTING_ENTRY": "",
                "UNIT_MULT": "0",
            },
        ]
        seeded_meta.datastructures[_FULL_ID]["dimensions"].extend(
            [
                {
                    "id": "UNIT_MEASURE",
                    "position": 4,
                    "codelist_id": "",
                    "concept_id": "UNIT_MEASURE",
                    "name": "Unit",
                },
                {
                    "id": "ADJUSTMENT",
                    "position": 5,
                    "codelist_id": "",
                    "concept_id": "ADJUSTMENT",
                    "name": "Adj",
                },
            ]
        )
        _patch_meta(
            seeded_meta,
            monkeypatch,
            get_dataflow_table_structure=lambda did, tid: {
                "hierarchy_name": "H1",
                "indicators": hier,
            },
            fetch_availability=lambda did, pinned=None: {
                "UNIT_MEASURE": ["XDC", "PT_B1GQ"]
            },
        )
        qb = _qb_stub(seeded_meta)

        def _fetch(**kwargs):
            if (kwargs.get("dimension_filters") or {}).get("UNIT_MEASURE") == "PT_B1GQ":
                return {"data": pct_rows, "metadata": {"url": "u2"}}
            return {"data": primary_rows, "metadata": {"url": "u1"}}

        qb.fetch_data.side_effect = _fetch
        tb = OecdTableBuilder(metadata=seeded_meta, query_builder=qb)
        result = tb.get_table(dataflow=_SHORT_ID)
        pct = [r for r in result["data"] if r["label"] == "% of GDP"]
        assert pct
        assert any("adjustment" in r for r in pct)
