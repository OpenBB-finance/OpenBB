"""Tests for openbb_oecd.utils.metadata._search_mixin."""

from __future__ import annotations

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

_FULL_ID = "DSD_TEST@DF_TEST"
_SHORT_ID = "DF_TEST"


class TestSearchDataflows:
    def test_empty_query_returns_all(self, seeded_meta):
        """Empty query string returns every dataflow."""
        result = seeded_meta.search_dataflows("")
        assert len(result) == 1
        assert result[0]["id"] == _FULL_ID

    def test_whitespace_query_returns_all(self, seeded_meta):
        """Whitespace-only query returns every dataflow."""
        result = seeded_meta.search_dataflows("   ")
        assert len(result) == 1

    def test_match_by_name(self, seeded_meta):
        """Single term that matches the dataflow name."""
        result = seeded_meta.search_dataflows("test")
        assert len(result) == 1
        assert result[0]["short_id"] == _SHORT_ID

    def test_match_by_short_id(self, seeded_meta):
        """Single term matching the short id."""
        result = seeded_meta.search_dataflows("DF_TEST")
        assert len(result) == 1

    def test_multi_term_and_logic(self, seeded_meta):
        """All terms must appear in the searchable text."""
        result = seeded_meta.search_dataflows("test dataflow")
        assert len(result) == 1

    def test_multi_term_no_match(self, seeded_meta):
        """Missing any term excludes the dataflow."""
        result = seeded_meta.search_dataflows("test absent")
        assert result == []

    def test_no_match_returns_empty(self, seeded_meta):
        """No matches returns an empty list."""
        result = seeded_meta.search_dataflows("nonexistentquery")
        assert result == []


def _seed_indicators(meta, indicators):
    """Helper: seed the indicator cache for the seeded dataflow."""
    meta._dataflow_indicators_cache[_FULL_ID] = indicators


class TestSearchIndicatorsScoped:
    def test_scoped_string_dataflow_resolves_short_id(self, seeded_meta):
        """A short-id string in dataflows resolves via _short_id_map."""
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "CPI",
                    "label": "Consumer Price Index",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "Prices",
                    "symbol": "x::CPI",
                },
            ],
        )
        result = seeded_meta.search_indicators(dataflows=_SHORT_ID)
        assert len(result) == 1
        assert result[0]["indicator"] == "CPI"

    def test_scoped_full_id_direct_hit(self, seeded_meta):
        """A full id already in the cache hits the direct branch."""
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "CPI",
                    "label": "CPI",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta.search_indicators(dataflows=[_FULL_ID])
        assert len(result) == 1

    def test_scoped_unknown_id_skipped(self, seeded_meta):
        """Dataflow ids that don't resolve are silently skipped."""
        _seed_indicators(seeded_meta, [])
        result = seeded_meta.search_indicators(dataflows=["NONEXISTENT_XYZ"])
        assert result == []

    def test_scoped_filters_table_dim(self, seeded_meta):
        """Indicators whose dimension_id is in _TABLE_GROUP_CANDIDATES are skipped."""
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "T01",
                    "label": "Table 1",
                    "dimension_id": "TABLE_IDENTIFIER",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
                {
                    "indicator": "CPI",
                    "label": "CPI",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta.search_indicators(dataflows=_SHORT_ID)
        codes = [r["indicator"] for r in result]
        assert "T01" not in codes
        assert "CPI" in codes

    def test_scoped_filters_non_indicator_dim(self, seeded_meta):
        """Indicators whose dim doesn't match the indicator dim are skipped."""
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "X",
                    "label": "Foreign dim",
                    "dimension_id": "OTHER",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
                {
                    "indicator": "CPI",
                    "label": "CPI",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta.search_indicators(dataflows=_SHORT_ID)
        codes = [r["indicator"] for r in result]
        assert "X" not in codes
        assert "CPI" in codes

    def test_scoped_constraint_filters_out_unallowed(self, seeded_meta):
        """Indicators not in the allowed constraint set are filtered out."""
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "CPI",
                    "label": "CPI",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
                {
                    "indicator": "PPI",
                    "label": "PPI",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta.search_indicators(dataflows=_SHORT_ID)
        codes = [r["indicator"] for r in result]
        assert "CPI" in codes
        assert "PPI" not in codes

    def test_scoped_no_constraints_branch(self, seeded_meta):
        """When there are no constraints, the unconstrained extend branch runs."""
        seeded_meta._dataflow_constraints.pop(_FULL_ID, None)
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "CPI",
                    "label": "CPI",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
                {
                    "indicator": "T01",
                    "label": "Table 1",
                    "dimension_id": "TABLE_IDENTIFIER",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
                {
                    "indicator": "X",
                    "label": "Foreign",
                    "dimension_id": "OTHER",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta.search_indicators(dataflows=_SHORT_ID)
        codes = [r["indicator"] for r in result]
        assert "CPI" in codes
        assert "T01" not in codes
        assert "X" not in codes

    def test_scoped_query_filter_applied(self, seeded_meta):
        """Query phrase narrows the scoped result set."""
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "CPI",
                    "label": "Consumer Price Index",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "Prices",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta.search_indicators(query="consumer", dataflows=_SHORT_ID)
        assert len(result) == 1


class TestSearchIndicatorsUnscoped:
    def test_unscoped_requires_at_least_one_param(self, seeded_meta):
        """Raises when no query, dataflows, or keywords are passed."""
        with pytest.raises(OpenBBError, match="At least one"):
            seeded_meta.search_indicators()

    def test_unscoped_query_uses_search_index(self, seeded_meta):
        """Unscoped path builds and uses the search index."""
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "CPI",
                    "label": "Consumer Price Index",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "Prices",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta.search_indicators(query="consumer")
        assert len(result) == 1
        assert result[0]["indicator"] == "CPI"

    def test_unscoped_query_no_match(self, seeded_meta):
        """No matching indicator yields empty result."""
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "CPI",
                    "label": "Consumer Price Index",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "Prices",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta.search_indicators(query="unemployment")
        assert result == []

    def test_unscoped_keywords_only(self, seeded_meta):
        """keywords alone (no query) is enough for an unscoped search."""
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "CPI",
                    "label": "Consumer Price Index",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "Prices",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta.search_indicators(keywords="consumer")
        assert len(result) == 1


class TestSearchIndicatorsKeywords:
    def test_keyword_string_normalized_to_list(self, seeded_meta):
        """A string keyword is wrapped into a single-item list."""
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "CPI",
                    "label": "Consumer Price Index",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta.search_indicators(dataflows=_SHORT_ID, keywords="consumer")
        assert len(result) == 1

    def test_include_keyword_filters_in(self, seeded_meta):
        """Plain keyword includes only indicators that contain it."""
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "CPI",
                    "label": "Consumer Price Index",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta.search_indicators(
            dataflows=_SHORT_ID, keywords=["consumer"]
        )
        codes = [r["indicator"] for r in result]
        assert codes == ["CPI"]

    def test_not_keyword_excludes(self, seeded_meta):
        """A keyword prefixed with 'not' excludes matches."""
        seeded_meta._dataflow_constraints.pop(_FULL_ID, None)
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "CPI",
                    "label": "Consumer Price Index",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
                {
                    "indicator": "UNE",
                    "label": "Unemployment Rate",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta.search_indicators(
            dataflows=_SHORT_ID, keywords=["not consumer"]
        )
        codes = [r["indicator"] for r in result]
        assert "CPI" not in codes
        assert "UNE" in codes


class TestGetSearchIndex:
    def test_returns_cached_when_present(self, seeded_meta):
        """When _search_index is already set, returns it directly."""
        cached = [("dummy", {"indicator": "X"})]
        seeded_meta._search_index = cached
        assert seeded_meta._get_search_index() is cached

    def test_builds_index_when_missing(self, seeded_meta):
        """Index is built lazily from _dataflow_indicators_cache."""
        seeded_meta._search_index = None
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "CPI",
                    "label": "Consumer Price Index",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "Prices",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta._get_search_index()
        assert len(result) == 1
        text, ind = result[0]
        assert "consumer price index" in text
        assert ind["indicator"] == "CPI"

    def test_index_skips_table_dim(self, seeded_meta):
        """Indicators in table-group dimensions are not indexed."""
        seeded_meta._search_index = None
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "T01",
                    "label": "Table 1",
                    "dimension_id": "TABLE_IDENTIFIER",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
                {
                    "indicator": "CPI",
                    "label": "CPI",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta._get_search_index()
        codes = [ind["indicator"] for _, ind in result]
        assert "T01" not in codes
        assert "CPI" in codes

    def test_index_skips_mismatched_dim(self, seeded_meta):
        """Indicators whose dim doesn't match the indicator dim are skipped."""
        seeded_meta._search_index = None
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "FOREIGN",
                    "label": "Foreign dim",
                    "dimension_id": "OTHER",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
                {
                    "indicator": "CPI",
                    "label": "CPI",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta._get_search_index()
        codes = [ind["indicator"] for _, ind in result]
        assert "FOREIGN" not in codes

    def test_index_skips_unallowed_constraint(self, seeded_meta):
        """Indicators not in the allowed constraint set are skipped."""
        seeded_meta._search_index = None
        _seed_indicators(
            seeded_meta,
            [
                {
                    "indicator": "CPI",
                    "label": "CPI",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
                {
                    "indicator": "PPI",
                    "label": "PPI",
                    "dimension_id": "MEASURE",
                    "dataflow_id": _SHORT_ID,
                    "dataflow_name": "Test",
                    "description": "",
                    "symbol": "",
                },
            ],
        )
        result = seeded_meta._get_search_index()
        codes = [ind["indicator"] for _, ind in result]
        assert "CPI" in codes
        assert "PPI" not in codes

    def test_index_persists_on_instance(self, seeded_meta):
        """After building, _search_index is set on the instance."""
        seeded_meta._search_index = None
        _seed_indicators(seeded_meta, [])
        seeded_meta._get_search_index()
        assert seeded_meta._search_index is not None


class TestListTables:
    def _seed_taxonomy(self, meta):
        meta._taxonomy_loaded = True
        meta._taxonomy_tree = [
            {
                "id": "ECO",
                "name": "Economy",
                "path": "ECO",
                "children": [
                    {
                        "id": "PRICES",
                        "name": "Prices",
                        "path": "ECO.PRICES",
                        "children": [],
                    }
                ],
            }
        ]
        meta._category_to_dfs = {"ECO.PRICES": [_FULL_ID]}
        meta._df_to_categories = {_FULL_ID: ["ECO.PRICES"]}
        meta._category_names = {"ECO": "Economy", "ECO.PRICES": "Prices"}

    def test_no_args_returns_all(self, seeded_meta):
        """With no filters, list_tables returns the full table map."""
        self._seed_taxonomy(seeded_meta)
        result = seeded_meta.list_tables()
        assert len(result) == 1
        assert result[0]["table_id"] == _SHORT_ID
        assert result[0]["dataflow_id"] == _FULL_ID

    def test_query_path(self, seeded_meta):
        """A query routes through find_tables."""
        self._seed_taxonomy(seeded_meta)
        result = seeded_meta.list_tables(query="Test")
        assert len(result) == 1

    def test_topic_filter_match(self, seeded_meta):
        """Topic filter keeps only matching rows."""
        self._seed_taxonomy(seeded_meta)
        result = seeded_meta.list_tables(topic="eco")
        assert len(result) == 1

    def test_topic_filter_no_match(self, seeded_meta):
        """Non-matching topic returns empty list."""
        self._seed_taxonomy(seeded_meta)
        result = seeded_meta.list_tables(topic="HEA")
        assert result == []

    def test_subtopic_filter_match(self, seeded_meta):
        """Subtopic filter keeps only matching rows."""
        self._seed_taxonomy(seeded_meta)
        result = seeded_meta.list_tables(subtopic="prices")
        assert len(result) == 1

    def test_subtopic_filter_no_match(self, seeded_meta):
        """Non-matching subtopic returns empty list."""
        self._seed_taxonomy(seeded_meta)
        result = seeded_meta.list_tables(subtopic="OTHER")
        assert result == []


class TestGetTable:
    def test_delegates_to_describe_dataflow(self, seeded_meta):
        """get_table is a passthrough to describe_dataflow."""
        _seed_indicators(seeded_meta, [])
        result = seeded_meta.get_table(_SHORT_ID)
        assert result["dataflow_id"] == _FULL_ID


class TestGetDataflowHierarchies:
    def test_no_table_dim_returns_empty(self, seeded_meta):
        """Without a TABLE_IDENTIFIER/CHAPTER dim, returns empty list."""
        result = seeded_meta.get_dataflow_hierarchies(_SHORT_ID)
        assert result == []

    def test_with_table_identifier(self, seeded_meta):
        """Returns one entry per table group when TABLE_IDENTIFIER present."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "TABLE_IDENTIFIER",
                "position": 99,
                "codelist_id": "OECD:CL_TBL(1.0)",
                "concept_id": "TABLE_IDENTIFIER",
                "name": "Table",
            }
        )
        seeded_meta.codelists["OECD:CL_TBL(1.0)"] = {
            "T01": "Table One",
            "T02": "Table Two",
        }
        seeded_meta._dataflow_constraints[_FULL_ID]["TABLE_IDENTIFIER"] = [
            "T01",
            "T02",
        ]
        seeded_meta._dataflow_parameters_cache.pop(_FULL_ID, None)
        result = seeded_meta.get_dataflow_hierarchies(_SHORT_ID)
        assert len(result) == 2
        first = next(r for r in result if r["id"] == "T01")
        assert first["name"] == "Table One"
        assert first["codelist_id"] == "OECD:CL_TBL(1.0)"

    def test_chapter_dim_also_matched(self, seeded_meta):
        """CHAPTER also counts as a table group dim."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "CHAPTER",
                "position": 99,
                "codelist_id": "OECD:CL_CHAP(1.0)",
                "concept_id": "CHAPTER",
                "name": "Chapter",
            }
        )
        seeded_meta.codelists["OECD:CL_CHAP(1.0)"] = {"C1": "Chapter One"}
        seeded_meta._dataflow_constraints[_FULL_ID]["CHAPTER"] = ["C1"]
        seeded_meta._dataflow_parameters_cache.pop(_FULL_ID, None)
        result = seeded_meta.get_dataflow_hierarchies(_SHORT_ID)
        assert len(result) == 1
        assert result[0]["id"] == "C1"
        assert result[0]["codelist_id"] == "OECD:CL_CHAP(1.0)"


class TestGetDataflowTableStructure:
    def test_uses_table_meta_label(self, seeded_meta, monkeypatch):
        """When the table_id exists in groups, uses its label as hierarchy name."""
        monkeypatch.setattr(
            type(seeded_meta),
            "get_table_groups",
            lambda self, did: [{"value": "T01", "label": "Table One"}],
        )
        monkeypatch.setattr(
            type(seeded_meta),
            "get_indicator_tree",
            lambda self, did: [
                {
                    "code": "A",
                    "label": "Alpha",
                    "children": [
                        {"code": "B", "label": "Beta", "children": []},
                    ],
                },
                {"code": "C", "label": "Gamma", "children": []},
            ],
        )
        result = seeded_meta.get_dataflow_table_structure(_SHORT_ID, "T01")
        assert result["hierarchy_id"] == "T01"
        assert result["hierarchy_name"] == "Table One"
        codes = [item["code"] for item in result["indicators"]]
        assert codes == ["A", "B", "C"]
        levels = {item["code"]: item["level"] for item in result["indicators"]}
        assert levels == {"A": 0, "B": 1, "C": 0}
        parents = {item["code"]: item["parent"] for item in result["indicators"]}
        assert parents == {"A": None, "B": "A", "C": None}
        children_of_a = next(
            item for item in result["indicators"] if item["code"] == "A"
        )["children"]
        assert children_of_a == ["B"]

    def test_unknown_table_id_falls_back_to_id(self, seeded_meta, monkeypatch):
        """When table_id is not in groups, hierarchy_name falls back to the id."""
        monkeypatch.setattr(type(seeded_meta), "get_table_groups", lambda self, did: [])
        monkeypatch.setattr(
            type(seeded_meta), "get_indicator_tree", lambda self, did: []
        )
        result = seeded_meta.get_dataflow_table_structure(_SHORT_ID, "UNKNOWN")
        assert result["hierarchy_name"] == "UNKNOWN"
        assert result["indicators"] == []

    def test_node_without_label_uses_code(self, seeded_meta, monkeypatch):
        """When a tree node lacks a 'label', the code is used as fallback."""
        monkeypatch.setattr(type(seeded_meta), "get_table_groups", lambda self, did: [])
        monkeypatch.setattr(
            type(seeded_meta),
            "get_indicator_tree",
            lambda self, did: [{"code": "X", "children": []}],
        )
        result = seeded_meta.get_dataflow_table_structure(_SHORT_ID, "T1")
        assert result["indicators"][0]["label"] == "X"


class TestDescribeDataflowLeafCount:
    def test_count_leaves_with_nested_children(self, seeded_meta, monkeypatch):
        """_count_leaves recurses through children and counts the leaves."""
        _seed_indicators(seeded_meta, [])
        monkeypatch.setattr(
            type(seeded_meta),
            "get_indicator_tree",
            lambda self, did: [
                {
                    "code": "A",
                    "label": "A",
                    "children": [
                        {"code": "B", "label": "B", "children": []},
                        {"code": "C", "label": "C", "children": []},
                    ],
                },
                {"code": "D", "label": "D", "children": []},
            ],
        )
        result = seeded_meta.describe_dataflow(_SHORT_ID)
        assert result["indicator_count"] == 3
