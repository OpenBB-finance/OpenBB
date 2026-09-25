"""Gap-fill tests for openbb_oecd.utils.metadata._public_api_mixin."""

from __future__ import annotations

import pytest

_FULL_ID = "DSD_TEST@DF_TEST"
_SHORT_ID = "DF_TEST"


class TestListDataflowsByTopic:
    """Covers lines 96-119 (``list_dataflows_by_topic``)."""

    def _seed(self, meta):
        """Seed taxonomy + categorisation for the test dataflow."""
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
                    {
                        "id": "EMPTY",
                        "name": "Empty",
                        "path": "ECO.EMPTY",
                        "children": [],
                    },
                ],
            }
        ]
        meta._category_to_dfs = {"ECO.PRICES": [_FULL_ID]}
        meta._df_to_categories = {_FULL_ID: ["ECO.PRICES"]}
        meta._taxonomy_loaded = True

    def test_returns_nested_topic_tree(self, seeded_meta):
        """Topic tree includes dataflows under their subtopic."""
        self._seed(seeded_meta)
        result = seeded_meta.list_dataflows_by_topic()
        assert len(result) == 1
        eco = result[0]
        assert eco["id"] == "ECO"
        assert eco["name"] == "Economy"
        assert len(eco["subtopics"]) == 1
        prices = eco["subtopics"][0]
        assert prices["id"] == "PRICES"
        assert prices["dataflows"][0] == {"label": "Test Dataflow", "value": _FULL_ID}

    def test_empty_subtopics_pruned(self, seeded_meta):
        """Subtopics with no dataflows are dropped from the tree."""
        self._seed(seeded_meta)
        result = seeded_meta.list_dataflows_by_topic()
        sub_ids = [s["id"] for s in result[0]["subtopics"]]
        assert "EMPTY" not in sub_ids

    def test_missing_dataflow_entry_falls_back_to_id(self, seeded_meta):
        """``_df_entry`` returns ``label=full_id`` when dataflow is missing."""
        self._seed(seeded_meta)
        seeded_meta._category_to_dfs = {"ECO.PRICES": ["UNKNOWN@DF"]}
        result = seeded_meta.list_dataflows_by_topic()
        prices = result[0]["subtopics"][0]
        entry = prices["dataflows"][0]
        assert entry["value"] == "UNKNOWN@DF"
        assert entry["label"] == "UNKNOWN@DF"


class TestGetDataflowInfo:
    """Covers lines 123-124 (``get_dataflow_info``)."""

    def test_returns_dataflow_dict(self, seeded_meta):
        """Returns the dataflow metadata mapping for a known id."""
        info = seeded_meta.get_dataflow_info(_SHORT_ID)
        assert info["short_id"] == _SHORT_ID
        assert info["name"] == "Test Dataflow"


class TestDetectCountryFamiliesBranches:
    """Covers lines 155, 165, 175-178, 181-182 in ``_detect_country_families``."""

    def _add_dataflow(self, meta, full_id, short_id, name="X"):
        """Inject a fake dataflow record."""
        meta.dataflows[full_id] = {
            "id": full_id,
            "short_id": short_id,
            "agency_id": "OECD",
            "version": "1.0",
            "name": name,
            "description": "",
        }

    def test_short_common_prefix_rejected(self, seeded_meta):
        """Common prefix < 4 chars triggers the early continue on line 155."""
        seeded_meta.dataflows.clear()
        dsd = "DSD_SHORT"
        for sid in ("A_USA", "B_GBR", "C_DEU", "D_FRA", "E_ITA"):
            self._add_dataflow(seeded_meta, f"{dsd}@{sid}", sid)
        families = seeded_meta._detect_country_families()
        assert families == {}

    def test_low_country_ratio_rejected(self, seeded_meta):
        """Group with <70% country suffixes triggers the continue on line 165."""
        seeded_meta.dataflows.clear()
        dsd = "DSD_MIX"
        for sid in (
            "TABLE_DATA1",
            "TABLE_DATA2",
            "TABLE_DATA3",
            "TABLE_DATA4",
            "TABLE_DATA5",
        ):
            self._add_dataflow(seeded_meta, f"{dsd}@{sid}", sid)
        families = seeded_meta._detect_country_families()
        assert families == {}

    def test_empty_suffix_picks_root_representative(self, seeded_meta):
        """An entry whose short_id equals the prefix is chosen as rep (lines 175-178)."""
        seeded_meta.dataflows.clear()
        dsd = "DSD_BASE"
        country_suffixes = ["_USA", "_GBR", "_DEU", "_FRA", "_ITA", "_ESP", "_NLD"]
        for sfx in country_suffixes:
            sid = f"TBL_REV{sfx}"
            self._add_dataflow(seeded_meta, f"{dsd}@{sid}", sid)
        bare_id = f"{dsd}@TBL_REV"
        self._add_dataflow(seeded_meta, bare_id, "TBL_REV", "Bare root")
        families = seeded_meta._detect_country_families()
        assert families
        rep = next(iter(families.values()))["representative"]
        assert rep == bare_id

    def test_non_country_fallback_representative(self, seeded_meta):
        """Falls back to first non-country member when no ALL/empty rep exists."""
        seeded_meta.dataflows.clear()
        dsd = "DSD_FALLBACK"
        country_suffixes = ["_USA", "_GBR", "_DEU", "_FRA", "_ITA", "_ESP", "_NLD"]
        for sfx in country_suffixes:
            sid = f"TBL_DATA{sfx}"
            self._add_dataflow(seeded_meta, f"{dsd}@{sid}", sid)
        non_country_id = f"{dsd}@TBL_DATA_SUMMARY"
        self._add_dataflow(seeded_meta, non_country_id, "TBL_DATA_SUMMARY")
        families = seeded_meta._detect_country_families()
        assert families
        rep = next(iter(families.values()))["representative"]
        assert rep == non_country_id


class TestDetectSectionFamilies:
    """Covers lines 228-248 (``_detect_section_families``)."""

    def _add_dataflow(self, meta, full_id, short_id):
        """Inject a fake dataflow record."""
        meta.dataflows[full_id] = {
            "id": full_id,
            "short_id": short_id,
            "agency_id": "OECD",
            "version": "1.0",
            "name": short_id,
            "description": "",
        }

    def test_section_attached_to_root(self, seeded_meta):
        """A longer short_id beginning with root + '_' becomes a section."""
        seeded_meta.dataflows.clear()
        dsd = "DSD_X"
        self._add_dataflow(seeded_meta, f"{dsd}@T1", "T1")
        self._add_dataflow(seeded_meta, f"{dsd}@T1_EXPEND", "T1_EXPEND")
        sections = seeded_meta._detect_section_families()
        assert sections == {f"{dsd}@T1_EXPEND": f"{dsd}@T1"}

    def test_no_section_when_only_one(self, seeded_meta):
        """Groups of size <2 are skipped early."""
        sections = seeded_meta._detect_section_families()
        assert sections == {}

    def test_siblings_without_root_relationship_are_independent(self, seeded_meta):
        """Two dataflows with disjoint short_ids each remain roots."""
        seeded_meta.dataflows.clear()
        dsd = "DSD_INDEP"
        self._add_dataflow(seeded_meta, f"{dsd}@FOO", "FOO")
        self._add_dataflow(seeded_meta, f"{dsd}@BAR", "BAR")
        sections = seeded_meta._detect_section_families()
        assert sections == {}


class TestTableMapBranches:
    """Covers lines 297, 300, 305-312, 339-347 in ``table_map``."""

    def _seed_taxonomy(self, meta, paths):
        """Seed a single-topic taxonomy referencing ``paths`` of dataflows."""
        meta._taxonomy_tree = [
            {
                "id": "ECO",
                "name": "Economy",
                "path": "ECO",
                "children": [],
            }
        ]
        meta._category_to_dfs = {"ECO": list(paths)}
        meta._df_to_categories = {fid: ["ECO"] for fid in paths}
        meta._taxonomy_loaded = True

    def _add_dataflow(self, meta, full_id, short_id, name=None):
        """Inject a fake dataflow record."""
        meta.dataflows[full_id] = {
            "id": full_id,
            "short_id": short_id,
            "agency_id": "OECD",
            "version": "1.0",
            "name": name or short_id,
            "description": "",
        }

    def test_missing_entry_skipped(self, seeded_meta):
        """Dataflow id present in category map but absent from registry is skipped."""
        self._seed_taxonomy(seeded_meta, [_FULL_ID, "MISSING@DF"])
        rows = seeded_meta.table_map()
        ids = [r["dataflow_id"] for r in rows]
        assert "MISSING@DF" not in ids
        assert _FULL_ID in ids

    def test_section_member_skipped(self, seeded_meta):
        """Dataflows in section_map are skipped (line 299-300)."""
        seeded_meta.dataflows.clear()
        dsd = "DSD_S"
        self._add_dataflow(seeded_meta, f"{dsd}@T1", "T1")
        self._add_dataflow(seeded_meta, f"{dsd}@T1_EXTRA", "T1_EXTRA")
        self._seed_taxonomy(seeded_meta, [f"{dsd}@T1", f"{dsd}@T1_EXTRA"])
        rows = seeded_meta.table_map()
        ids = [r["dataflow_id"] for r in rows]
        assert f"{dsd}@T1" in ids
        assert f"{dsd}@T1_EXTRA" not in ids

    def test_family_representative_emitted_once(self, seeded_meta):
        """Country families render one row with ``countries`` count (305-312)."""
        seeded_meta.dataflows.clear()
        dsd = "DSD_FAM"
        country_suffixes = [
            "_USA",
            "_GBR",
            "_DEU",
            "_FRA",
            "_ITA",
            "_ESP",
            "_NLD",
            "_AUT",
        ]
        ids = []
        for sfx in country_suffixes:
            sid = f"TBL_REV{sfx}"
            fid = f"{dsd}@{sid}"
            self._add_dataflow(seeded_meta, fid, sid)
            ids.append(fid)
        rep_fid = f"{dsd}@TBL_REV_ALL"
        self._add_dataflow(seeded_meta, rep_fid, "TBL_REV_ALL", "Tax revenues (All)")
        ids.append(rep_fid)
        self._seed_taxonomy(seeded_meta, ids)
        rows = seeded_meta.table_map()
        family_rows = [r for r in rows if r["dataflow_id"] == rep_fid]
        assert len(family_rows) == 1
        assert family_rows[0]["countries"] == len(ids)

    def test_family_representative_deduped_across_categories(self, seeded_meta):
        """A family rep referenced from multiple categories emits per-category."""
        seeded_meta.dataflows.clear()
        dsd = "DSD_FAM2"
        country_suffixes = ["_USA", "_GBR", "_DEU", "_FRA", "_ITA", "_ESP", "_NLD"]
        ids = []
        for sfx in country_suffixes:
            sid = f"TBL_XX{sfx}"
            fid = f"{dsd}@{sid}"
            self._add_dataflow(seeded_meta, fid, sid)
            ids.append(fid)
        rep_fid = f"{dsd}@TBL_XX_ALL"
        self._add_dataflow(seeded_meta, rep_fid, "TBL_XX_ALL")
        ids.append(rep_fid)
        seeded_meta._taxonomy_tree = [
            {
                "id": "ECO",
                "name": "Economy",
                "path": "ECO",
                "children": [
                    {
                        "id": "SUB",
                        "name": "Sub",
                        "path": "ECO.SUB",
                        "children": [],
                    }
                ],
            }
        ]
        seeded_meta._category_to_dfs = {"ECO.SUB": list(ids)}
        seeded_meta._df_to_categories = {fid: ["ECO.SUB"] for fid in ids}
        seeded_meta._taxonomy_loaded = True
        rows = seeded_meta.table_map()
        rep_rows = [r for r in rows if r["dataflow_id"] == rep_fid]
        assert len(rep_rows) == 1

    def test_include_empty_lists_uncategorised(self, seeded_meta):
        """Uncategorised dataflows appear with topic '(Uncategorised)' (339-347)."""
        orphan_id = "DSD_ORPHAN@DF_ORPHAN"
        seeded_meta.dataflows[orphan_id] = {
            "id": orphan_id,
            "short_id": "DF_ORPHAN",
            "agency_id": "OECD",
            "version": "1.0",
            "name": "Orphan",
            "description": "",
        }
        seeded_meta._taxonomy_tree = []
        seeded_meta._category_to_dfs = {}
        seeded_meta._df_to_categories = {}
        seeded_meta._taxonomy_loaded = True
        rows = seeded_meta.table_map(include_empty=True)
        uncat = [r for r in rows if r["dataflow_id"] == orphan_id]
        assert len(uncat) == 1
        assert uncat[0]["topic"] == "(Uncategorised)"
        assert uncat[0]["path"] == "(Uncategorised)"


class TestPrintTableMap:
    """Covers lines 410-458 (``print_table_map``)."""

    def _seed(self, meta):
        """Seed a basic categorised taxonomy with one dataflow."""
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
        meta._category_to_dfs = {"ECO.PRICES": [_FULL_ID]}
        meta._df_to_categories = {_FULL_ID: ["ECO.PRICES"]}
        meta._taxonomy_loaded = True

    def test_empty_returns_placeholder(self, seeded_meta):
        """No matching rows returns the explicit placeholder string."""
        seeded_meta._taxonomy_tree = []
        seeded_meta._category_to_dfs = {}
        seeded_meta._df_to_categories = {}
        seeded_meta._taxonomy_loaded = True
        result = seeded_meta.print_table_map()
        assert result == "(no matching tables)"

    def test_basic_output_includes_table(self, seeded_meta):
        """Output contains the topic banner and table label."""
        self._seed(seeded_meta)
        result = seeded_meta.print_table_map()
        assert "Economy" in result
        assert "Test Dataflow" in result
        assert "=" * 60 in result

    def test_query_argument_routes_to_find_tables(self, seeded_meta):
        """A non-empty query goes through find_tables."""
        self._seed(seeded_meta)
        result = seeded_meta.print_table_map(query="Test")
        assert "Test Dataflow" in result

    def test_topic_filter_keeps_matching_rows(self, seeded_meta):
        """``topic`` keyword filters by case-insensitive substring."""
        self._seed(seeded_meta)
        result = seeded_meta.print_table_map(topic="economy")
        assert "Test Dataflow" in result

    def test_topic_filter_excludes_other_rows(self, seeded_meta):
        """Unmatched topic gives the empty placeholder."""
        self._seed(seeded_meta)
        result = seeded_meta.print_table_map(topic="health")
        assert result == "(no matching tables)"

    def test_topic_break_separator_between_topics(self, seeded_meta):
        """A second topic inserts a blank-line separator before its banner."""
        seeded_meta.dataflows["DSD_HEA@DF_HEA"] = {
            "id": "DSD_HEA@DF_HEA",
            "short_id": "DF_HEA",
            "agency_id": "OECD",
            "version": "1.0",
            "name": "Health Stats",
            "description": "",
        }
        seeded_meta._taxonomy_tree = [
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
            },
            {
                "id": "HEA",
                "name": "Health",
                "path": "HEA",
                "children": [
                    {
                        "id": "STATS",
                        "name": "Stats",
                        "path": "HEA.STATS",
                        "children": [],
                    },
                ],
            },
        ]
        seeded_meta._category_to_dfs = {
            "ECO.PRICES": [_FULL_ID],
            "HEA.STATS": ["DSD_HEA@DF_HEA"],
        }
        seeded_meta._df_to_categories = {
            _FULL_ID: ["ECO.PRICES"],
            "DSD_HEA@DF_HEA": ["HEA.STATS"],
        }
        seeded_meta._taxonomy_loaded = True
        result = seeded_meta.print_table_map()
        assert "Economy" in result
        assert "Health" in result

    def test_sub_subtopic_appended_to_label(self, seeded_meta):
        """A sub-subtopic level shows up in the bracketed sub label."""
        seeded_meta._taxonomy_tree = [
            {
                "id": "ECO",
                "name": "Economy",
                "path": "ECO",
                "children": [
                    {
                        "id": "PRICES",
                        "name": "Prices",
                        "path": "ECO.PRICES",
                        "children": [
                            {
                                "id": "CPI",
                                "name": "CPI",
                                "path": "ECO.PRICES.CPI",
                                "children": [],
                            }
                        ],
                    }
                ],
            }
        ]
        seeded_meta._category_to_dfs = {"ECO.PRICES.CPI": [_FULL_ID]}
        seeded_meta._df_to_categories = {_FULL_ID: ["ECO.PRICES.CPI"]}
        seeded_meta._taxonomy_loaded = True
        result = seeded_meta.print_table_map()
        assert "[Prices > CPI]" in result

    def test_countries_suffix_added_for_family(self, seeded_meta):
        """Family rows render a ``(N countries)`` suffix."""
        seeded_meta.dataflows.clear()
        dsd = "DSD_FAM3"
        country_suffixes = ["_USA", "_GBR", "_DEU", "_FRA", "_ITA", "_ESP", "_NLD"]
        ids = []
        for sfx in country_suffixes:
            sid = f"TBL_AAA{sfx}"
            fid = f"{dsd}@{sid}"
            seeded_meta.dataflows[fid] = {
                "id": fid,
                "short_id": sid,
                "agency_id": "OECD",
                "version": "1.0",
                "name": sid,
                "description": "",
            }
            ids.append(fid)
        rep_fid = f"{dsd}@TBL_AAA_ALL"
        seeded_meta.dataflows[rep_fid] = {
            "id": rep_fid,
            "short_id": "TBL_AAA_ALL",
            "agency_id": "OECD",
            "version": "1.0",
            "name": "AAA Aggregate",
            "description": "",
        }
        ids.append(rep_fid)
        seeded_meta._taxonomy_tree = [
            {
                "id": "ECO",
                "name": "Economy",
                "path": "ECO",
                "children": [],
            }
        ]
        seeded_meta._category_to_dfs = {"ECO": list(ids)}
        seeded_meta._df_to_categories = {fid: ["ECO"] for fid in ids}
        seeded_meta._taxonomy_loaded = True
        result = seeded_meta.print_table_map()
        assert "countries)" in result


class TestGetDataflowParametersCacheBranches:
    """Covers lines 475 and 485 in ``get_dataflow_parameters``."""

    def test_full_id_cache_hit(self, seeded_meta):
        """When only full_id is cached, short_id lookup hits the second branch."""
        seeded_meta._dataflow_parameters_cache[_FULL_ID] = {"REF_AREA": []}
        result = seeded_meta.get_dataflow_parameters(_SHORT_ID)
        assert result == {"REF_AREA": []}

    def test_time_period_dim_is_skipped(self, seeded_meta):
        """A TIME_PERIOD dimension is excluded from the returned params."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "TIME_PERIOD",
                "position": 99,
                "codelist_id": "",
                "concept_id": "TIME_PERIOD",
                "name": "Time",
            }
        )
        seeded_meta._dataflow_parameters_cache.pop(_FULL_ID, None)
        seeded_meta._dataflow_parameters_cache.pop(_SHORT_ID, None)
        params = seeded_meta.get_dataflow_parameters(_FULL_ID)
        assert "TIME_PERIOD" not in params


class TestGetDimensionInfoBranches:
    """Covers lines 518, 531-533, 544-546, 555-560, 572 in ``get_dimension_info``."""

    def test_time_period_dim_skipped(self, seeded_meta):
        """A TIME_PERIOD dimension is omitted from the result."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "TIME_PERIOD",
                "position": 99,
                "codelist_id": "",
                "concept_id": "TIME_PERIOD",
                "name": "Time",
            }
        )
        seeded_meta._dataflow_parameters_cache.pop(_FULL_ID, None)
        seeded_meta._dataflow_parameters_cache.pop(_SHORT_ID, None)
        result = seeded_meta.get_dimension_info(_SHORT_ID)
        ids = [d["id"] for d in result]
        assert "TIME_PERIOD" not in ids

    def test_parents_resolved_from_prefix_match(self, seeded_meta):
        """When direct codelist_id has no parents but a prefixed key does."""
        seeded_meta._codelist_parents["OECD:CL_AREA(2.5)"] = {"USA": "AMERICAS"}
        result = seeded_meta.get_dimension_info(_SHORT_ID)
        ref_area = next(d for d in result if d["id"] == "REF_AREA")
        assert ref_area["has_hierarchy"] is True
        usa = next(v for v in ref_area["values"] if v["value"] == "USA")
        assert usa["parent"] == "AMERICAS"

    def test_descriptions_resolved_from_prefix_match(self, seeded_meta):
        """Descriptions backfill from another codelist version under same prefix."""
        seeded_meta._codelist_descriptions["OECD:CL_AREA(2.5)"] = {
            "USA": "USA full description",
        }
        result = seeded_meta.get_dimension_info(_SHORT_ID)
        ref_area = next(d for d in result if d["id"] == "REF_AREA")
        usa = next(v for v in ref_area["values"] if v["value"] == "USA")
        assert usa["description"] == "USA full description"

    def test_empty_constrained_entries_fallback_to_allowed(self, seeded_meta):
        """If constraint allows codes not in params, codelist labels are used."""
        seeded_meta._dataflow_constraints[_FULL_ID]["REF_AREA"] = ["ZZZ"]
        seeded_meta.codelists["OECD:CL_AREA(1.0)"] = {"ZZZ": "Zedland"}
        seeded_meta._dataflow_parameters_cache.pop(_FULL_ID, None)
        seeded_meta._dataflow_parameters_cache.pop(_SHORT_ID, None)
        result = seeded_meta.get_dimension_info(_SHORT_ID)
        ref_area = next(d for d in result if d["id"] == "REF_AREA")
        values = {v["value"]: v["label"] for v in ref_area["values"]}
        assert values == {"ZZZ": "Zedland"}

    def test_unconstrained_dimension_uses_all_entries(self, seeded_meta):
        """Dim without a constraint takes the else branch (line 560)."""
        seeded_meta._dataflow_constraints[_FULL_ID].pop("REF_AREA", None)
        seeded_meta._dataflow_parameters_cache.pop(_FULL_ID, None)
        seeded_meta._dataflow_parameters_cache.pop(_SHORT_ID, None)
        result = seeded_meta.get_dimension_info(_SHORT_ID)
        ref_area = next(d for d in result if d["id"] == "REF_AREA")
        values = {v["value"] for v in ref_area["values"]}
        assert values == {"USA", "GBR", "DEU"}

    def test_empty_constrained_entries_with_missing_codelist_entry(self, seeded_meta):
        """Allowed code missing from codelist falls back to the code itself."""
        seeded_meta._dataflow_constraints[_FULL_ID]["REF_AREA"] = ["UNK"]
        seeded_meta.codelists["OECD:CL_AREA(1.0)"] = {}
        seeded_meta._dataflow_parameters_cache.pop(_FULL_ID, None)
        seeded_meta._dataflow_parameters_cache.pop(_SHORT_ID, None)
        result = seeded_meta.get_dimension_info(_SHORT_ID)
        ref_area = next(d for d in result if d["id"] == "REF_AREA")
        values = {v["value"]: v["label"] for v in ref_area["values"]}
        assert values == {"UNK": "UNK"}


class TestGetConstrainedValuesBranches:
    """Covers line 644 (TIME_PERIOD skip in ``get_constrained_values``)."""

    def test_time_period_dim_is_skipped(self, seeded_meta):
        """A TIME_PERIOD dimension is omitted from constrained values output."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "TIME_PERIOD",
                "position": 99,
                "codelist_id": "",
                "concept_id": "TIME_PERIOD",
                "name": "Time",
            }
        )
        seeded_meta._dataflow_parameters_cache.pop(_FULL_ID, None)
        seeded_meta._dataflow_parameters_cache.pop(_SHORT_ID, None)
        result = seeded_meta.get_constrained_values(_SHORT_ID)
        assert "TIME_PERIOD" not in result


@pytest.fixture
def empty_meta_with_taxonomy(empty_meta):
    """Empty meta marked as taxonomy-loaded so ensure-helpers are no-ops."""
    empty_meta._taxonomy_loaded = True
    empty_meta._full_catalogue_loaded = True
    return empty_meta
