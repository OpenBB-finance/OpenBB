"""Unit tests for openbb_oecd.utils.helpers."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_oecd.utils.helpers import (
    _build_dimension_lookups,
    _guess_primary_dimension,
    _parse_compound_code,
    _raise_invalid_codes_error,
    detect_indicator_dimensions,
    detect_transform_dimension,
    normalize_country_label,
    oecd_date_to_python_date,
    parse_search_query,
    resolve_country_code,
)
from openbb_oecd.utils.metadata import OecdMetadata

_FULL_ID = "DSD_TEST@DF_TEST"
_SHORT_ID = "DF_TEST"


class TestOecdDateToPythonDate:
    """Tests for oecd_date_to_python_date."""

    def test_annual(self):
        """Year-only string returns January 1 date."""
        assert oecd_date_to_python_date("2024") == date(2024, 1, 1)

    def test_quarterly(self):
        """Quarterly period returns first month of quarter."""
        assert oecd_date_to_python_date("2024-Q3") == date(2024, 7, 1)

    def test_monthly(self):
        """Monthly period returns first of month."""
        assert oecd_date_to_python_date("2024-06") == date(2024, 6, 1)

    def test_daily(self):
        """Daily period parsed directly."""
        assert oecd_date_to_python_date("2024-03-15") == date(2024, 3, 15)

    def test_int_input(self):
        """Integer year is accepted."""
        assert oecd_date_to_python_date(2024) == date(2024, 1, 1)

    def test_empty_string(self):
        """Empty string returns None."""
        assert oecd_date_to_python_date("") is None

    def test_none(self):
        """None returns None."""
        assert oecd_date_to_python_date(None) is None  # type: ignore[arg-type]

    def test_whitespace_only(self):
        """Whitespace-only string returns None."""
        assert oecd_date_to_python_date("   ") is None

    def test_zero(self):
        """Zero (falsy) returns None."""
        assert oecd_date_to_python_date(0) is None

    def test_malformed_long_string_truncation_path(self):
        """Long unparsable string falls back to first 10 chars."""
        result = oecd_date_to_python_date("2024-03-15T00:00:00")
        assert result == date(2024, 3, 15)

    def test_completely_invalid(self):
        """Garbage input returns None via final fallback."""
        assert oecd_date_to_python_date("not-a-date") is None

    def test_short_invalid(self):
        """Short unrecognized string returns None."""
        assert oecd_date_to_python_date("xyz") is None


class TestNormalizeCountryLabel:
    """Tests for normalize_country_label."""

    def test_basic(self):
        """Plain label is lower_snake_cased."""
        assert normalize_country_label("United States") == "united_states"

    def test_china_override(self):
        """Verbose China label is collapsed to override."""
        assert normalize_country_label("China (People's Republic of)") == "china"

    def test_czech_override(self):
        """Czech Republic maps to czechia."""
        assert normalize_country_label("Czech Republic") == "czechia"

    def test_korea_override(self):
        """Korea (Republic of) maps to korea."""
        assert normalize_country_label("Korea, Republic of") == "korea"

    def test_eu27_override(self):
        """EU27 label is shortened."""
        assert (
            normalize_country_label("European Union (27 countries from 01/02/2020)")
            == "eu27"
        )

    def test_eu15_override(self):
        """EU15 label is shortened."""
        assert normalize_country_label("European Union (15 countries)") == "eu15"

    def test_euro_area_override(self):
        """Euro area evolving composition maps to euro_area."""
        assert (
            normalize_country_label("Euro area (evolving composition)") == "euro_area"
        )

    def test_oecd_non_euro_override(self):
        """OECD excluding euro area maps to oecd_non_euro_area."""
        assert (
            normalize_country_label("OECD excluding the euro area")
            == "oecd_non_euro_area"
        )

    def test_asia5_override(self):
        """Major five Asia economies maps to asia5."""
        assert normalize_country_label("Major five Asia economies") == "asia5"

    def test_europe4_override(self):
        """Major four European countries maps to europe4."""
        assert normalize_country_label("Major four European countries") == "europe4"

    def test_dae_override(self):
        """Dynamic Asian economies maps to dae."""
        assert normalize_country_label("Dynamic Asian economies") == "dae"

    def test_other_oil_override(self):
        """Other major oil producers is collapsed."""
        assert normalize_country_label("Other major oil producers") == "other_major_oil"

    def test_rest_of_world_override(self):
        """Rest of the world maps to rest_of_world."""
        assert normalize_country_label("Rest of the world") == "rest_of_world"

    def test_eu22_oecd_override(self):
        """EU22 OECD members maps to eu22_oecd."""
        assert (
            normalize_country_label("European Union (22 countries in OECD)")
            == "eu22_oecd"
        )

    def test_accented(self):
        """Combining marks are stripped."""
        assert normalize_country_label("Türkiye") == "turkiye"

    def test_strips_punctuation(self):
        """Non-alphanumeric chars are replaced by underscores."""
        assert normalize_country_label("New Zealand!") == "new_zealand"

    def test_leading_trailing_whitespace(self):
        """Outer whitespace is removed."""
        assert normalize_country_label("  Germany  ") == "germany"


class TestParseSearchQuery:
    """Tests for parse_search_query."""

    def test_single_term(self):
        """Single bare term yields one group."""
        assert parse_search_query("gdp") == [["gdp"]]

    def test_implicit_or(self):
        """Multiple bare terms within a single group act as OR alternatives."""
        assert parse_search_query("gdp income") == [["gdp", "income"]]

    def test_explicit_plus_creates_and_group(self):
        """The + operator separates AND groups."""
        assert parse_search_query("consumer + price") == [["consumer"], ["price"]]

    def test_pipe_skipped(self):
        """Pipe is a no-op separator between OR alternatives."""
        assert parse_search_query("gdp | income") == [["gdp", "income"]]

    def test_quoted_phrase(self):
        """Double-quoted phrases preserve internal spaces."""
        assert parse_search_query('gdp "per capita" | income') == [
            ["gdp", "per capita", "income"]
        ]

    def test_empty_string(self):
        """Empty query returns empty list."""
        assert parse_search_query("") == []

    def test_only_operators(self):
        """Operator-only input produces no groups."""
        assert parse_search_query("+ |") == []

    def test_case_folded(self):
        """Tokens are lower-cased."""
        assert parse_search_query("GDP") == [["gdp"]]


class TestParseCompoundCode:
    """Tests for _parse_compound_code."""

    def test_all_matched_single_part(self):
        """Single-part code mapped to its dimension."""
        c2d = {"CPI": "MEASURE"}
        matched, unmatched = _parse_compound_code("CPI", c2d)
        assert matched == [("MEASURE", "CPI")]
        assert unmatched == []

    def test_compound_multiple_dimensions(self):
        """Greedy matcher splits a compound across dimensions."""
        c2d = {"CPI": "MEASURE", "CP01": "EXPENDITURE", "N": "TRANSFORMATION"}
        matched, unmatched = _parse_compound_code("CPI_CP01_N", c2d)
        assert ("MEASURE", "CPI") in matched
        assert ("EXPENDITURE", "CP01") in matched
        assert ("TRANSFORMATION", "N") in matched
        assert unmatched == []

    def test_greedy_longest_first(self):
        """Greedy matcher prefers longest combined string."""
        c2d = {"FOO_BAR": "DIM_A", "FOO": "DIM_B", "BAR": "DIM_C"}
        matched, _ = _parse_compound_code("FOO_BAR", c2d)
        assert matched == [("DIM_A", "FOO_BAR")]

    def test_skips_duplicate_dimension(self):
        """Same dimension matched twice — the second occurrence is dropped."""
        c2d = {"A": "DIM_X", "B": "DIM_X"}
        matched, unmatched = _parse_compound_code("A_B", c2d)
        assert matched == [("DIM_X", "A")]
        assert unmatched == ["B"]

    def test_unmatched_parts_recorded(self):
        """Parts with no dimension lookup go to unmatched list."""
        c2d = {"CPI": "MEASURE"}
        matched, unmatched = _parse_compound_code("CPI_UNKNOWN", c2d)
        assert matched == [("MEASURE", "CPI")]
        assert unmatched == ["UNKNOWN"]

    def test_all_unmatched(self):
        """Completely unknown code produces empty matches."""
        matched, unmatched = _parse_compound_code("X_Y_Z", {})
        assert matched == []
        assert unmatched == ["X", "Y", "Z"]


class TestBuildDimensionLookups:
    """Tests for _build_dimension_lookups."""

    def test_uses_existing_metadata(self, seeded_meta):
        """Passing metadata avoids creating a new singleton."""
        c2d, by_dim, order = _build_dimension_lookups(_SHORT_ID, seeded_meta)
        assert "CPI" in c2d
        assert c2d["CPI"] == "MEASURE"
        assert "CPI" in by_dim["MEASURE"]
        assert "MEASURE" in order

    def test_excludes_country_and_freq(self, seeded_meta):
        """REF_AREA and FREQ are excluded from code/order maps."""
        c2d, by_dim, order = _build_dimension_lookups(_SHORT_ID, seeded_meta)
        assert "USA" not in c2d
        assert "REF_AREA" not in by_dim
        assert "REF_AREA" not in order
        assert "FREQ" not in order

    def test_default_metadata_creation(self, monkeypatch):
        """When metadata=None, function instantiates OecdMetadata."""
        OecdMetadata._reset()
        monkeypatch.setattr(OecdMetadata, "_load_from_cache", lambda self: True)
        with (
            patch(
                "openbb_oecd.utils.metadata.OecdMetadata.get_dataflow_parameters",
                return_value={},
            ),
            patch(
                "openbb_oecd.utils.metadata.OecdMetadata._resolve_dataflow_id",
                return_value=_FULL_ID,
            ),
            patch(
                "openbb_oecd.utils.metadata.OecdMetadata._ensure_structure",
                return_value=None,
            ),
        ):
            c2d, by_dim, order = _build_dimension_lookups("X", metadata=None)
        assert c2d == {}
        assert by_dim == {}
        assert order == []
        OecdMetadata._reset()

    def test_parameters_failure_silenced(self, seeded_meta):
        """Exception from get_dataflow_parameters is swallowed."""
        with patch.object(
            seeded_meta, "get_dataflow_parameters", side_effect=RuntimeError("boom")
        ):
            c2d, by_dim, order = _build_dimension_lookups(_SHORT_ID, seeded_meta)
        assert c2d == {}
        assert by_dim == {}

    def test_dsd_failure_silenced(self, seeded_meta):
        """Exception during DSD lookup leaves dimension_order empty."""
        with patch.object(
            seeded_meta, "_resolve_dataflow_id", side_effect=RuntimeError("nope")
        ):
            _, _, order = _build_dimension_lookups(_SHORT_ID, seeded_meta)
        assert order == []

    def test_skips_value_without_code(self, seeded_meta):
        """Codelist entries without a 'value' key are skipped."""
        with patch.object(
            seeded_meta,
            "get_dataflow_parameters",
            return_value={
                "MEASURE": [
                    {"value": "CPI", "label": "Consumer Price Index"},
                    {"label": "no-value"},
                ]
            },
        ):
            c2d, by_dim, _ = _build_dimension_lookups(_SHORT_ID, seeded_meta)
        assert "CPI" in c2d
        assert by_dim["MEASURE"] == {"CPI"}

    def test_first_dimension_wins_for_duplicate_code(self, seeded_meta):
        """If two dimensions share a code, the first one wins."""
        with patch.object(
            seeded_meta,
            "get_dataflow_parameters",
            return_value={
                "DIM_A": [{"value": "SHARED", "label": "A"}],
                "DIM_B": [{"value": "SHARED", "label": "B"}],
            },
        ):
            c2d, by_dim, _ = _build_dimension_lookups(_SHORT_ID, seeded_meta)
        assert c2d["SHARED"] == "DIM_A"
        assert "SHARED" in by_dim["DIM_A"]
        assert "SHARED" in by_dim["DIM_B"]

    def test_excluded_dimensions_not_in_order(self, seeded_meta):
        """Trailing/excluded dimensions are not in the dimension_order list."""
        seeded_meta.datastructures[_FULL_ID]["dimensions"].extend(
            [
                {
                    "id": "TRANSFORMATION",
                    "position": 4,
                    "codelist_id": "OECD:CL_T(1.0)",
                    "concept_id": "TRANSFORMATION",
                    "name": "Transform",
                },
                {
                    "id": "UNIT_MEASURE",
                    "position": 5,
                    "codelist_id": "OECD:CL_U(1.0)",
                    "concept_id": "UNIT_MEASURE",
                    "name": "Unit",
                },
                {
                    "id": "TIME_PERIOD",
                    "position": 6,
                    "codelist_id": "",
                    "concept_id": "TIME_PERIOD",
                    "name": "Time",
                },
                {
                    "id": "MY_TRANSFORM",
                    "position": 7,
                    "codelist_id": "",
                    "concept_id": "MY_TRANSFORM",
                    "name": "X",
                },
            ]
        )
        _, _, order = _build_dimension_lookups(_SHORT_ID, seeded_meta)
        assert order == ["MEASURE"]


class TestGuessPrimaryDimension:
    """Tests for _guess_primary_dimension."""

    def test_picks_first_candidate(self):
        """First candidate from the list takes priority."""
        result = _guess_primary_dimension(
            {"SUBJECT": {"X"}, "MEASURE": {"Y"}, "OTHER": {"Z"}}
        )
        assert result == "MEASURE"

    def test_falls_back_to_first_dim(self):
        """No candidate match — first non-candidate dim is returned."""
        result = _guess_primary_dimension({"WEIRD": {"X"}})
        assert result == "WEIRD"

    def test_empty_returns_indicator(self):
        """Empty input returns the literal 'INDICATOR'."""
        assert _guess_primary_dimension({}) == "INDICATOR"


class TestDetectIndicatorDimensions:
    """Tests for detect_indicator_dimensions."""

    def test_simple_code(self, seeded_meta):
        """Code mapped to its declared dimension."""
        result = detect_indicator_dimensions(_SHORT_ID, ["CPI"], seeded_meta)
        assert result == {"MEASURE": ["CPI"]}

    def test_wildcard(self, seeded_meta):
        """Wildcard '*' goes to the primary dimension."""
        result = detect_indicator_dimensions(_SHORT_ID, ["*"], seeded_meta)
        assert "MEASURE" in result
        assert result["MEASURE"] == ["*"]

    def test_compound_code(self, seeded_meta):
        """Compound code is split across known dimensions."""
        with patch.object(
            seeded_meta,
            "get_dataflow_parameters",
            return_value={
                "MEASURE": [{"value": "CPI", "label": "CPI"}],
                "EXPENDITURE": [{"value": "CP01", "label": "Food"}],
            },
        ):
            result = detect_indicator_dimensions(_SHORT_ID, ["CPI_CP01"], seeded_meta)
        assert "CPI" in result["MEASURE"]
        assert "CP01" in result["EXPENDITURE"]

    def test_compound_part_already_in_list(self, seeded_meta):
        """Compound parts are not added twice."""
        with patch.object(
            seeded_meta,
            "get_dataflow_parameters",
            return_value={
                "MEASURE": [{"value": "CPI", "label": "CPI"}],
                "EXPENDITURE": [{"value": "CP01", "label": "Food"}],
            },
        ):
            result = detect_indicator_dimensions(
                _SHORT_ID, ["CPI_CP01", "CPI_CP01"], seeded_meta
            )
        assert result["MEASURE"] == ["CPI"]
        assert result["EXPENDITURE"] == ["CP01"]

    def test_invalid_code_raises(self, seeded_meta):
        """Unknown code raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid indicator code"):
            detect_indicator_dimensions(_SHORT_ID, ["NOPE_XYZ"], seeded_meta)

    def test_partial_match_raises(self, seeded_meta):
        """Compound with unmatched tail raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid indicator code"):
            detect_indicator_dimensions(_SHORT_ID, ["CPI_NOPE"], seeded_meta)

    def test_fallback_on_unexpected_exception(self, seeded_meta):
        """Non-OpenBB errors fall back to generic INDICATOR dimension."""
        with patch(
            "openbb_oecd.utils.helpers._build_dimension_lookups",
            side_effect=RuntimeError("boom"),
        ):
            result = detect_indicator_dimensions(_SHORT_ID, ["A", "B"], seeded_meta)
        assert result == {"INDICATOR": ["A", "B"]}

    def test_default_metadata_branch(self, monkeypatch):
        """Default metadata path: creates new OecdMetadata."""
        OecdMetadata._reset()
        monkeypatch.setattr(OecdMetadata, "_load_from_cache", lambda self: True)
        with patch(
            "openbb_oecd.utils.helpers._build_dimension_lookups",
            return_value=({"CPI": "MEASURE"}, {"MEASURE": {"CPI"}}, ["MEASURE"]),
        ):
            result = detect_indicator_dimensions(_SHORT_ID, ["CPI"], metadata=None)
        assert result == {"MEASURE": ["CPI"]}
        OecdMetadata._reset()


class TestRaiseInvalidCodesError:
    """Tests for _raise_invalid_codes_error."""

    def test_no_unmatched_parts(self):
        """Entry with empty unmatched list still raises."""
        with pytest.raises(OpenBBError) as exc:
            _raise_invalid_codes_error(_SHORT_ID, [("CPI", [])], {}, {}, [])
        assert "'CPI'" in str(exc.value)

    def test_unmatched_with_known_dimension(self):
        """Unmatched part raises error referencing valid neighbour dim."""
        c2d = {"CPI": "MEASURE"}
        by_dim = {"MEASURE": {"CPI"}, "EXPENDITURE": {"CP01", "CP02"}}
        order = ["MEASURE", "EXPENDITURE"]
        with pytest.raises(OpenBBError) as exc:
            _raise_invalid_codes_error(
                _SHORT_ID, [("CPI_BAD", ["BAD"])], c2d, by_dim, order
            )
        msg = str(exc.value)
        assert "BAD" in msg
        assert "EXPENDITURE" in msg

    def test_unmatched_without_matched_segments(self):
        """Code with no matched segments uses positional expected_pos."""
        by_dim = {"MEASURE": {"CPI"}, "EXP": {"CP01"}}
        order = ["MEASURE", "EXP"]
        with pytest.raises(OpenBBError) as exc:
            _raise_invalid_codes_error(
                _SHORT_ID, [("FOO_BAR", ["FOO", "BAR"])], {}, by_dim, order
            )
        msg = str(exc.value)
        assert "FOO" in msg
        assert "BAR" in msg

    def test_expected_pos_out_of_range(self):
        """Segment beyond effective_order length is labelled 'unrecognized'."""
        by_dim: dict = {}
        order: list = []
        with pytest.raises(OpenBBError) as exc:
            _raise_invalid_codes_error(_SHORT_ID, [("FOO", ["FOO"])], {}, by_dim, order)
        assert "unrecognized" in str(exc.value)

    def test_country_dim_kept_in_effective_order(self):
        """When code contains a country dim, country dims stay in effective_order."""
        c2d = {"USA": "REF_AREA"}
        by_dim = {"REF_AREA": {"USA"}, "MEASURE": {"CPI"}}
        order = ["REF_AREA", "MEASURE"]
        with pytest.raises(OpenBBError) as exc:
            _raise_invalid_codes_error(
                _SHORT_ID, [("USA_BAD", ["BAD"])], c2d, by_dim, order
            )
        assert "BAD" in str(exc.value)
        assert "MEASURE" in str(exc.value)


class TestDetectTransformDimension:
    """Tests for detect_transform_dimension."""

    def test_no_transform_or_unit_dim(self, seeded_meta):
        """Dataflow with no transform/unit dim returns all None."""
        t_dim, u_dim, t_lookup, u_lookup = detect_transform_dimension(
            _SHORT_ID, seeded_meta
        )
        assert t_dim is None
        assert u_dim is None
        assert t_lookup == {}
        assert u_lookup == {}

    def test_transform_dim_index_label(self, seeded_meta):
        """Index label is mapped to 'index' key."""
        with patch.object(
            seeded_meta,
            "get_dataflow_parameters",
            return_value={
                "TRANSFORMATION": [
                    {"value": "IX", "label": "Index"},
                    {"value": "YOY", "label": "Year-over-year change"},
                    {"value": "POP", "label": "Period-over-period change"},
                    {"value": "PCT_GDP", "label": "Percent of GDP"},
                    {"value": "DOM", "label": "Domestic currency"},
                ]
            },
        ):
            t_dim, _, t_lookup, _ = detect_transform_dimension(_SHORT_ID, seeded_meta)
        assert t_dim == "TRANSFORMATION"
        assert t_lookup["index"] == "IX"
        assert t_lookup["yoy"] == "YOY"
        assert t_lookup["period"] == "POP"
        assert t_lookup["percent_gdp"] == "PCT_GDP"
        assert t_lookup["currency"] == "DOM"
        assert t_lookup["ix"] == "IX"

    def test_transform_prefers_simple_code(self, seeded_meta):
        """When multiple codes match the same friendly key, simple one wins."""
        with patch.object(
            seeded_meta,
            "get_dataflow_parameters",
            return_value={
                "TRANSFORMATION": [
                    {"value": "SRP_IX", "label": "Index"},
                    {"value": "IX", "label": "Index"},
                ]
            },
        ):
            _, _, t_lookup, _ = detect_transform_dimension(_SHORT_ID, seeded_meta)
        assert t_lookup["index"] == "IX"

    def test_adjustment_dim_recognized(self, seeded_meta):
        """ADJUSTMENT (without TRANSFORM in name) is also recognized."""
        with patch.object(
            seeded_meta,
            "get_dataflow_parameters",
            return_value={
                "ADJUSTMENT": [
                    {"value": "SA", "label": "Seasonally adjusted index"},
                ]
            },
        ):
            t_dim, _, t_lookup, _ = detect_transform_dimension(_SHORT_ID, seeded_meta)
        assert t_dim == "ADJUSTMENT"
        assert t_lookup["index"] == "SA"

    def test_unit_dim_friendly_lookups(self, seeded_meta):
        """Unit dimension builds the unit lookup map."""
        with patch.object(
            seeded_meta,
            "get_dataflow_parameters",
            return_value={
                "UNIT_MEASURE": [
                    {"value": "USD", "label": "US dollar"},
                    {"value": "EUR", "label": "Euro"},
                    {"value": "IX", "label": "Index"},
                    {"value": "NCU", "label": "National currency"},
                    {"value": "PT", "label": "Percent"},
                ]
            },
        ):
            _, u_dim, _, u_lookup = detect_transform_dimension(_SHORT_ID, seeded_meta)
        assert u_dim == "UNIT_MEASURE"
        assert u_lookup["usd"] == "USD"
        assert u_lookup["eur"] == "EUR"
        assert u_lookup["index"] == "IX"
        assert u_lookup["local"] == "NCU"
        assert u_lookup["percent"] == "PT"
        assert u_lookup["pt"] == "PT"

    def test_metadata_exception_silenced(self, seeded_meta):
        """KeyError/ValueError from params returns the empty defaults."""
        with patch.object(
            seeded_meta,
            "get_dataflow_parameters",
            side_effect=KeyError("missing"),
        ):
            t_dim, u_dim, t_lookup, u_lookup = detect_transform_dimension(
                _SHORT_ID, seeded_meta
            )
        assert t_dim is None
        assert u_dim is None
        assert t_lookup == {}
        assert u_lookup == {}

    def test_default_metadata_branch(self, monkeypatch):
        """metadata=None instantiates the singleton."""
        OecdMetadata._reset()
        monkeypatch.setattr(OecdMetadata, "_load_from_cache", lambda self: True)
        with patch(
            "openbb_oecd.utils.metadata.OecdMetadata.get_dataflow_parameters",
            return_value={},
        ):
            t_dim, u_dim, t_lookup, u_lookup = detect_transform_dimension(
                _SHORT_ID, metadata=None
            )
        assert t_dim is None
        assert u_dim is None
        assert t_lookup == {}
        assert u_lookup == {}
        OecdMetadata._reset()

    def test_index_change_excluded(self, seeded_meta):
        """Label containing 'index' and 'change' is not treated as index."""
        with patch.object(
            seeded_meta,
            "get_dataflow_parameters",
            return_value={
                "TRANSFORMATION": [
                    {"value": "CH", "label": "Index change percent"},
                ]
            },
        ):
            _, _, t_lookup, _ = detect_transform_dimension(_SHORT_ID, seeded_meta)
        assert "index" not in t_lookup

    def test_period_without_change_excluded(self, seeded_meta):
        """Label with 'period' but no 'change' is not treated as period."""
        with patch.object(
            seeded_meta,
            "get_dataflow_parameters",
            return_value={
                "TRANSFORMATION": [
                    {"value": "PR", "label": "Reporting period"},
                ]
            },
        ):
            _, _, t_lookup, _ = detect_transform_dimension(_SHORT_ID, seeded_meta)
        assert "period" not in t_lookup


class TestResolveCountryCode:
    """Tests for resolve_country_code."""

    def test_no_dataflow_uppercases_input(self):
        """Without a dataflow, returns upper-cased trimmed input."""
        assert resolve_country_code("  jpn ") == "JPN"

    def test_resolves_via_metadata(self, seeded_meta):
        """Resolves country name through metadata when dataflow provided."""
        assert (
            resolve_country_code("United States", seeded_meta, dataflow=_SHORT_ID)
            == "USA"
        )

    def test_unresolved_falls_back_to_upper(self, seeded_meta):
        """Empty resolution result falls back to upper-cased input."""
        with patch.object(seeded_meta, "resolve_country_codes", return_value=[]):
            assert resolve_country_code("xyz", seeded_meta, dataflow=_SHORT_ID) == "XYZ"

    def test_resolve_raises_falls_back(self, seeded_meta):
        """Exception in resolver is silenced and input upper-cased."""
        with patch.object(
            seeded_meta, "resolve_country_codes", side_effect=RuntimeError("nope")
        ):
            assert resolve_country_code("abc", seeded_meta, dataflow=_SHORT_ID) == "ABC"

    def test_default_metadata_branch(self, monkeypatch):
        """metadata=None constructs a singleton."""
        OecdMetadata._reset()
        monkeypatch.setattr(OecdMetadata, "_load_from_cache", lambda self: True)
        result = resolve_country_code("jpn", metadata=None, dataflow=None)
        assert result == "JPN"
        OecdMetadata._reset()
