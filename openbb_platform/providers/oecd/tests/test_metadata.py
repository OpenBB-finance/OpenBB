"""Comprehensive unit tests for openbb_oecd.utils.metadata.

All tests are entirely offline — no network calls are made.
HTTP is mocked via unittest.mock wherever _ensure_* methods are exercised.
The OecdMetadata singleton is reset between every test that uses it.
"""

from __future__ import annotations

import gzip
import json
import lzma
import threading
import warnings
from unittest.mock import MagicMock, patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_oecd.utils.metadata import (
    OecdMetadata,
    _build_code_tree,
    _extract_codelist_id_from_urn,
    _extract_concept_id_from_urn,
    _matches_query,
    _normalize_label,
    _parse_sdmx_json_codelists,
    _parse_search_query,
    _term_matches,
)
from openbb_oecd.utils.metadata._cache_mixin import CacheMixin
from openbb_oecd.utils.metadata._helpers import _get_user_cache_file

_FULL_ID = "DSD_TEST@DF_TEST"
_SHORT_ID = "DF_TEST"

_TEST_DATAFLOW = {
    "id": _FULL_ID,
    "short_id": _SHORT_ID,
    "agency_id": "OECD",
    "version": "1.0",
    "name": "Test Dataflow",
    "description": "",
    "structure_ref": "",
}

_TEST_DSD = {
    "dsd_id": "DSD_TEST",
    "agency_id": "OECD",
    "version": "1.0",
    "dimensions": [
        {
            "id": "REF_AREA",
            "position": 1,
            "codelist_id": "OECD:CL_AREA(1.0)",
            "concept_id": "REF_AREA",
            "name": "Reference Area",
        },
        {
            "id": "MEASURE",
            "position": 2,
            "codelist_id": "OECD:CL_MEASURE(1.0)",
            "concept_id": "MEASURE",
            "name": "Measure",
        },
        {
            "id": "FREQ",
            "position": 3,
            "codelist_id": "OECD:CL_FREQ(1.0)",
            "concept_id": "FREQ",
            "name": "Frequency",
        },
    ],
    "attributes": [],
    "has_time_dimension": True,
}

_TEST_CODELISTS = {
    "OECD:CL_AREA(1.0)": {
        "USA": "United States",
        "GBR": "United Kingdom",
        "DEU": "Germany",
    },
    "OECD:CL_MEASURE(1.0)": {
        "CPI": "Consumer Price Index",
        "PPI": "Producer Price Index",
    },
    "OECD:CL_FREQ(1.0)": {"A": "Annual", "Q": "Quarterly", "M": "Monthly"},
}

_TEST_CONSTRAINTS = {
    _FULL_ID: {
        "REF_AREA": ["USA", "GBR"],
        "MEASURE": ["CPI"],
        "FREQ": ["A", "Q"],
    }
}


@pytest.fixture
def meta(monkeypatch):
    """Yield a fresh, empty OecdMetadata instance with test data pre-loaded."""
    OecdMetadata._reset()
    monkeypatch.setattr(OecdMetadata, "_load_from_cache", lambda self: True)
    instance = OecdMetadata()
    # Inject minimal test data so tests don't need the network.
    instance.dataflows[_FULL_ID] = _TEST_DATAFLOW.copy()
    instance._short_id_map[_SHORT_ID] = _FULL_ID
    instance._full_catalogue_loaded = True
    instance.datastructures[_FULL_ID] = {
        k: list(v) if isinstance(v, list) else v for k, v in _TEST_DSD.items()
    }
    instance.datastructures[_FULL_ID]["dimensions"] = [
        dict(d) for d in _TEST_DSD["dimensions"]
    ]
    instance.codelists.update({k: dict(v) for k, v in _TEST_CODELISTS.items()})
    instance._dataflow_constraints.update(
        {
            k: {dk: list(dv) for dk, dv in v.items()}
            for k, v in _TEST_CONSTRAINTS.items()
        }
    )
    yield instance
    OecdMetadata._reset()


# ===========================================================================
# 1.  Pure module-level functions
# ===========================================================================


class TestNormalizeLabel:
    def test_basic_replacement(self):
        assert _normalize_label("United States") == "united_states"

    def test_hyphen_to_underscore(self):
        assert _normalize_label("Czech-Republic") == "czech_republic"

    def test_parenthetical_stripped(self):
        assert _normalize_label("Korea (Republic of)") == "korea"

    def test_comma_suffix_stripped(self):
        assert _normalize_label("China, People's Republic of") == "china"

    def test_leading_trailing_underscores(self):
        assert not _normalize_label("  Germany  ").startswith("_")
        assert not _normalize_label("  Germany  ").endswith("_")

    def test_multiple_spaces_collapsed(self):
        assert _normalize_label("New   Zealand") == "new_zealand"

    def test_already_normalized(self):
        assert _normalize_label("france") == "france"

    def test_all_caps(self):
        result = _normalize_label("USA")
        assert result == "usa"


class TestBuildCodeTree:
    def test_flat_no_parents(self):
        codes = {"A": "Alpha", "B": "Beta", "C": "Gamma"}
        tree = _build_code_tree(codes, {}, {})
        assert len(tree) == 3
        assert all(n["children"] == [] for n in tree)
        labels = [n["label"] for n in tree]
        assert labels == sorted(labels)

    def test_child_attached_to_parent(self):
        codes = {"P": "Parent", "C": "Child"}
        parents = {"C": "P"}
        tree = _build_code_tree(codes, parents, {})
        root_codes = [n["code"] for n in tree]
        assert "P" in root_codes
        assert "C" not in root_codes
        parent_node = next(n for n in tree if n["code"] == "P")
        assert len(parent_node["children"]) == 1
        assert parent_node["children"][0]["code"] == "C"

    def test_description_fallback_to_label(self):
        codes = {"X": "Label X"}
        tree = _build_code_tree(codes, {}, {})
        assert tree[0]["description"] == "Label X"

    def test_description_override(self):
        codes = {"X": "Label X"}
        descs = {"X": "Custom description"}
        tree = _build_code_tree(codes, {}, descs)
        assert tree[0]["description"] == "Custom description"

    def test_orphaned_parent_reference(self):
        """Child referencing a non-existent parent becomes a root."""
        codes = {"C": "Child Only"}
        parents = {"C": "MISSING_PARENT"}
        tree = _build_code_tree(codes, parents, {})
        assert len(tree) == 1
        assert tree[0]["code"] == "C"

    def test_sorting(self):
        codes = {"Z": "Zebra", "A": "Apple", "M": "Mango"}
        tree = _build_code_tree(codes, {}, {})
        labels = [n["label"] for n in tree]
        assert labels == sorted(labels)

    def test_empty(self):
        assert _build_code_tree({}, {}, {}) == []

    def test_multi_level_hierarchy(self):
        codes = {"G": "Grand", "P": "Parent", "C": "Child"}
        parents = {"P": "G", "C": "P"}
        tree = _build_code_tree(codes, parents, {})
        assert len(tree) == 1
        grand = tree[0]
        assert grand["code"] == "G"
        assert len(grand["children"]) == 1
        parent_node = grand["children"][0]
        assert parent_node["code"] == "P"
        assert len(parent_node["children"]) == 1
        assert parent_node["children"][0]["code"] == "C"


class TestParseSdmxJsonCodelists:
    def _make_raw(self, codelists_data):
        return {"data": {"codelists": codelists_data}}

    def test_basic_codelist(self):
        raw = self._make_raw(
            [
                {
                    "id": "CL_TEST",
                    "agencyID": "OECD",
                    "version": "1.0",
                    "codes": [
                        {"id": "A", "names": {"en": "Apple"}},
                        {"id": "B", "names": {"en": "Banana"}},
                    ],
                }
            ]
        )
        cls, parents = _parse_sdmx_json_codelists(raw)
        assert "OECD:CL_TEST(1.0)" in cls
        assert cls["OECD:CL_TEST(1.0)"]["A"] == "Apple"
        assert cls["OECD:CL_TEST(1.0)"]["B"] == "Banana"
        assert parents == {}

    def test_parent_hierarchy(self):
        raw = self._make_raw(
            [
                {
                    "id": "CL_H",
                    "agencyID": "OECD",
                    "version": "2.0",
                    "codes": [
                        {"id": "P", "names": {"en": "Parent"}},
                        {"id": "C", "names": {"en": "Child"}, "parent": "P"},
                    ],
                }
            ]
        )
        _, parents = _parse_sdmx_json_codelists(raw)
        key = "OECD:CL_H(2.0)"
        assert key in parents
        assert parents[key]["C"] == "P"
        assert "P" not in parents[key]  # parent itself has no parent

    def test_name_fallback(self):
        """Falls back to 'name' string when 'names' dict is absent."""
        raw = self._make_raw(
            [
                {
                    "id": "CL_FALLBACK",
                    "agencyID": "OECD",
                    "version": "1.0",
                    "codes": [{"id": "X", "name": "Fallback Label"}],
                }
            ]
        )
        cls, _ = _parse_sdmx_json_codelists(raw)
        assert cls["OECD:CL_FALLBACK(1.0)"]["X"] == "Fallback Label"

    def test_empty_codelists(self):
        raw = self._make_raw([])
        cls, parents = _parse_sdmx_json_codelists(raw)
        assert cls == {}
        assert parents == {}

    def test_missing_data_key(self):
        raw = {"codelists": []}
        cls, _ = _parse_sdmx_json_codelists(raw)
        assert cls == {}

    def test_multiple_codelists(self):
        raw = self._make_raw(
            [
                {
                    "id": "CL_A",
                    "agencyID": "OECD",
                    "version": "1.0",
                    "codes": [{"id": "X", "names": {"en": "Ex"}}],
                },
                {
                    "id": "CL_B",
                    "agencyID": "OECD",
                    "version": "1.0",
                    "codes": [{"id": "Y", "names": {"en": "Why"}}],
                },
            ]
        )
        cls, _ = _parse_sdmx_json_codelists(raw)
        assert "OECD:CL_A(1.0)" in cls
        assert "OECD:CL_B(1.0)" in cls

    def test_id_fallback_code_label(self):
        """When names dict lang key absent, falls back to code id."""
        raw = self._make_raw(
            [
                {
                    "id": "CL_X",
                    "agencyID": "OECD",
                    "version": "1.0",
                    "codes": [{"id": "FOO", "names": {}}],
                }
            ]
        )
        cls, _ = _parse_sdmx_json_codelists(raw)
        assert cls["OECD:CL_X(1.0)"]["FOO"] == "FOO"


class TestExtractCodelistIdFromUrn:
    def test_full_qualified_urn(self):
        urn = "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=OECD.SDD.TPS:CL_REF_AREA(3.0)"
        result = _extract_codelist_id_from_urn(urn)
        assert result == "OECD.SDD.TPS:CL_REF_AREA(3.0)"

    def test_simple_urn(self):
        urn = "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=OECD:CL_FREQ(2.1)"
        result = _extract_codelist_id_from_urn(urn)
        assert result == "OECD:CL_FREQ(2.1)"

    def test_no_version_fallback(self):
        urn = "some:CL_TEST"
        result = _extract_codelist_id_from_urn(urn)
        assert "CL_TEST" in result

    def test_plain_string_passthrough(self):
        result = _extract_codelist_id_from_urn("PLAIN")
        assert result == "PLAIN"


class TestExtractConceptIdFromUrn:
    def test_dotted_urn(self):
        urn = (
            "urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept=OECD:CS_COMMON(2.0).FREQ"
        )
        assert _extract_concept_id_from_urn(urn) == "FREQ"

    def test_no_dot(self):
        assert _extract_concept_id_from_urn("MEASURE") == "MEASURE"

    def test_nested_dot(self):
        urn = "urn:sdmx:...=OECD:CS(1.0).SECTOR.SUB"
        assert _extract_concept_id_from_urn(urn) == "SUB"


class TestParseSearchQuery:
    def test_single_term(self):
        result = _parse_search_query("GDP")
        assert result == [["gdp"]]

    def test_multiple_terms_implicit_and(self):
        result = _parse_search_query("consumer price index")
        assert result == [["consumer", "price", "index"]]

    def test_semicolon_or(self):
        result = _parse_search_query("GDP; CPI")
        assert result == [["gdp"], ["cpi"]]

    def test_empty_string(self):
        assert _parse_search_query("") == []

    def test_whitespace_only(self):
        assert _parse_search_query("   ") == []

    def test_pipe_preserved_in_term(self):
        result = _parse_search_query("gdp|gross")
        assert result == [["gdp|gross"]]

    def test_mixed_case_lowercased(self):
        result = _parse_search_query("GDP Consumer")
        assert result == [["gdp", "consumer"]]


class TestMatchesQuery:
    def test_empty_phrases_always_true(self):
        assert _matches_query("anything", []) is True

    def test_single_phrase_match(self):
        assert _matches_query("consumer price index", [["consumer"]]) is True

    def test_single_phrase_no_match(self):
        assert _matches_query("unemployment rate", [["cpi"]]) is False

    def test_and_logic(self):
        assert _matches_query("consumer price index", [["consumer", "price"]]) is True
        assert _matches_query("consumer goods index", [["consumer", "price"]]) is False

    def test_or_phrases(self):
        # "GDP" OR "CPI"
        phrases = [["gdp"], ["cpi"]]
        assert _matches_query("consumer price index cpi", phrases) is True
        assert _matches_query("gdp growth", phrases) is True
        assert _matches_query("unemployment", phrases) is False

    def test_pipe_or_within_term(self):
        phrases = [["gdp|gross"]]
        assert _matches_query("gross domestic product", phrases) is True
        assert _matches_query("gdp per capita", phrases) is True
        assert _matches_query("inflation rate", phrases) is False


class TestTermMatches:
    def test_simple_match(self):
        assert _term_matches("hello world", "world") is True

    def test_simple_no_match(self):
        assert _term_matches("hello world", "foo") is False

    def test_pipe_or(self):
        assert _term_matches("hello world", "hello|goodbye") is True
        assert _term_matches("hello world", "foo|bar") is False

    def test_empty_alternatives_stripped(self):
        # pipe with empty side
        assert _term_matches("hello", "hello|") is True


class TestSingleton:
    def test_singleton_returns_same_instance(self, meta):
        """Two OecdMetadata() calls return the exact same object."""
        instance2 = OecdMetadata()
        assert meta is instance2

    def test_deepcopy_returns_self(self, meta):
        """``deepcopy`` on the singleton must return the same instance, not walk it."""
        from copy import deepcopy

        assert deepcopy(meta) is meta

    def test_copy_returns_self(self, meta):
        """``copy`` on the singleton must return the same instance."""
        from copy import copy

        assert copy(meta) is meta

    def test_reset_creates_new_instance(self, monkeypatch):
        """After _reset, a new instance is created."""
        OecdMetadata._reset()
        monkeypatch.setattr(OecdMetadata, "_load_from_cache", lambda self: True)
        a = OecdMetadata()
        OecdMetadata._reset()
        monkeypatch.setattr(OecdMetadata, "_load_from_cache", lambda self: True)
        b = OecdMetadata()
        assert a is not b
        OecdMetadata._reset()

    def test_thread_safety(self, monkeypatch):
        """Concurrent instantiation always yields the same object."""
        OecdMetadata._reset()
        monkeypatch.setattr(OecdMetadata, "_load_from_cache", lambda self: True)
        instances = []

        def get_instance():
            instances.append(OecdMetadata())

        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(set(id(i) for i in instances)) == 1
        OecdMetadata._reset()


class TestApplyBlob:
    def test_basic_blob_population(self, meta):
        blob = {
            "dataflows": {
                "DSD_X@DF_Y": {"id": "DSD_X@DF_Y", "short_id": "DF_Y", "name": "Y"}
            },
            "codelists": {"OECD:CL_NEW(1.0)": {"A": "Alpha"}},
            "short_id_map": {"DF_Y": "DSD_X@DF_Y"},
            "taxonomy_tree": [],
        }
        meta._apply_blob(blob)
        assert "DSD_X@DF_Y" in meta.dataflows
        assert "OECD:CL_NEW(1.0)" in meta.codelists

    def test_blob_compact_indicators(self, meta):
        blob = {
            "dataflow_indicators": {
                _FULL_ID: {
                    "dim_id": "MEASURE",
                    "codes": [
                        {"indicator": "CPI", "label": "Consumer Price Index"},
                        {
                            "indicator": "PPI",
                            "label": "Producer Price Index",
                            "parent": "CPI",
                        },
                    ],
                }
            }
        }
        meta._apply_blob(blob)
        expanded = meta._dataflow_indicators_cache.get(_FULL_ID, [])
        assert len(expanded) == 2
        assert expanded[0]["indicator"] == "CPI"
        assert expanded[1]["parent"] == "CPI"
        assert "symbol" in expanded[0]

    def test_blob_taxonomy_loaded_flag(self, meta):
        meta._taxonomy_loaded = False
        blob = {
            "taxonomy_tree": [
                {"id": "ECO", "name": "Economy", "path": "ECO", "children": []}
            ],
            "df_to_categories": {},
            "category_to_dfs": {},
            "category_names": {"ECO": "Economy"},
        }
        meta._apply_blob(blob)
        assert meta._taxonomy_loaded is True
        assert meta._taxonomy_tree[0]["id"] == "ECO"

    def test_blob_descriptions_baked_flag(self, meta):
        """``descriptions_baked: True`` sets the runtime flag."""
        meta._descriptions_baked = False
        meta._apply_blob({"descriptions_baked": True})
        assert meta._descriptions_baked is True

    def test_blob_smaller_taxonomy_does_not_regress(self, meta):
        """A smaller incoming tree must not overwrite a larger already-loaded tree."""
        meta._taxonomy_tree = [
            {"id": "A", "name": "A", "path": "A", "children": []},
            {"id": "B", "name": "B", "path": "B", "children": []},
            {"id": "C", "name": "C", "path": "C", "children": []},
        ]
        meta._taxonomy_loaded = False
        meta._apply_blob(
            {
                "taxonomy_tree": [
                    {"id": "STUB", "name": "Stub", "path": "STUB", "children": []}
                ],
                "category_to_dfs": {"STUB": ["x"]},
            }
        )
        assert [t["id"] for t in meta._taxonomy_tree] == ["A", "B", "C"]
        assert meta._taxonomy_loaded is True
        assert meta._category_to_dfs.get("STUB") is None


class TestResolveDataflowId:
    def test_full_id_passthrough(self, meta):
        assert meta._resolve_dataflow_id(_FULL_ID) == _FULL_ID

    def test_short_id_resolution(self, meta):
        assert meta._resolve_dataflow_id(_SHORT_ID) == _FULL_ID

    def test_unknown_id_raises(self, meta):
        meta._full_catalogue_loaded = True  # prevent network call
        with pytest.raises(OpenBBError, match="Unknown OECD dataflow"):
            meta._resolve_dataflow_id("DF_NONEXISTENT_XYZ")


class TestListDataflows:
    def test_returns_all_when_no_filter(self, meta):
        meta._taxonomy_loaded = True
        result = meta.list_dataflows()
        assert len(result) == 1
        assert result[0]["value"] == _FULL_ID

    def test_topic_filter_match(self, meta):
        meta._taxonomy_loaded = True
        meta._df_to_categories[_FULL_ID] = ["ECO.PRICES"]
        result = meta.list_dataflows(topic="ECO")
        assert len(result) == 1

    def test_topic_filter_no_match(self, meta):
        meta._taxonomy_loaded = True
        meta._df_to_categories[_FULL_ID] = ["ECO.PRICES"]
        result = meta.list_dataflows(topic="HEA")
        assert result == []

    def test_result_sorted_by_value(self, meta):
        meta._taxonomy_loaded = True
        meta.dataflows["DSD_Z@DF_ZZZ"] = {
            "id": "DSD_Z@DF_ZZZ",
            "short_id": "DF_ZZZ",
            "name": "ZZZ",
            "description": "",
        }
        meta._short_id_map["DF_ZZZ"] = "DSD_Z@DF_ZZZ"
        result = meta.list_dataflows()
        values = [r["value"] for r in result]
        assert values == sorted(values)

    def test_result_includes_topic_names(self, meta):
        meta._taxonomy_loaded = True
        meta._df_to_categories[_FULL_ID] = ["ECO.PRICES"]
        meta._category_names["ECO"] = "Economy"
        meta._category_names["ECO.PRICES"] = "Prices"
        result = meta.list_dataflows()
        row = result[0]
        assert row["topic"] == "ECO"
        assert row["topic_name"] == "Economy"
        assert row["subtopic"] == "PRICES"
        assert row["subtopic_name"] == "Prices"


class TestListTopics:
    def _seed_taxonomy(self, meta):
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
                    },
                ],
            }
        ]
        meta._category_to_dfs = {
            "ECO": [],
            "ECO.PRICES": [_FULL_ID],
        }
        meta._taxonomy_loaded = True

    def test_basic_tree_structure(self, meta):
        self._seed_taxonomy(meta)
        result = meta.list_topics()
        assert len(result) == 1
        top = result[0]
        assert top["id"] == "ECO"
        assert top["dataflow_count"] == 1
        assert len(top["subtopics"]) == 1
        assert top["subtopics"][0]["id"] == "PRICES"

    def test_empty_subtopics_excluded(self, meta):
        """Subtopics with zero dataflows are dropped."""
        meta._taxonomy_tree = [
            {
                "id": "ECO",
                "name": "Economy",
                "path": "ECO",
                "children": [
                    {
                        "id": "EMPTY",
                        "name": "Empty",
                        "path": "ECO.EMPTY",
                        "children": [],
                    },
                    {
                        "id": "PRICES",
                        "name": "Prices",
                        "path": "ECO.PRICES",
                        "children": [],
                    },
                ],
            }
        ]
        meta._category_to_dfs = {"ECO.PRICES": [_FULL_ID]}
        meta._taxonomy_loaded = True
        topics = meta.list_topics()
        assert len(topics[0]["subtopics"]) == 1
        assert topics[0]["subtopics"][0]["id"] == "PRICES"


class TestParseCategoryTree:
    def test_flat_categories(self):
        cats = [
            {"id": "A", "names": {"en": "Alpha"}, "categories": []},
            {"id": "B", "names": {"en": "Beta"}, "categories": []},
        ]
        tree, names = OecdMetadata._parse_category_tree(cats)
        assert len(tree) == 2
        assert names["A"] == "Alpha"
        assert names["B"] == "Beta"

    def test_nested_categories(self):
        cats = [
            {
                "id": "ECO",
                "names": {"en": "Economy"},
                "categories": [
                    {"id": "CPI", "names": {"en": "Prices"}, "categories": []},
                ],
            }
        ]
        tree, names = OecdMetadata._parse_category_tree(cats)
        assert tree[0]["children"][0]["id"] == "CPI"
        assert "ECO.CPI" in names
        assert names["ECO.CPI"] == "Prices"

    def test_name_fallback(self):
        cats = [{"id": "X", "name": "Fallback Name", "categories": []}]
        _, names = OecdMetadata._parse_category_tree(cats)
        assert names["X"] == "Fallback Name"

    def test_path_prefixed_for_child(self):
        cats = [
            {
                "id": "TOP",
                "names": {"en": "Top"},
                "categories": [{"id": "SUB", "names": {"en": "Sub"}, "categories": []}],
            }
        ]
        _, names = OecdMetadata._parse_category_tree(cats, prefix="PARENT")
        assert "PARENT.TOP" in names
        assert "PARENT.TOP.SUB" in names


class TestParseCategorisations:
    def test_basic_mapping(self, meta):
        meta._df_to_categories = {}
        meta._category_to_dfs = {}
        # Test the regex patterns directly
        df_re = OecdMetadata._CATEGORISATION_DF_RE
        cat_re = OecdMetadata._CATEGORISATION_CAT_RE
        m_df = df_re.search("Dataflow=OECD:DSD_TEST@DF_TEST(1.0)")
        m_cat = cat_re.search("OECDCS1(v1).ECO.PRICES")
        assert m_df is not None
        assert m_cat is not None
        assert m_df.group(2) == "DSD_TEST@DF_TEST"
        assert m_cat.group(1) == "ECO.PRICES"


class TestGetDimensionOrder:
    def test_returns_dims_excluding_time_period(self, meta):
        order = meta.get_dimension_order(_SHORT_ID)
        assert "TIME_PERIOD" not in order
        assert order == ["REF_AREA", "MEASURE", "FREQ"]

    def test_full_id_works(self, meta):
        order = meta.get_dimension_order(_FULL_ID)
        assert order == ["REF_AREA", "MEASURE", "FREQ"]


class TestGetDataflowParameters:
    def test_basic_parameters(self, meta):
        params = meta.get_dataflow_parameters(_SHORT_ID)
        assert "REF_AREA" in params
        assert "MEASURE" in params
        assert "FREQ" in params
        assert "TIME_PERIOD" not in params

    def test_values_are_label_value_dicts(self, meta):
        params = meta.get_dataflow_parameters(_SHORT_ID)
        for entry in params["REF_AREA"]:
            assert "label" in entry
            assert "value" in entry

    def test_usa_in_ref_area(self, meta):
        params = meta.get_dataflow_parameters(_SHORT_ID)
        codes = {e["value"] for e in params["REF_AREA"]}
        assert "USA" in codes

    def test_cache_hit_returns_same_object(self, meta):
        p1 = meta.get_dataflow_parameters(_SHORT_ID)
        p2 = meta.get_dataflow_parameters(_SHORT_ID)
        assert p1 is p2

    def test_empty_codelist_dimension(self, meta):
        """Dimension with no codelist_id gets an empty list."""
        meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "NAKED",
                "position": 99,
                "codelist_id": "",
                "concept_id": "NAKED",
                "name": "Naked",
            }
        )
        params = meta.get_dataflow_parameters(_FULL_ID)
        assert params.get("NAKED") == []


class TestGetCodelistForDimension:
    def test_known_dimension(self, meta):
        result = meta.get_codelist_for_dimension(_SHORT_ID, "REF_AREA")
        assert "USA" in result
        assert result["USA"] == "United States"

    def test_unknown_dimension_returns_empty(self, meta):
        result = meta.get_codelist_for_dimension(_SHORT_ID, "NONEXISTENT")
        assert result == {}

    def test_time_period_returns_empty(self, meta):
        """TIME_PERIOD has no codelist_id → empty."""
        meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "TIME_PERIOD",
                "position": 99,
                "codelist_id": "",
                "concept_id": "TIME_PERIOD",
                "name": "Time",
            }
        )
        result = meta.get_codelist_for_dimension(_SHORT_ID, "TIME_PERIOD")
        assert result == {}


class TestResolveCountryCodes:
    def test_empty_input_returns_empty(self, meta):
        # Seed codelist so the country dim is resolvable.
        meta._dataflow_constraints.clear()
        assert meta.resolve_country_codes(_SHORT_ID, "") == []

    def test_all_returns_empty(self, meta):
        assert meta.resolve_country_codes(_SHORT_ID, "all") == []

    def test_uppercase_code_matched(self, meta):
        result = meta.resolve_country_codes(_SHORT_ID, "USA")
        assert result == ["USA"]

    def test_lowercase_code_matched(self, meta):
        result = meta.resolve_country_codes(_SHORT_ID, "usa")
        assert result == ["USA"]

    def test_label_matched(self, meta):
        result = meta.resolve_country_codes(_SHORT_ID, "United States")
        assert result == ["USA"]

    def test_normalized_label_matched(self, meta):
        result = meta.resolve_country_codes(_SHORT_ID, "united_states")
        assert result == ["USA"]

    def test_multiple_countries(self, meta):
        result = meta.resolve_country_codes(_SHORT_ID, "USA,GBR")
        assert "USA" in result
        assert "GBR" in result

    def test_invalid_country_raises(self, meta):
        with pytest.raises(OpenBBError, match="Invalid country"):
            meta.resolve_country_codes(_SHORT_ID, "ZZZNOTACOUNTRY")


class TestGetDimensionInfo:
    def test_returns_list_of_dims(self, meta):
        result = meta.get_dimension_info(_SHORT_ID)
        assert isinstance(result, list)
        assert len(result) == 3  # REF_AREA, MEASURE, FREQ (TIME_PERIOD excluded)

    def test_each_entry_has_required_keys(self, meta):
        result = meta.get_dimension_info(_SHORT_ID)
        required_keys = {
            "id",
            "position",
            "name",
            "codelist_id",
            "total_codes",
            "constrained_codes",
            "has_hierarchy",
            "values",
        }
        for entry in result:
            assert required_keys.issubset(entry.keys()), f"Missing keys in {entry}"

    def test_constraints_applied(self, meta):
        result = meta.get_dimension_info(_SHORT_ID)
        ref_area = next(d for d in result if d["id"] == "REF_AREA")
        # Constraint limits to USA+GBR
        values = {v["value"] for v in ref_area["values"]}
        assert values == {"USA", "GBR"}
        assert "DEU" not in values

    def test_total_codes_vs_constrained(self, meta):
        result = meta.get_dimension_info(_SHORT_ID)
        ref_area = next(d for d in result if d["id"] == "REF_AREA")
        assert ref_area["total_codes"] == 3  # full codelist size
        assert ref_area["constrained_codes"] == 2  # after constraint

    def test_measure_constrained_to_one(self, meta):
        result = meta.get_dimension_info(_SHORT_ID)
        measure = next(d for d in result if d["id"] == "MEASURE")
        assert measure["constrained_codes"] == 1
        assert measure["values"][0]["value"] == "CPI"


class TestGetTableGroups:
    def test_no_table_identifier_dimension(self, meta):
        """Returns empty list when TABLE_IDENTIFIER is not a dimension."""
        result = meta.get_table_groups(_SHORT_ID)
        assert result == []

    def test_with_table_identifier(self, meta):
        meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "TABLE_IDENTIFIER",
                "position": 99,
                "codelist_id": "OECD:CL_TBL(1.0)",
                "concept_id": "TABLE_IDENTIFIER",
                "name": "Table",
            }
        )
        meta.codelists["OECD:CL_TBL(1.0)"] = {"T01": "Table One", "T02": "Table Two"}
        meta._dataflow_constraints[_FULL_ID]["TABLE_IDENTIFIER"] = ["T01"]
        params_cache = meta._dataflow_parameters_cache
        params_cache.pop(_FULL_ID, None)
        params_cache.pop(_SHORT_ID, None)

        result = meta.get_table_groups(_SHORT_ID)
        assert len(result) == 1
        assert result[0]["value"] == "T01"
        assert result[0]["label"] == "Table One"


class TestGetConstrainedValues:
    def test_returns_per_dimension(self, meta):
        result = meta.get_constrained_values(_SHORT_ID)
        assert "REF_AREA" in result
        assert "MEASURE" in result
        assert "FREQ" in result

    def test_constrained_values_filtered(self, meta):
        result = meta.get_constrained_values(_SHORT_ID)
        freq_values = {v["value"] for v in result["FREQ"]}
        assert freq_values == {"A", "Q"}
        assert "M" not in freq_values

    def test_each_value_has_label_and_description(self, meta):
        result = meta.get_constrained_values(_SHORT_ID)
        for dim_values in result.values():
            for v in dim_values:
                assert "value" in v
                assert "label" in v
                assert "description" in v


class TestFindIndicatorDimension:
    def test_measure_identified(self, meta):
        dim = meta._find_indicator_dimension(_SHORT_ID)
        assert dim == "MEASURE"

    def test_with_indicator_code(self, meta):
        dim = meta._find_indicator_dimension(_SHORT_ID, "CPI")
        assert dim == "MEASURE"

    def test_invalid_code_returns_none(self, meta):
        dim = meta._find_indicator_dimension(_SHORT_ID, "NONEXISTENT_CODE_XYZ")
        assert dim is None


class TestGetIndicatorsIn:
    def test_from_cache(self, meta):
        meta._dataflow_indicators_cache[_FULL_ID] = [
            {
                "indicator": "CPI",
                "label": "Consumer Price Index",
                "dimension_id": "MEASURE",
                "dataflow_id": _SHORT_ID,
                "dataflow_name": "Test",
                "description": "CPI",
                "symbol": f"{_SHORT_ID}::CPI",
            },
        ]
        result = meta.get_indicators_in(_SHORT_ID)
        assert len(result) == 1
        assert result[0]["indicator"] == "CPI"

    def test_constraint_filtering(self, meta):
        meta._dataflow_indicators_cache[_FULL_ID] = [
            {
                "indicator": "CPI",
                "label": "CPI",
                "dimension_id": "MEASURE",
                "dataflow_id": _SHORT_ID,
                "dataflow_name": "Test",
                "description": "CPI",
                "symbol": f"{_SHORT_ID}::CPI",
            },
            {
                "indicator": "PPI",
                "label": "PPI",
                "dimension_id": "MEASURE",
                "dataflow_id": _SHORT_ID,
                "dataflow_name": "Test",
                "description": "PPI",
                "symbol": f"{_SHORT_ID}::PPI",
            },
        ]
        # Constraint only allows CPI
        result = meta.get_indicators_in(_SHORT_ID)
        codes = [r["indicator"] for r in result]
        assert "CPI" in codes
        assert "PPI" not in codes


class TestGetIndicatorDataflows:
    def test_finds_correct_dataflow(self, meta):
        meta._dataflow_indicators_cache[_FULL_ID] = [
            {
                "indicator": "CPI",
                "dataflow_id": _SHORT_ID,
                "label": "CPI",
                "dimension_id": "MEASURE",
                "dataflow_name": "Test",
                "description": "",
                "symbol": "",
            },
        ]
        result = meta.get_indicator_dataflows("CPI")
        assert _SHORT_ID in result

    def test_missing_indicator_returns_empty(self, meta):
        meta._dataflow_indicators_cache[_FULL_ID] = []
        result = meta.get_indicator_dataflows("NONEXISTENT")
        assert result == []


class TestDescribeDataflow:
    def test_basic_structure(self, meta):
        meta._dataflow_indicators_cache[_FULL_ID] = []
        result = meta.describe_dataflow(_SHORT_ID)
        assert result["dataflow_id"] == _FULL_ID
        assert result["short_id"] == _SHORT_ID
        assert result["name"] == "Test Dataflow"
        assert "dimensions" in result
        assert "table_groups" in result
        assert "indicator_tree" in result

    def test_ensure_description_called(self, meta):
        """describe_dataflow should attempt to fetch description."""
        meta._dataflow_indicators_cache[_FULL_ID] = []
        # Pre-set description so _ensure_description skips network
        meta.dataflows[_FULL_ID]["description"] = "Pre-set description"
        result = meta.describe_dataflow(_SHORT_ID)
        assert result["description"] == "Pre-set description"


class TestEnsureDescription:
    def test_already_has_description(self, meta):
        """Skips fetch when description already present."""
        meta.dataflows[_FULL_ID]["description"] = "Existing"
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request"
        ) as mock_req:
            meta._ensure_description(_FULL_ID)
            mock_req.assert_not_called()
        assert meta.dataflows[_FULL_ID]["description"] == "Existing"

    def test_fetches_and_strips_html(self, meta):
        """Strips HTML tags from raw description."""
        meta.dataflows[_FULL_ID]["description"] = ""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "data": {
                "dataflows": [{"descriptions": {"en": "<p>Hello <b>World</b></p>"}}]
            }
        }
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=mock_resp,
        ):
            meta._ensure_description(_FULL_ID)
        assert meta.dataflows[_FULL_ID]["description"] == "Hello World"

    def test_deduplicated_whitespace(self, meta):
        meta.dataflows[_FULL_ID]["description"] = ""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "data": {
                "dataflows": [{"descriptions": {"en": "Word1\t\t  Word2   Word3"}}]
            }
        }
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=mock_resp,
        ):
            meta._ensure_description(_FULL_ID)
        assert meta.dataflows[_FULL_ID]["description"] == "Word1 Word2 Word3"

    def test_network_error_silenced(self, meta):
        """Exception during fetch is silently ignored."""
        meta.dataflows[_FULL_ID]["description"] = ""
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            side_effect=Exception("network error"),
        ):
            meta._ensure_description(_FULL_ID)  # must not raise
        assert meta.dataflows[_FULL_ID]["description"] == ""

    def test_cached_after_fetch(self, meta):
        """Second call does not go to network again."""
        meta.dataflows[_FULL_ID]["description"] = ""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "data": {"dataflows": [{"descriptions": {"en": "Desc"}}]}
        }
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=mock_resp,
        ) as mock_req:
            meta._ensure_description(_FULL_ID)
            meta._ensure_description(_FULL_ID)
            assert mock_req.call_count == 1

    def test_html_entities_decoded(self, meta):
        meta.dataflows[_FULL_ID]["description"] = ""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "data": {
                "dataflows": [{"descriptions": {"en": "A &amp; B &lt;C&gt; D&nbsp;E"}}]
            }
        }
        with patch(
            "openbb_oecd.utils.metadata._loader_mixin._make_request",
            return_value=mock_resp,
        ):
            meta._ensure_description(_FULL_ID)
        desc = meta.dataflows[_FULL_ID]["description"]
        assert "&amp;" not in desc
        assert "A & B" in desc


class TestFindTables:
    def _seed_table_map(self, meta):
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

    def test_finds_by_name(self, meta):
        self._seed_table_map(meta)
        results = meta.find_tables("Test")
        assert any(r["dataflow_id"] == _FULL_ID for r in results)

    def test_empty_query_returns_all(self, meta):
        self._seed_table_map(meta)
        results = meta.find_tables("")
        assert len(results) >= 1

    def test_no_match_returns_empty(self, meta):
        self._seed_table_map(meta)
        results = meta.find_tables("ZZZNONEXISTENTXYZ")
        assert results == []

    def test_multi_word_and_logic(self, meta):
        self._seed_table_map(meta)
        # Both "Test" and "Dataflow" should appear in the row text
        results = meta.find_tables("Test Dataflow")
        assert any(r["dataflow_id"] == _FULL_ID for r in results)
        results2 = meta.find_tables("Test NOMATCH")
        assert not any(r["dataflow_id"] == _FULL_ID for r in results2)


class TestDetectCountryFamilies:
    def test_no_family_for_small_group(self, meta):
        # Only one dataflow → too small to be a family
        result = meta._detect_country_families()
        assert result == {}

    def test_family_detected(self, meta):
        """Add enough per-country dataflows to trigger family detection."""
        dsd = "DSD_REV"
        country_suffixes = [
            "_AUT",
            "_BEL",
            "_CAN",
            "_DEU",
            "_ESP",
            "_FIN",
            "_FRA",
            "_GBR",
            "_GRC",
            "_IRL",
        ]
        for sfx in country_suffixes:
            fid = f"{dsd}@DF_REV{sfx}"
            meta.dataflows[fid] = {
                "id": fid,
                "short_id": f"DF_REV{sfx}",
                "agency_id": "OECD",
                "version": "1.0",
                "name": f"Tax revenues ({sfx[1:]})",
                "description": "",
            }
        # Add an ALL variant
        rep_fid = f"{dsd}@DF_REV_ALL"
        meta.dataflows[rep_fid] = {
            "id": rep_fid,
            "short_id": "DF_REV_ALL",
            "agency_id": "OECD",
            "version": "1.0",
            "name": "Tax revenues (OECD)",
            "description": "",
        }
        families = meta._detect_country_families()
        # Some members should be in the family map
        in_family = [fid for fid in families if "DF_REV" in fid]
        assert len(in_family) > 0
        # Representative should be the _ALL variant
        first = families[in_family[0]]
        assert first["representative"] == rep_fid


class TestSearchIndicators:
    def test_raises_without_params(self, meta):
        with pytest.raises(OpenBBError, match="At least one"):
            meta.search_indicators()

    def test_finds_by_dataflow(self, meta):
        meta._dataflow_indicators_cache[_FULL_ID] = [
            {
                "indicator": "CPI",
                "label": "Consumer Price Index",
                "dimension_id": "MEASURE",
                "dataflow_id": _SHORT_ID,
                "dataflow_name": "Test",
                "description": "The CPI",
                "symbol": "x::CPI",
            },
        ]
        results = meta.search_indicators(dataflows=_SHORT_ID)
        assert len(results) == 1
        assert results[0]["indicator"] == "CPI"

    def test_finds_by_query_label(self, meta):
        meta._dataflow_indicators_cache[_FULL_ID] = [
            {
                "indicator": "CPI",
                "label": "Consumer Price Index",
                "dimension_id": "MEASURE",
                "dataflow_id": _SHORT_ID,
                "dataflow_name": "Test",
                "description": "Consumer prices",
                "symbol": "x::CPI",
            },
            {
                "indicator": "UNE",
                "label": "Unemployment Rate",
                "dimension_id": "MEASURE",
                "dataflow_id": _SHORT_ID,
                "dataflow_name": "Test",
                "description": "Jobs",
                "symbol": "x::UNE",
            },
        ]
        results = meta.search_indicators(query="consumer", dataflows=_SHORT_ID)
        codes = [r["indicator"] for r in results]
        assert "CPI" in codes
        assert "UNE" not in codes


class TestBuildDataUrl:
    def test_basic_url_format(self, meta):
        url = meta.build_data_url(_SHORT_ID)
        assert "sdmx.oecd.org" in url
        assert "DF_TEST" in url

    def test_last_n_appended(self, meta):
        url = meta.build_data_url(_SHORT_ID, last_n=5)
        assert "lastNObservations=5" in url

    def test_dimension_filter_in_url(self, meta):
        url = meta.build_data_url(_SHORT_ID, dimension_filter="USA.*.*")
        assert "USA" in url


class TestBuildDimensionFilter:
    def test_wildcard_for_all(self, meta):
        result = meta.build_dimension_filter(_SHORT_ID)
        # Default: wildcard for each dimension + time
        assert result.count("*") >= 3

    def test_specific_value_inserted(self, meta):
        result = meta.build_dimension_filter(_SHORT_ID, REF_AREA="USA")
        assert result.startswith("USA.")

    def test_freq_value_at_correct_position(self, meta):
        result = meta.build_dimension_filter(_SHORT_ID, FREQ="A")
        parts = result.split(".")
        # Dimension order: REF_AREA(0), MEASURE(1), FREQ(2)
        assert parts[2] == "A"


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
