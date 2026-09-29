"""Unit tests for openbb_oecd.utils.metadata._indicator_mixin (full coverage)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

_FULL_ID = "DSD_TEST@DF_TEST"
_SHORT_ID = "DF_TEST"


class TestGetIndicatorDim:
    """Coverage for IndicatorMixin._get_indicator_dim."""

    def test_cache_hit_short_circuits(self, seeded_meta):
        """Cached value is returned without recomputation."""
        seeded_meta._indicator_dim_cache[_FULL_ID] = "MEASURE"
        assert seeded_meta._get_indicator_dim(_FULL_ID) == "MEASURE"

    def test_cache_hit_with_none(self, seeded_meta):
        """None cached value is honored."""
        seeded_meta._indicator_dim_cache["FAKE@FAKE"] = None
        assert seeded_meta._get_indicator_dim("FAKE@FAKE") is None

    def test_layout_row_matches_candidate(self, seeded_meta):
        """LAYOUT_ROW annotation pointing at a known indicator dim wins."""
        seeded_meta.dataflows[_FULL_ID]["annotations"] = {
            "LAYOUT_ROW": "MEASURE, REF_AREA"
        }
        assert seeded_meta._get_indicator_dim(_FULL_ID) == "MEASURE"

    def test_layout_row_no_match_falls_back_to_candidate(self, seeded_meta):
        """LAYOUT_ROW unknown dim → falls through to candidate loop."""
        seeded_meta.dataflows[_FULL_ID]["annotations"] = {"LAYOUT_ROW": "FOO, BAR"}
        assert seeded_meta._get_indicator_dim(_FULL_ID) == "MEASURE"

    def test_falls_back_to_first_non_skip_dim(self, seeded_meta):
        """When no indicator candidate present, picks lowest-position non-skip dim."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"] = [
            {
                "id": "FREQ",
                "position": 1,
                "codelist_id": "OECD:CL_FREQ(1.0)",
                "concept_id": "FREQ",
                "name": "Frequency",
            },
            {
                "id": "CUSTOM_DIM",
                "position": 2,
                "codelist_id": "OECD:CL_CUSTOM(1.0)",
                "concept_id": "CUSTOM",
                "name": "Custom",
            },
        ]
        assert seeded_meta._get_indicator_dim(_FULL_ID) == "CUSTOM_DIM"

    def test_returns_none_when_only_skip_dims(self, seeded_meta):
        """All dimensions in the skip set → None and cached."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"] = [
            {
                "id": "REF_AREA",
                "position": 1,
                "codelist_id": "OECD:CL_AREA(1.0)",
                "concept_id": "REF_AREA",
                "name": "Reference Area",
            },
            {
                "id": "FREQ",
                "position": 2,
                "codelist_id": "OECD:CL_FREQ(1.0)",
                "concept_id": "FREQ",
                "name": "Frequency",
            },
        ]
        assert seeded_meta._get_indicator_dim(_FULL_ID) is None
        assert seeded_meta._indicator_dim_cache[_FULL_ID] is None


class TestFindIndicatorDimensionFallback:
    """Coverage for the second loop in _find_indicator_dimension."""

    def _swap_to_custom_dim(self, meta):
        """Replace MEASURE with a non-candidate dimension having codes."""
        meta.datastructures[_FULL_ID]["dimensions"] = [
            {
                "id": "REF_AREA",
                "position": 1,
                "codelist_id": "OECD:CL_AREA(1.0)",
                "concept_id": "REF_AREA",
                "name": "Reference Area",
            },
            {
                "id": "CUSTOM",
                "position": 2,
                "codelist_id": "OECD:CL_CUSTOM(1.0)",
                "concept_id": "CUSTOM",
                "name": "Custom",
            },
            {
                "id": "FREQ",
                "position": 3,
                "codelist_id": "OECD:CL_FREQ(1.0)",
                "concept_id": "FREQ",
                "name": "Frequency",
            },
        ]
        meta.codelists["OECD:CL_CUSTOM(1.0)"] = {"X": "X label", "Y": "Y label"}
        meta._dataflow_constraints[_FULL_ID]["CUSTOM"] = ["X", "Y"]
        meta._dataflow_parameters_cache.pop(_FULL_ID, None)

    def test_fallback_returns_custom_dim_no_code(self, seeded_meta):
        """No indicator_code: the fallback returns the first non-skip dim."""
        self._swap_to_custom_dim(seeded_meta)
        assert seeded_meta._find_indicator_dimension(_SHORT_ID) == "CUSTOM"

    def test_fallback_matches_code(self, seeded_meta):
        """With indicator_code, returns the dim whose codelist contains it."""
        self._swap_to_custom_dim(seeded_meta)
        assert seeded_meta._find_indicator_dimension(_SHORT_ID, "X") == "CUSTOM"

    def test_fallback_code_not_in_dim_returns_none(self, seeded_meta):
        """With unknown indicator_code falls through both loops."""
        self._swap_to_custom_dim(seeded_meta)
        assert seeded_meta._find_indicator_dimension(_SHORT_ID, "ZZZ") is None


class TestGetCodelistForDimensionForceRefresh:
    """Coverage for the force-refresh branch when constraints reference missing codes."""

    def test_force_refresh_when_constraint_code_missing(self, seeded_meta):
        """Codelist missing constrained code → _ensure_structure called with force."""
        seeded_meta._dataflow_constraints[_FULL_ID]["REF_AREA"] = ["USA", "ZZZ"]
        calls: list[dict] = []
        original = seeded_meta._get_codelist

        def fake_get_codelist(cl_id, df_id=None):
            calls.append({"cl_id": cl_id, "df": df_id})
            return original(cl_id, df_id)

        with (
            patch.object(seeded_meta, "_ensure_structure") as mock_ensure,
            patch.object(seeded_meta, "_get_codelist", side_effect=fake_get_codelist),
        ):
            result = seeded_meta.get_codelist_for_dimension(_SHORT_ID, "REF_AREA")

        forced = [c for c in mock_ensure.call_args_list if c.kwargs.get("force")]
        assert forced, "Expected at least one _ensure_structure(force=True) call"
        assert "USA" in result


class TestResolveCountryCodesNoCodelist:
    """When the country codelist is empty, raw codes pass through."""

    def test_empty_codelist_passthrough(self, seeded_meta):
        """No country codelist → values are uppercased and returned verbatim."""
        with patch.object(seeded_meta, "_get_country_codelist", return_value={}):
            result = seeded_meta.resolve_country_codes(_SHORT_ID, " usa , gbr ")
        assert result == ["USA", "GBR"]


class TestGetCountryCodelist:
    """Coverage for IndicatorMixin._get_country_codelist."""

    def test_returns_from_loaded_dsd(self, seeded_meta):
        """When DSD is loaded, returns the codelist via _get_codelist."""
        result = seeded_meta._get_country_codelist(_SHORT_ID)
        assert "USA" in result
        assert result["USA"] == "United States"

    def test_falls_back_to_cl_area_scan(self, empty_meta):
        """When dataflow not loaded, scans codelists for ':CL_AREA('."""
        empty_meta.dataflows[_FULL_ID] = {
            "id": _FULL_ID,
            "short_id": _SHORT_ID,
            "agency_id": "OECD",
            "version": "1.0",
            "name": "X",
        }
        empty_meta._short_id_map[_SHORT_ID] = _FULL_ID
        empty_meta._full_catalogue_loaded = True
        empty_meta.codelists["OECD:CL_AREA(1.0)"] = {"USA": "United States"}
        with patch.object(empty_meta, "_ensure_structure"):
            result = empty_meta._get_country_codelist(_SHORT_ID)
        assert result == {"USA": "United States"}

    def test_falls_back_to_ensure_structure_then_dim(self, empty_meta):
        """When CL_AREA scan misses, _ensure_structure populates the DSD."""
        empty_meta.dataflows[_FULL_ID] = {
            "id": _FULL_ID,
            "short_id": _SHORT_ID,
            "agency_id": "OECD",
            "version": "1.0",
            "name": "X",
        }
        empty_meta._short_id_map[_SHORT_ID] = _FULL_ID
        empty_meta._full_catalogue_loaded = True

        def fake_ensure(df_id, *, force=False):
            empty_meta.datastructures[_FULL_ID] = {
                "dsd_id": "DSD_TEST",
                "agency_id": "OECD",
                "version": "1.0",
                "dimensions": [
                    {
                        "id": "REF_AREA",
                        "position": 1,
                        "codelist_id": "OECD:CL_REF(1.0)",
                        "concept_id": "REF_AREA",
                        "name": "Ref",
                    }
                ],
                "attributes": [],
                "has_time_dimension": True,
            }
            empty_meta.codelists["OECD:CL_REF(1.0)"] = {"USA": "United States"}

        with patch.object(empty_meta, "_ensure_structure", side_effect=fake_ensure):
            result = empty_meta._get_country_codelist(_SHORT_ID)
        assert result == {"USA": "United States"}

    def test_returns_empty_when_no_country_dim(self, empty_meta):
        """No country dimension anywhere → empty dict."""
        empty_meta.dataflows[_FULL_ID] = {
            "id": _FULL_ID,
            "short_id": _SHORT_ID,
            "agency_id": "OECD",
            "version": "1.0",
            "name": "X",
        }
        empty_meta._short_id_map[_SHORT_ID] = _FULL_ID
        empty_meta._full_catalogue_loaded = True

        def fake_ensure(df_id, *, force=False):
            empty_meta.datastructures[_FULL_ID] = {
                "dsd_id": "DSD_TEST",
                "agency_id": "OECD",
                "version": "1.0",
                "dimensions": [
                    {
                        "id": "MEASURE",
                        "position": 1,
                        "codelist_id": "OECD:CL_MEASURE(1.0)",
                        "concept_id": "MEASURE",
                        "name": "M",
                    }
                ],
                "attributes": [],
                "has_time_dimension": True,
            }

        with patch.object(empty_meta, "_ensure_structure", side_effect=fake_ensure):
            assert empty_meta._get_country_codelist(_SHORT_ID) == {}


class TestFilterIndicatorsByConstraints:
    """Coverage for IndicatorMixin._filter_indicators_by_constraints."""

    def test_no_constraints_passthrough(self, seeded_meta):
        """Empty constraints → indicators returned unchanged."""
        seeded_meta._dataflow_constraints.clear()
        inds = [{"indicator": "X", "dimension_id": "MEASURE"}]
        assert seeded_meta._filter_indicators_by_constraints(_SHORT_ID, inds) is inds

    def test_empty_indicators_passthrough(self, seeded_meta):
        """Empty indicator list passes through even with constraints set."""
        result = seeded_meta._filter_indicators_by_constraints(_SHORT_ID, [])
        assert result == []

    def test_unknown_dim_id_kept(self, seeded_meta):
        """An indicator with a dim_id not in constraints survives."""
        inds = [{"indicator": "X", "dimension_id": "OTHER"}]
        result = seeded_meta._filter_indicators_by_constraints(_SHORT_ID, inds)
        assert result == inds


class TestGetIndicatorsInUncached:
    """Coverage for the full uncached body of get_indicators_in."""

    def test_short_id_cache_hit(self, seeded_meta):
        """A short-id cache hit early-exits and applies constraint filtering."""
        seeded_meta._dataflow_indicators_cache[_SHORT_ID] = [
            {
                "indicator": "CPI",
                "dimension_id": "MEASURE",
                "dataflow_id": _SHORT_ID,
                "dataflow_name": "Test",
                "label": "CPI",
                "description": "CPI",
                "symbol": "X::CPI",
            },
        ]
        result = seeded_meta.get_indicators_in(_SHORT_ID)
        assert len(result) == 1
        assert result[0]["indicator"] == "CPI"

    def test_uncached_builds_from_indicator_dim(self, seeded_meta):
        """When uncached, builds indicators using _get_indicator_dim → MEASURE."""
        seeded_meta._dataflow_indicators_cache.clear()
        seeded_meta._dataflow_constraints.pop(_FULL_ID, None)
        seeded_meta._codelist_descriptions["OECD:CL_MEASURE(1.0)"] = {
            "CPI": "Consumer Price Idx"
        }
        seeded_meta._codelist_parents["OECD:CL_MEASURE(1.0)"] = {"PPI": "CPI"}
        result = seeded_meta.get_indicators_in(_SHORT_ID)
        codes = {r["indicator"] for r in result}
        assert codes == {"CPI", "PPI"}
        cpi = next(r for r in result if r["indicator"] == "CPI")
        assert cpi["description"] == "Consumer Price Idx"
        assert cpi["symbol"] == f"{_SHORT_ID}::CPI"
        ppi = next(r for r in result if r["indicator"] == "PPI")
        assert ppi["parent"] == "CPI"

    def test_uncached_with_constraints(self, seeded_meta):
        """Constraints filter available codes."""
        seeded_meta._dataflow_indicators_cache.clear()
        result = seeded_meta.get_indicators_in(_SHORT_ID)
        codes = {r["indicator"] for r in result}
        assert codes == {"CPI"}

    def test_no_content_dims_returns_empty_and_caches(self, seeded_meta):
        """When no content dimensions remain, returns empty and caches it."""
        seeded_meta._dataflow_indicators_cache.clear()
        seeded_meta.datastructures[_FULL_ID]["dimensions"] = [
            {
                "id": "REF_AREA",
                "position": 1,
                "codelist_id": "OECD:CL_AREA(1.0)",
                "concept_id": "REF_AREA",
                "name": "Ref",
            },
            {
                "id": "FREQ",
                "position": 2,
                "codelist_id": "OECD:CL_FREQ(1.0)",
                "concept_id": "FREQ",
                "name": "F",
            },
        ]
        seeded_meta._dataflow_constraints.pop(_FULL_ID, None)
        seeded_meta._dataflow_parameters_cache.pop(_FULL_ID, None)
        seeded_meta._indicator_dim_cache.pop(_FULL_ID, None)
        result = seeded_meta.get_indicators_in(_SHORT_ID)
        assert result == []
        assert seeded_meta._dataflow_indicators_cache[_FULL_ID] == []

    def test_falls_back_to_non_skip_dims_when_no_indicator_candidate(self, seeded_meta):
        """When _get_indicator_dim returns None, iterates non-skip dims."""
        seeded_meta._dataflow_indicators_cache.clear()
        seeded_meta._dataflow_parameters_cache.pop(_FULL_ID, None)
        seeded_meta._indicator_dim_cache[_FULL_ID] = None
        seeded_meta.datastructures[_FULL_ID]["dimensions"] = [
            {
                "id": "REF_AREA",
                "position": 1,
                "codelist_id": "OECD:CL_AREA(1.0)",
                "concept_id": "REF_AREA",
                "name": "Ref",
            },
            {
                "id": "CUSTOM1",
                "position": 2,
                "codelist_id": "OECD:CL_CUSTOM1(1.0)",
                "concept_id": "CUSTOM1",
                "name": "C1",
            },
            {
                "id": "CUSTOM2",
                "position": 3,
                "codelist_id": "OECD:CL_CUSTOM2(1.0)",
                "concept_id": "CUSTOM2",
                "name": "C2",
            },
            {
                "id": "FREQ",
                "position": 4,
                "codelist_id": "OECD:CL_FREQ(1.0)",
                "concept_id": "FREQ",
                "name": "F",
            },
        ]
        seeded_meta.codelists["OECD:CL_CUSTOM1(1.0)"] = {"K1": "K1 label"}
        seeded_meta.codelists["OECD:CL_CUSTOM2(1.0)"] = {"K2": "K2 label"}
        seeded_meta._dataflow_constraints.pop(_FULL_ID, None)
        result = seeded_meta.get_indicators_in(_SHORT_ID)
        codes = {r["indicator"] for r in result}
        assert "K1" in codes and "K2" in codes

    def test_availability_filter_applied(self, seeded_meta):
        """Availability filtering excludes codes not in fetch_availability()."""
        seeded_meta._dataflow_indicators_cache.clear()
        seeded_meta._dataflow_constraints.pop(_FULL_ID, None)
        with patch.object(
            seeded_meta, "fetch_availability", return_value={"MEASURE": ["CPI"]}
        ):
            result = seeded_meta.get_indicators_in(_SHORT_ID)
        codes = {r["indicator"] for r in result}
        assert codes == {"CPI"}

    def test_availability_exception_silenced(self, seeded_meta):
        """fetch_availability errors are silenced, indicators still returned."""
        seeded_meta._dataflow_indicators_cache.clear()
        seeded_meta._dataflow_constraints.pop(_FULL_ID, None)
        with patch.object(
            seeded_meta, "fetch_availability", side_effect=RuntimeError("boom")
        ):
            result = seeded_meta.get_indicators_in(_SHORT_ID)
        codes = {r["indicator"] for r in result}
        assert "CPI" in codes
        assert "PPI" in codes

    def test_seen_codes_deduplicated(self, seeded_meta):
        """A code appearing in two content dims is only emitted once."""
        seeded_meta._dataflow_indicators_cache.clear()
        seeded_meta._dataflow_parameters_cache.pop(_FULL_ID, None)
        seeded_meta._indicator_dim_cache[_FULL_ID] = None
        seeded_meta.datastructures[_FULL_ID]["dimensions"] = [
            {
                "id": "REF_AREA",
                "position": 1,
                "codelist_id": "OECD:CL_AREA(1.0)",
                "concept_id": "REF_AREA",
                "name": "Ref",
            },
            {
                "id": "DIM_A",
                "position": 2,
                "codelist_id": "OECD:CL_X(1.0)",
                "concept_id": "DIM_A",
                "name": "A",
            },
            {
                "id": "DIM_B",
                "position": 3,
                "codelist_id": "OECD:CL_X(1.0)",
                "concept_id": "DIM_B",
                "name": "B",
            },
        ]
        seeded_meta.codelists["OECD:CL_X(1.0)"] = {"DUP": "Duplicate"}
        seeded_meta._dataflow_constraints.pop(_FULL_ID, None)
        result = seeded_meta.get_indicators_in(_SHORT_ID)
        assert len([r for r in result if r["indicator"] == "DUP"]) == 1

    def test_uses_short_id_when_no_at_in_id(self, seeded_meta):
        """A dataflow id lacking '@' produces a short_df_id equal to itself."""
        seeded_meta._dataflow_indicators_cache.clear()
        seeded_meta._dataflow_constraints.pop(_FULL_ID, None)
        result = seeded_meta.get_indicators_in(_SHORT_ID)
        for ind in result:
            assert ind["dataflow_id"] == _SHORT_ID


class TestGetCodelistHierarchy:
    """Coverage for IndicatorMixin.get_codelist_hierarchy."""

    def test_returns_copy_of_parents(self, seeded_meta):
        """Returns a snapshot of the codelist_parents mapping."""
        seeded_meta._codelist_parents["OECD:CL_X(1.0)"] = {"C": "P"}
        result = seeded_meta.get_codelist_hierarchy("OECD:CL_X(1.0)")
        assert result == {"C": "P"}
        result["NEW"] = "X"
        assert "NEW" not in seeded_meta._codelist_parents["OECD:CL_X(1.0)"]

    def test_unknown_codelist_empty(self, seeded_meta):
        """Unknown codelist id → empty dict."""
        assert seeded_meta.get_codelist_hierarchy("NOPE") == {}


class TestGetIndicatorTree:
    """Coverage for IndicatorMixin.get_indicator_tree."""

    def test_returns_empty_when_no_indicator_dim(self, seeded_meta):
        """No indicator dimension at all → empty list."""
        with patch.object(seeded_meta, "_find_indicator_dimension", return_value=None):
            assert seeded_meta.get_indicator_tree(_SHORT_ID) == []

    def test_returns_empty_when_no_available_codes(self, seeded_meta):
        """No codes available for the indicator dimension → empty list."""
        seeded_meta._dataflow_constraints[_FULL_ID]["MEASURE"] = []
        seeded_meta._dataflow_parameters_cache.pop(_FULL_ID, None)
        assert seeded_meta.get_indicator_tree(_SHORT_ID) == []

    def test_basic_tree_built(self, seeded_meta):
        """Builds a tree with parent linkage from _codelist_parents."""
        seeded_meta._codelist_parents["OECD:CL_MEASURE(1.0)"] = {"PPI": "CPI"}
        seeded_meta._dataflow_constraints[_FULL_ID]["MEASURE"] = ["CPI", "PPI"]
        seeded_meta._dataflow_parameters_cache.pop(_FULL_ID, None)
        tree = seeded_meta.get_indicator_tree(_SHORT_ID)
        roots = [n["code"] for n in tree]
        assert "CPI" in roots
        cpi = next(n for n in tree if n["code"] == "CPI")
        child_codes = [c["code"] for c in cpi["children"]]
        assert "PPI" in child_codes


class TestFindCodelistByPrefix:
    """Coverage for IndicatorMixin._find_codelist_by_prefix."""

    def test_returns_none_on_unparsable_key(self, seeded_meta):
        """Non-conformant codelist id returns None."""
        assert seeded_meta._find_codelist_by_prefix("not-a-codelist-key") is None

    def test_merges_across_agency_prefixes(self, seeded_meta):
        """Dotted-agency entries are merged with shorter agency prefixes."""
        seeded_meta.codelists["OECD.SDD.TPS:CL_T(1.0)"] = {"A": "From SDD"}
        seeded_meta.codelists["OECD.SDD:CL_T(1.0)"] = {"B": "From OECD.SDD"}
        seeded_meta.codelists["OECD:CL_T(1.0)"] = {"C": "From OECD"}
        result = seeded_meta._find_codelist_by_prefix("OECD.SDD.TPS:CL_T(1.0)")
        assert result is not None
        assert "A" in result and "B" in result and "C" in result

    def test_returns_none_when_no_match(self, seeded_meta):
        """No matching codelists in cache → None."""
        assert seeded_meta._find_codelist_by_prefix("OECD:CL_NONE(1.0)") is None


class TestGetCodelist:
    """Coverage for IndicatorMixin._get_codelist."""

    def test_returns_exact_match(self, seeded_meta):
        """An exact-key hit takes priority."""
        result = seeded_meta._get_codelist("OECD:CL_AREA(1.0)")
        assert result["USA"] == "United States"

    def test_returns_exact_when_prefix_match_none(self, seeded_meta):
        """Exact returned when key is non-conformant and prefix scan returns None."""
        seeded_meta.codelists["BARE_KEY"] = {"X": "Xlabel"}
        result = seeded_meta._get_codelist("BARE_KEY")
        assert result == {"X": "Xlabel"}

    def test_returns_prefix_match_when_no_exact(self, seeded_meta):
        """Falls back to prefix scan when the exact key is absent."""
        seeded_meta.codelists.clear()
        seeded_meta.codelists["OECD:CL_FOO(2.0)"] = {"X": "Xlabel"}
        result = seeded_meta._get_codelist("OECD:CL_FOO(1.0)")
        assert result == {"X": "Xlabel"}

    def test_merged_returns_when_prefix_larger(self, seeded_meta):
        """When the prefix match has more codes than exact, merges and returns."""
        seeded_meta.codelists["OECD.SDD:CL_FOO(1.0)"] = {"A": "A"}
        seeded_meta.codelists["OECD.SDD:CL_FOO(2.0)"] = {
            "A": "A v2",
            "B": "B",
            "C": "C",
        }
        result = seeded_meta._get_codelist("OECD.SDD:CL_FOO(1.0)")
        assert "A" in result and "B" in result and "C" in result
        assert result["A"] == "A"

    def test_exact_when_larger_than_prefix(self, seeded_meta):
        """Exact dict wins when prefix match isn't larger."""
        seeded_meta.codelists["OECD.SDD:CL_BAR(1.0)"] = {"A": "A", "B": "B"}
        seeded_meta.codelists["OECD.SDD:CL_BAR(2.0)"] = {"A": "A2"}
        result = seeded_meta._get_codelist("OECD.SDD:CL_BAR(1.0)")
        assert result == {"A": "A", "B": "B"}

    def test_fetches_when_no_match(self, seeded_meta):
        """When neither exact nor prefix matches, _fetch_single_codelist runs."""
        seeded_meta.codelists.clear()
        with patch.object(
            seeded_meta, "_fetch_single_codelist", return_value={"X": "Y"}
        ) as mock:
            result = seeded_meta._get_codelist("OECD:CL_UNKNOWN(1.0)", "DF_TEST")
        assert result == {"X": "Y"}
        mock.assert_called_once_with("OECD:CL_UNKNOWN(1.0)", "DF_TEST")


class TestFetchSingleCodelist:
    """Coverage for IndicatorMixin._fetch_single_codelist."""

    def _mock_response(self, codelists):
        """Build a mocked response object with .json() returning structure data."""
        resp = MagicMock()
        resp.json.return_value = {"data": {"codelists": codelists}}
        return resp

    def test_parses_qualified_codelist_id(self, seeded_meta):
        """A fully-qualified codelist key is parsed for agency/bare/version."""
        resp = self._mock_response(
            [
                {
                    "id": "CL_FOO",
                    "agencyID": "OECD",
                    "version": "1.0",
                    "codes": [{"id": "A", "names": {"en": "A label"}}],
                }
            ]
        )
        with patch(
            "openbb_oecd.utils.metadata._helpers._make_request", return_value=resp
        ) as mock_req:
            result = seeded_meta._fetch_single_codelist("OECD:CL_FOO(1.0)")
        assert result == {"A": "A label"}
        url = mock_req.call_args.args[0]
        assert "/codelist/OECD/CL_FOO/1.0" in url
        assert seeded_meta._cache_dirty is True

    def test_bare_id_uses_dataflow_agency(self, seeded_meta):
        """When key has no agency/version, agency is looked up from the dataflow."""
        resp = self._mock_response(
            [
                {
                    "id": "CL_FOO",
                    "agencyID": "OECD",
                    "version": "",
                    "codes": [{"id": "B", "names": {"en": "B"}}],
                }
            ]
        )
        with patch(
            "openbb_oecd.utils.metadata._helpers._make_request", return_value=resp
        ) as mock_req:
            seeded_meta._fetch_single_codelist("CL_FOO", _SHORT_ID)
        url = mock_req.call_args.args[0]
        assert "/codelist/OECD/CL_FOO" in url
        assert "/codelist/OECD/CL_FOO/" not in url.split("?")[0].rstrip("OECD/CL_FOO")

    def test_bare_id_no_dataflow_uses_all_agency(self, seeded_meta):
        """When no _dataflow_id is given, agency defaults to 'all'."""
        resp = self._mock_response([])
        with patch(
            "openbb_oecd.utils.metadata._helpers._make_request", return_value=resp
        ) as mock_req:
            seeded_meta._fetch_single_codelist("CL_FOO")
        url = mock_req.call_args.args[0]
        assert "/codelist/all/CL_FOO" in url

    def test_bare_id_with_full_dataflow_id(self, seeded_meta):
        """Full dataflow id (containing '@') is used verbatim for agency lookup."""
        resp = self._mock_response(
            [
                {
                    "id": "CL_FOO",
                    "agencyID": "OECD",
                    "version": "",
                    "codes": [{"id": "Z", "names": {"en": "Z"}}],
                }
            ]
        )
        with patch(
            "openbb_oecd.utils.metadata._helpers._make_request", return_value=resp
        ) as mock_req:
            seeded_meta._fetch_single_codelist("CL_FOO", _FULL_ID)
        url = mock_req.call_args.args[0]
        assert "/codelist/OECD/CL_FOO" in url

    def test_bare_id_with_unknown_dataflow_keeps_all(self, seeded_meta):
        """An unknown dataflow id leaves agency as 'all'."""
        resp = self._mock_response([])
        with (
            patch(
                "openbb_oecd.utils.metadata._helpers._make_request", return_value=resp
            ) as mock_req,
            patch.object(
                seeded_meta, "_resolve_dataflow_id", return_value="UNKNOWN@UNKNOWN"
            ),
        ):
            seeded_meta._fetch_single_codelist("CL_FOO", "UNKNOWN_DF")
        url = mock_req.call_args.args[0]
        assert "/codelist/all/CL_FOO" in url

    def test_updates_existing_codelist(self, seeded_meta):
        """An existing codelist entry is updated in place, not replaced."""
        seeded_meta.codelists["OECD:CL_FOO(1.0)"] = {"OLD": "old label"}
        resp = self._mock_response(
            [
                {
                    "id": "CL_FOO",
                    "agencyID": "OECD",
                    "version": "1.0",
                    "codes": [{"id": "NEW", "names": {"en": "new"}}],
                }
            ]
        )
        with patch(
            "openbb_oecd.utils.metadata._helpers._make_request", return_value=resp
        ):
            seeded_meta._fetch_single_codelist("OECD:CL_FOO(1.0)")
        merged = seeded_meta.codelists["OECD:CL_FOO(1.0)"]
        assert merged == {"OLD": "old label", "NEW": "new"}

    def test_updates_existing_parents(self, seeded_meta):
        """An existing codelist parents entry is merged, not overwritten."""
        seeded_meta._codelist_parents["OECD:CL_FOO(1.0)"] = {"X": "OLD_PARENT"}
        resp = self._mock_response(
            [
                {
                    "id": "CL_FOO",
                    "agencyID": "OECD",
                    "version": "1.0",
                    "codes": [
                        {"id": "Y", "names": {"en": "Y label"}, "parent": "NEW_PARENT"},
                    ],
                }
            ]
        )
        with patch(
            "openbb_oecd.utils.metadata._helpers._make_request", return_value=resp
        ):
            seeded_meta._fetch_single_codelist("OECD:CL_FOO(1.0)")
        parents = seeded_meta._codelist_parents["OECD:CL_FOO(1.0)"]
        assert parents == {"X": "OLD_PARENT", "Y": "NEW_PARENT"}

    def test_new_parents_inserted(self, seeded_meta):
        """A new codelist's parent mapping is inserted when absent."""
        seeded_meta._codelist_parents.pop("OECD:CL_NEW(1.0)", None)
        resp = self._mock_response(
            [
                {
                    "id": "CL_NEW",
                    "agencyID": "OECD",
                    "version": "1.0",
                    "codes": [
                        {"id": "P", "names": {"en": "P"}},
                        {"id": "C", "names": {"en": "C"}, "parent": "P"},
                    ],
                }
            ]
        )
        with patch(
            "openbb_oecd.utils.metadata._helpers._make_request", return_value=resp
        ):
            seeded_meta._fetch_single_codelist("OECD:CL_NEW(1.0)")
        assert seeded_meta._codelist_parents["OECD:CL_NEW(1.0)"] == {"C": "P"}

    def test_exception_returns_empty(self, seeded_meta):
        """A network/parse error is silently caught and returns {}."""
        with patch(
            "openbb_oecd.utils.metadata._helpers._make_request",
            side_effect=RuntimeError("network down"),
        ):
            result = seeded_meta._fetch_single_codelist("OECD:CL_FOO(1.0)")
        assert result == {}
