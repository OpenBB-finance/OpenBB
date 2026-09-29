"""Tests for IMF helper utilities."""

# ruff: noqa: I001

from unittest.mock import MagicMock, patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_imf.utils.helpers import (
    _build_dimension_lookups,
    _parse_compound_code,
    build_codelist_to_hierarchies_map,
    build_hierarchy_to_codelist_map,
    build_time_period_params,
    detect_indicator_dimensions,
    detect_transform_dimension,
    extract_all_codelists_from_hierarchy,
    normalize_country_label,
    parse_agency_from_urn,
    parse_codelist_id_from_urn,
    parse_codelist_urn,
    parse_indicator_code_from_urn,
    parse_search_query,
    parse_time_period,
    resolve_country_code,
    translate_error_message,
)


class TestNormalizeCountryLabel:
    """Tests for normalize_country_label function."""

    def test_simple_name(self):
        """Test normalization of simple country names."""
        assert normalize_country_label("United States") == "united_states"
        assert normalize_country_label("Japan") == "japan"
        assert normalize_country_label("United Kingdom") == "united_kingdom"

    def test_name_with_comma(self):
        """Test normalization of names with comma suffix."""
        assert normalize_country_label("Armenia, Republic of") == "armenia"
        assert normalize_country_label("Korea, Republic of") == "korea"
        assert normalize_country_label("Iran, Islamic Republic of") == "iran"

    def test_name_with_parentheses(self):
        """Test normalization of names with parenthetical content."""
        assert normalize_country_label("Euro Area (EA)") == "euro_area"
        assert normalize_country_label("China (Mainland)") == "china"
        assert normalize_country_label("Taiwan (Province of China)") == "taiwan"

    def test_name_with_hyphen(self):
        """Test normalization of names with hyphens."""
        assert normalize_country_label("Guinea-Bissau") == "guinea_bissau"
        assert normalize_country_label("Timor-Leste") == "timor_leste"

    def test_mixed_cases(self):
        """Test normalization handles mixed cases."""
        assert normalize_country_label("UNITED STATES") == "united_states"
        assert normalize_country_label("united states") == "united_states"
        assert normalize_country_label("United STATES") == "united_states"


class TestResolveCountryCode:
    """Tests for resolve_country_code function."""

    @pytest.fixture
    def mock_metadata(self):
        """Create mock metadata with country codelist."""
        metadata = MagicMock()
        metadata._codelist_cache = {
            "CL_COUNTRY": {
                "USA": "United States",
                "JPN": "Japan",
                "GBR": "United Kingdom",
                "DEU": "Germany",
                "FRA": "France",
            }
        }
        return metadata

    def test_iso_code_passthrough(self, mock_metadata):
        """Test that valid ISO codes are passed through."""
        assert resolve_country_code("USA", mock_metadata) == "USA"
        assert resolve_country_code("JPN", mock_metadata) == "JPN"
        assert resolve_country_code("gbr", mock_metadata) == "GBR"

    def test_name_to_code_resolution(self, mock_metadata):
        """Test that country names are resolved to codes."""
        assert resolve_country_code("Japan", mock_metadata) == "JPN"
        assert resolve_country_code("japan", mock_metadata) == "JPN"
        assert resolve_country_code("United Kingdom", mock_metadata) == "GBR"

    def test_unrecognized_returns_uppercase(self, mock_metadata):
        """Test that unrecognized values are returned as uppercase."""
        assert resolve_country_code("XYZ", mock_metadata) == "XYZ"
        assert resolve_country_code("unknown", mock_metadata) == "UNKNOWN"

    def test_whitespace_handling(self, mock_metadata):
        """Test that whitespace is trimmed."""
        assert resolve_country_code("  USA  ", mock_metadata) == "USA"
        assert resolve_country_code(" Japan ", mock_metadata) == "JPN"

    def test_empty_codelist_cache(self):
        """Test handling when codelist cache is empty."""
        metadata = MagicMock()
        metadata._codelist_cache = {}
        assert resolve_country_code("USA", metadata) == "USA"


class TestDetectTransformDimension:
    """Tests for detect_transform_dimension function."""

    @pytest.fixture
    def mock_metadata_transform(self):
        """Mock metadata with TRANSFORM dimension."""
        with patch("openbb_imf.utils.metadata.ImfMetadata") as MockMetadata:
            mock_instance = MockMetadata.return_value
            mock_instance.get_dataflow_parameters.return_value = {
                "TRANSFORMATION": [
                    {"value": "IX", "label": "Index"},
                    {"value": "PC_PA", "label": "Year-over-year percent change"},
                    {"value": "PC_PP", "label": "Period-over-period percent change"},
                ],
                "COUNTRY": [
                    {"value": "USA", "label": "United States"},
                ],
            }
            yield MockMetadata

    @pytest.fixture
    def mock_metadata_unit(self):
        """Mock metadata with UNIT dimension."""
        with patch("openbb_imf.utils.metadata.ImfMetadata") as MockMetadata:
            mock_instance = MockMetadata.return_value
            mock_instance.get_dataflow_parameters.return_value = {
                "UNIT": [
                    {"value": "USD", "label": "US Dollar"},
                    {"value": "EUR", "label": "Euro"},
                    {"value": "XDC", "label": "Domestic currency"},
                    {"value": "IX", "label": "Index"},
                ],
                "COUNTRY": [
                    {"value": "USA", "label": "United States"},
                ],
            }
            yield MockMetadata

    def test_detect_transform_dimension(self, mock_metadata_transform):
        """Test detection of TRANSFORM dimension."""
        transform_dim, unit_dim, transform_lookup, unit_lookup = (
            detect_transform_dimension("CPI")
        )

        assert transform_dim == "TRANSFORMATION"
        assert unit_dim is None
        assert "index" in transform_lookup
        assert "yoy" in transform_lookup
        assert "period" in transform_lookup
        assert transform_lookup["index"] == "IX"
        assert transform_lookup["yoy"] == "PC_PA"
        assert transform_lookup["period"] == "PC_PP"

    def test_detect_unit_dimension(self, mock_metadata_unit):
        """Test detection of UNIT dimension."""
        transform_dim, unit_dim, transform_lookup, unit_lookup = (
            detect_transform_dimension("MFS_MA")
        )

        assert transform_dim is None
        assert unit_dim == "UNIT"
        assert "usd" in unit_lookup
        assert "eur" in unit_lookup
        assert "local" in unit_lookup
        assert "index" in unit_lookup
        assert unit_lookup["usd"] == "USD"
        assert unit_lookup["eur"] == "EUR"
        assert unit_lookup["local"] == "XDC"

    def test_no_transform_or_unit(self):
        """Test dataflow without transform or unit dimension."""
        with patch("openbb_imf.utils.metadata.ImfMetadata") as MockMetadata:
            mock_instance = MockMetadata.return_value
            mock_instance.get_dataflow_parameters.return_value = {
                "COUNTRY": [{"value": "USA", "label": "United States"}],
                "INDICATOR": [{"value": "GDP", "label": "GDP"}],
            }

            transform_dim, unit_dim, transform_lookup, unit_lookup = (
                detect_transform_dimension("WEO")
            )

            assert transform_dim is None
            assert unit_dim is None
            assert transform_lookup == {}
            assert unit_lookup == {}

    def test_direct_code_access(self, mock_metadata_transform):
        """Test that direct codes are also in lookup."""
        transform_dim, unit_dim, transform_lookup, unit_lookup = (
            detect_transform_dimension("CPI")
        )

        assert "ix" in transform_lookup
        assert "pc_pa" in transform_lookup
        assert transform_lookup["ix"] == "IX"

    def test_mixed_transform_and_unit(self):
        """Test detection when both TRANSFORM and UNIT dimensions exist."""
        with patch("openbb_imf.utils.metadata.ImfMetadata") as MockMetadata:
            mock_instance = MockMetadata.return_value
            mock_instance.get_dataflow_parameters.return_value = {
                "TRANSFORMATION": [
                    {"value": "IX", "label": "Index"},
                ],
                "UNIT": [
                    {"value": "USD", "label": "US Dollar"},
                ],
            }

            transform_dim, unit_dim, transform_lookup, unit_lookup = (
                detect_transform_dimension("MIXED")
            )

            assert transform_dim == "TRANSFORMATION"
            assert unit_dim == "UNIT"
            assert "index" in transform_lookup
            assert "usd" in unit_lookup


class TestDetectIndicatorDimensions:
    """Tests for detect_indicator_dimensions function."""

    def test_indicator_dimension_mapping(self):
        """Test that indicators are mapped to correct dimensions."""
        mock_metadata = MagicMock()
        mock_metadata.get_dataflow_parameters.return_value = {
            "INDICATOR": [
                {"value": "GDP", "label": "GDP"},
                {"value": "CPI", "label": "CPI"},
            ],
            "BOP_ACCOUNTING_ENTRY": [
                {"value": "CD_T", "label": "Current Account"},
            ],
        }
        mock_metadata.dataflows = {}
        mock_metadata.datastructures = {}

        result = detect_indicator_dimensions(
            "TEST", ["GDP", "CPI", "CD_T"], mock_metadata
        )

        assert "INDICATOR" in result
        assert "BOP_ACCOUNTING_ENTRY" in result
        assert "GDP" in result["INDICATOR"]
        assert "CPI" in result["INDICATOR"]
        assert "CD_T" in result["BOP_ACCOUNTING_ENTRY"]

    def test_fallback_to_indicator_dimension(self):
        """Test fallback when indicator not found in metadata."""
        mock_metadata = MagicMock()
        mock_metadata.get_dataflow_parameters.return_value = {
            "INDICATOR": [{"value": "GDP", "label": "GDP"}],
        }
        mock_metadata.dataflows = {}
        mock_metadata.datastructures = {}

        with pytest.raises(OpenBBError):
            detect_indicator_dimensions("TEST", ["GDP", "UNKNOWN"], mock_metadata)

    def test_compound_indicator_codes(self):
        """Test parsing of compound indicator codes."""
        mock_metadata = MagicMock()
        mock_metadata.get_dataflow_parameters.return_value = {
            "SECTOR": [{"value": "S1", "label": "Sector 1"}],
            "INDICATOR": [{"value": "I1", "label": "Indicator 1"}],
        }
        mock_metadata.dataflows = {}
        mock_metadata.datastructures = {}

        result = detect_indicator_dimensions("TEST", ["S1_I1"], mock_metadata)

        assert "SECTOR" in result
        assert "INDICATOR" in result
        assert "S1" in result["SECTOR"]
        assert "I1" in result["INDICATOR"]

    def test_wildcard_fallback(self):
        """Test wildcard fallback for missing dimensions in compound codes."""
        mock_metadata = MagicMock()
        mock_metadata.get_dataflow_parameters.return_value = {
            "SECTOR": [{"value": "S1", "label": "Sector 1"}],
            "INDICATOR": [{"value": "I1", "label": "Indicator 1"}],
            "FREQ": [{"value": "A", "label": "Annual"}],
        }
        mock_metadata.dataflows = {"TEST": {"structureRef": {"id": "DSD_TEST"}}}
        mock_metadata.datastructures = {
            "DSD_TEST": {
                "dimensions": [
                    {"id": "FREQ", "position": 1},
                    {"id": "SECTOR", "position": 2},
                    {"id": "INDICATOR", "position": 3},
                ]
            }
        }

        result = detect_indicator_dimensions("TEST", ["S1"], mock_metadata)

        assert "SECTOR" in result
        assert "S1" in result["SECTOR"]

    def test_detailed_error_message(self):
        """Test that error message contains helpful information."""
        mock_metadata = MagicMock()
        mock_metadata.get_dataflow_parameters.return_value = {
            "INDICATOR": [{"value": "GDP", "label": "GDP"}],
        }
        mock_metadata.dataflows = {}
        mock_metadata.datastructures = {}

        with pytest.raises(OpenBBError) as exc_info:
            detect_indicator_dimensions("TEST", ["INVALID"], mock_metadata)

        assert "Invalid indicator code(s)" in str(exc_info.value)
        assert "INVALID" in str(exc_info.value)
        assert "unrecognized" in str(exc_info.value)

    def test_exception_fallback(self):
        """Test fallback when metadata raises exception."""
        mock_metadata = MagicMock()
        mock_metadata.get_dataflow_parameters.side_effect = KeyError("Not found")
        mock_metadata.dataflows = {}
        mock_metadata.datastructures = {}

        with pytest.raises(OpenBBError):
            detect_indicator_dimensions("TEST", ["GDP", "CPI"], mock_metadata)


class TestBuildDimensionLookups:
    """Tests for _build_dimension_lookups."""

    def test_params_exception_handled(self):
        """Exception from get_dataflow_parameters is swallowed."""
        meta = MagicMock()
        meta.get_dataflow_parameters.side_effect = RuntimeError("boom")
        meta.dataflows = {}
        meta.datastructures = {}
        code_to_dim, codes_by_dim, dim_order = _build_dimension_lookups("X", meta)
        assert code_to_dim == {}
        assert codes_by_dim == {}
        assert dim_order == []

    def test_dim_order_skips_trailing_and_transform(self):
        """TIME_PERIOD/FREQUENCY/TRANSFORMATION-like dims are filtered out."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {}
        meta.dataflows = {"DF": {"structureRef": {"id": "DSD"}}}
        meta.datastructures = {
            "DSD": {
                "dimensions": [
                    {"id": "SECTOR"},
                    {"id": "FREQUENCY"},
                    {"id": "TIME_PERIOD"},
                    {"id": "TYPE_OF_TRANSFORMATION"},
                    {"id": "MY_TRANSFORM"},
                    {"id": "INDICATOR"},
                    {"id": ""},
                ]
            }
        }
        _ct, _cb, dim_order = _build_dimension_lookups("DF", meta)
        assert dim_order == ["SECTOR", "INDICATOR"]

    def test_dsd_exception_handled(self):
        """Exception inside DSD inspection is swallowed."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {}

        class _DataflowsRaises:
            def get(self, *_, **__):
                raise RuntimeError("nope")

        meta.dataflows = _DataflowsRaises()
        meta.datastructures = {}
        _ct, _cb, dim_order = _build_dimension_lookups("DF", meta)
        assert dim_order == []


class TestParseCompoundCode:
    """Tests for _parse_compound_code."""

    def test_unmatched_parts(self):
        """Unmatched parts are returned as-is."""
        code_to_dim = {"S1": "SECTOR"}
        matched, unmatched = _parse_compound_code("S1_X9_T", code_to_dim)
        assert matched == [("SECTOR", "S1")]
        assert unmatched == ["X9", "T"]

    def test_duplicate_dimension_skipped(self):
        """A second match for the same dimension is skipped."""
        code_to_dim = {"S1": "SECTOR", "S2": "SECTOR", "I1": "INDICATOR"}
        matched, unmatched = _parse_compound_code("S1_S2_I1", code_to_dim)
        # First match for SECTOR wins; S2 becomes unmatched
        matched_dims = [m[0] for m in matched]
        assert matched_dims.count("SECTOR") == 1
        assert "S2" in unmatched


class TestDetectIndicatorDimensionsExtra:
    """Extra branches for detect_indicator_dimensions."""

    def test_wildcard_with_indicator(self):
        """Wildcard maps to INDICATOR when available."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "INDICATOR": [{"value": "GDP", "label": "GDP"}]
        }
        meta.dataflows = {}
        meta.datastructures = {}
        result = detect_indicator_dimensions("X", ["*"], meta)
        assert result["INDICATOR"] == ["*"]

    def test_wildcard_with_no_indicator_dim_uses_first(self):
        """Wildcard falls back to first known dimension when no INDICATOR."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "SECTOR": [{"value": "S1", "label": "Sector 1"}]
        }
        meta.dataflows = {}
        meta.datastructures = {}
        result = detect_indicator_dimensions("X", ["*"], meta)
        assert "*" in result.get("SECTOR", [])

    def test_wildcard_with_empty_lookups(self):
        """Wildcard falls back to INDICATOR when no codes mapped."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {}
        meta.dataflows = {}
        meta.datastructures = {}
        result = detect_indicator_dimensions("X", ["*"], meta)
        assert result["INDICATOR"] == ["*"]

    def test_compound_skips_duplicate_dimension_match(self):
        """Compound code dedups same code per dimension list."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "SECTOR": [{"value": "S1", "label": "S1"}],
            "INDICATOR": [{"value": "I1", "label": "I1"}],
        }
        meta.dataflows = {}
        meta.datastructures = {}
        result = detect_indicator_dimensions("X", ["S1_I1", "S1_I1"], meta)
        assert result["SECTOR"] == ["S1"]
        assert result["INDICATOR"] == ["I1"]

    def test_error_with_country_match_uses_full_order(self):
        """Error message uses full dim order when COUNTRY/REF_AREA was matched."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "REF_AREA": [{"value": "USA", "label": "USA"}],
            "INDICATOR": [{"value": "GDP", "label": "GDP"}],
        }
        meta.dataflows = {"X": {"structureRef": {"id": "DSD"}}}
        meta.datastructures = {
            "DSD": {
                "dimensions": [
                    {"id": "REF_AREA"},
                    {"id": "INDICATOR"},
                ]
            }
        }
        with pytest.raises(OpenBBError) as exc_info:
            detect_indicator_dimensions("X", ["USA_BAD"], meta)
        assert "BAD" in str(exc_info.value)

    def test_error_message_with_expected_dim(self):
        """Error message lists expected dimension samples."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "SECTOR": [{"value": "S1", "label": "S1"}],
            "INDICATOR": [{"value": "GDP", "label": "GDP"}],
        }
        meta.dataflows = {"X": {"structureRef": {"id": "DSD"}}}
        meta.datastructures = {
            "DSD": {"dimensions": [{"id": "SECTOR"}, {"id": "INDICATOR"}]}
        }
        with pytest.raises(OpenBBError) as exc_info:
            detect_indicator_dimensions("X", ["S1_BAD"], meta)
        msg = str(exc_info.value)
        assert "BAD" in msg
        assert "INDICATOR" in msg or "unrecognized" in msg

    def test_unmatched_beyond_dim_order(self):
        """Unmatched segment beyond dimension order falls to 'unrecognized'."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "SECTOR": [{"value": "S1", "label": "S1"}],
        }
        meta.dataflows = {"X": {"structureRef": {"id": "DSD"}}}
        meta.datastructures = {"DSD": {"dimensions": [{"id": "SECTOR"}]}}
        with pytest.raises(OpenBBError) as exc_info:
            detect_indicator_dimensions("X", ["S1_BAD_EXTRA"], meta)
        assert "unrecognized" in str(exc_info.value) or "EXTRA" in str(exc_info.value)

    def test_unexpected_exception_falls_back(self):
        """Unexpected error inside try-block falls back to plain INDICATOR mapping."""
        meta = MagicMock()
        meta.get_dataflow_parameters.return_value = {
            "INDICATOR": [{"value": "GDP", "label": "GDP"}],
        }
        meta.dataflows = {}
        meta.datastructures = {}
        with patch(
            "openbb_imf.utils.helpers._parse_compound_code",
            side_effect=RuntimeError("kaboom"),
        ):
            result = detect_indicator_dimensions("X", ["UNKNOWN"], meta)
        assert result == {"INDICATOR": ["UNKNOWN"]}


class TestDetectTransformDimensionExtra:
    """Branches in detect_transform_dimension not covered elsewhere."""

    def test_currency_and_percent_gdp(self, monkeypatch):
        """Labels matching currency/percent_gdp map correctly."""
        from openbb_imf.utils import helpers as helpers_mod

        class FakeMeta:
            def get_dataflow_parameters(self, _dataflow):
                return {
                    "TRANSFORMATION": [
                        {"value": "PG", "label": "Percent of GDP"},
                        {"value": "DC", "label": "Domestic currency"},
                    ]
                }

        monkeypatch.setattr("openbb_imf.utils.metadata.ImfMetadata", FakeMeta)
        _td, _ud, t_lookup, _ul = helpers_mod.detect_transform_dimension("CPI")
        assert t_lookup.get("percent_gdp") == "PG"
        assert t_lookup.get("currency") == "DC"

    def test_unit_percent_label(self, monkeypatch):
        """UNIT dimension picks up percent variants."""
        from openbb_imf.utils import helpers as helpers_mod

        class FakeMeta:
            def get_dataflow_parameters(self, _dataflow):
                return {
                    "UNIT": [
                        {"value": "PCT", "label": "Percent change"},
                    ]
                }

        monkeypatch.setattr("openbb_imf.utils.metadata.ImfMetadata", FakeMeta)
        _td, ud, _tl, u_lookup = helpers_mod.detect_transform_dimension("X")
        assert ud == "UNIT"
        assert u_lookup.get("percent") == "PCT"

    def test_metadata_keyerror_swallowed(self, monkeypatch):
        """KeyError from metadata results in empty lookups."""
        from openbb_imf.utils import helpers as helpers_mod

        class FakeMeta:
            def get_dataflow_parameters(self, _dataflow):
                raise KeyError("missing")

        monkeypatch.setattr("openbb_imf.utils.metadata.ImfMetadata", FakeMeta)
        td, ud, tl, ul = helpers_mod.detect_transform_dimension("X")
        assert td is None
        assert ud is None
        assert tl == {}
        assert ul == {}


class TestParseTimePeriod:
    """Tests for parse_time_period."""

    def test_empty_string(self):
        """Empty string returns empty."""
        assert parse_time_period("") == ""

    def test_monthly(self):
        """YYYY-Mm becomes period end of month."""
        assert parse_time_period("2023-M02") == "2023-02-28"
        assert parse_time_period("2024-M02") == "2024-02-29"

    def test_monthly_malformed(self):
        """Extra split parts return input untouched."""
        assert parse_time_period("2023-M01-M02") == "2023-M01-M02"

    def test_quarterly(self):
        """YYYY-Qn becomes quarter-end date."""
        assert parse_time_period("2023-Q1") == "2023-03-31"
        assert parse_time_period("2023-Q4") == "2023-12-31"

    def test_quarterly_malformed(self):
        """Multi-Q strings return input untouched."""
        assert parse_time_period("2023-Q1-Q2") == "2023-Q1-Q2"

    def test_quarterly_unknown_quarter(self):
        """Unknown quarter falls back to December."""
        assert parse_time_period("2023-Q9") == "2023-12-31"

    def test_yearly(self):
        """Bare year becomes Dec 31."""
        assert parse_time_period("2024") == "2024-12-31"

    def test_passthrough(self):
        """Strings not matching known formats pass through."""
        assert parse_time_period("2024-01-15") == "2024-01-15"
        assert parse_time_period("abc") == "abc"

    def test_invalid_month_returns_input(self):
        """Invalid month (13) triggers ValueError and returns input."""
        assert parse_time_period("2023-M13") == "2023-M13"


class TestParseAgencyFromUrn:
    """Tests for parse_agency_from_urn."""

    def test_simple(self):
        """Parses agency from URN."""
        urn = "urn:sdmx:org.sdmx.infomodel.codelist.Code=ISORA:CL_X(1.0+.0).A"
        assert parse_agency_from_urn(urn) == "ISORA"

    def test_compound_agency(self):
        """Parses compound agency."""
        urn = "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF.STA:CL_X(1.0+.0).A"
        assert parse_agency_from_urn(urn) == "IMF.STA"

    def test_no_equals(self):
        """Returns None for URN without '='."""
        assert parse_agency_from_urn("no-equals-here:foo") is None

    def test_no_colon(self):
        """Returns None for URN without ':'."""
        assert parse_agency_from_urn("foo=bar") is None

    def test_empty(self):
        """Empty input returns None."""
        assert parse_agency_from_urn("") is None

    def test_malformed_after_equals(self):
        """Returns None when no colon after equals."""
        # has ":" elsewhere but not after "=" — split would fail
        assert parse_agency_from_urn("urn:sdmx=onlypart") is None

    def test_string_method_raises_returns_none(self):
        """Defensive except: rsplit raising returns None."""

        class WeirdStr(str):
            def rsplit(self, *_a, **_kw):
                raise RuntimeError("boom")

        # Passes early "=" and ":" checks because __contains__ inherited
        assert parse_agency_from_urn(WeirdStr("a=b:c")) is None


class TestParseIndicatorCodeFromUrn:
    """Tests for parse_indicator_code_from_urn."""

    def test_simple(self):
        """Parses indicator code from URN."""
        urn = "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF.STA:CL_X(4.0+.0).INTINC"
        assert parse_indicator_code_from_urn(urn) == "INTINC"

    def test_no_dot(self):
        """No dot returns None."""
        assert parse_indicator_code_from_urn("nodothere") is None

    def test_empty(self):
        """Empty returns None."""
        assert parse_indicator_code_from_urn("") is None


class TestParseCodelistIdFromUrn:
    """Tests for parse_codelist_id_from_urn."""

    def test_simple(self):
        """Parses codelist ID."""
        urn = "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF.STA:CL_BOP(10.0+.0).CAB"
        assert parse_codelist_id_from_urn(urn) == "CL_BOP"

    def test_no_colon(self):
        """Missing colon returns None."""
        assert parse_codelist_id_from_urn("nocolon(x)") is None

    def test_no_paren(self):
        """Missing paren returns None."""
        assert parse_codelist_id_from_urn("a:b") is None

    def test_empty(self):
        """Empty returns None."""
        assert parse_codelist_id_from_urn("") is None

    def test_string_method_raises_returns_none(self):
        """Defensive except: rsplit raising returns None."""

        class WeirdStr(str):
            def rsplit(self, *_a, **_kw):
                raise RuntimeError("boom")

        assert parse_codelist_id_from_urn(WeirdStr("a:b(c)")) is None


class TestParseSearchQuery:
    """Tests for parse_search_query."""

    def test_or_groups(self):
        """OR groups separated by pipe."""
        result = parse_search_query('inflation | "consumer price"')
        assert result == [["inflation"], ["consumer price"]]

    def test_simple_and(self):
        """Whitespace creates AND terms."""
        assert parse_search_query("gdp growth") == [["gdp", "growth"]]

    def test_plus_treated_as_space(self):
        """Plus separates AND terms."""
        assert parse_search_query("gdp+growth") == [["gdp", "growth"]]

    def test_stop_words_filtered(self):
        """Stop words like 'of' / 'the' are dropped."""
        assert parse_search_query("of the gdp") == [["gdp"]]

    def test_quoted_with_leading_term(self):
        """Bare term before quote is processed."""
        result = parse_search_query('gdp "consumer price"')
        assert result == [["gdp", "consumer price"]]

    def test_quoted_with_attached_leading_term(self):
        """Term butted up against opening quote is processed then quote starts."""
        result = parse_search_query('gdp"consumer price"')
        assert result == [["gdp", "consumer price"]]

    def test_quoted_attached_stop_word_dropped(self):
        """Stop-word attached to opening quote is dropped from output."""
        result = parse_search_query('the"price"')
        assert result == [["price"]]

    def test_quoted_with_empty_close(self):
        """An empty quoted region is skipped."""
        result = parse_search_query('"" inflation')
        assert result == [["inflation"]]

    def test_empty_or_part_skipped(self):
        """Empty OR groups are skipped."""
        assert parse_search_query("inflation |  | gdp") == [["inflation"], ["gdp"]]

    def test_only_stop_words(self):
        """A part containing only stop words produces no group."""
        assert parse_search_query("of the") == []

    def test_punctuation_strip(self):
        """Trailing punctuation is stripped."""
        result = parse_search_query("gdp.")
        assert result == [["gdp"]]


class TestBuildTimePeriodParams:
    """Tests for build_time_period_params."""

    def test_none_input(self):
        """None constraints return empties."""
        assert build_time_period_params(None) == ([], None)

    def test_empty_dict(self):
        """Empty dict returns empties."""
        opts, count = build_time_period_params({})
        assert opts == []
        assert count is None

    def test_full_payload(self):
        """Full payload yields start/end/series_count."""
        resp = {
            "full_response": {
                "data": {
                    "contentConstraints": [
                        {
                            "annotations": [
                                {"id": "time_period_start", "title": "2000-01"},
                                {"id": "time_period_end", "title": "2024-12"},
                                {"id": "series_count", "title": "42"},
                                {"id": "other", "title": "ignored"},
                            ]
                        }
                    ]
                }
            }
        }
        opts, count = build_time_period_params(resp)
        assert {"label": "Start Date: 2000-01", "value": "2000-01"} in opts
        assert {"label": "End Date: 2024-12", "value": "2024-12"} in opts
        assert count == "42"

    def test_no_content_constraints(self):
        """Empty contentConstraints returns empty options."""
        resp = {"full_response": {"data": {"contentConstraints": []}}}
        opts, count = build_time_period_params(resp)
        assert opts == []
        assert count is None


class TestParseCodelistUrn:
    """Tests for parse_codelist_urn."""

    def test_simple(self):
        """Parses codelist URN."""
        urn = (
            "urn:sdmx:com.epam.quanthub.sdmxplus.infomodel.Glossary="
            "IMF.STA:CL_FSIBSIS(4.0+.0)"
        )
        assert parse_codelist_urn(urn) == "CL_FSIBSIS"

    def test_empty(self):
        """Empty returns None."""
        assert parse_codelist_urn("") is None

    def test_no_equals(self):
        """No '=' returns None."""
        assert parse_codelist_urn("noequals") is None

    def test_string_method_raises_returns_none(self):
        """Defensive except: rsplit raising returns None."""

        class WeirdStr(str):
            def rsplit(self, *_a, **_kw):
                raise RuntimeError("boom")

        assert parse_codelist_urn(WeirdStr("a=b")) is None


class TestExtractAllCodelistsFromHierarchy:
    """Tests for extract_all_codelists_from_hierarchy."""

    def test_empty(self):
        """Hierarchy with no codes returns empty set."""
        assert extract_all_codelists_from_hierarchy({}) == set()

    def test_recursive(self):
        """Nested hierarchies are scanned."""
        urn = "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF.STA:CL_TOP(1.0+.0).A"
        sub_urn = "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF.STA:CL_SUB(1.0+.0).B"
        hier = {
            "hierarchicalCodes": [
                {
                    "code": urn,
                    "hierarchicalCodes": [{"code": sub_urn}],
                }
            ]
        }
        result = extract_all_codelists_from_hierarchy(hier)
        assert "CL_TOP" in result
        assert "CL_SUB" in result

    def test_empty_code(self):
        """Entry with empty code is skipped."""
        hier = {"hierarchicalCodes": [{"code": ""}]}
        assert extract_all_codelists_from_hierarchy(hier) == set()

    def test_non_list_hcodes(self):
        """Non-list hierarchicalCodes returns empty set."""
        assert extract_all_codelists_from_hierarchy({"hierarchicalCodes": "x"}) == set()


class TestBuildHierarchyToCodelistMap:
    """Tests for build_hierarchy_to_codelist_map."""

    def test_via_annotation(self):
        """Mapping is derived from owningCodelistUrn annotation."""
        urn = (
            "urn:sdmx:com.epam.quanthub.sdmxplus.infomodel.Glossary="
            "IMF.STA:CL_X(1.0+.0)"
        )
        hierarchies = {
            "H1": {"annotations": [{"id": "owningCodelistUrn", "text": urn}]}
        }
        mapping = build_hierarchy_to_codelist_map(hierarchies)
        assert mapping == {"H1": "CL_X"}

    def test_fallback_to_first_code(self):
        """Falls back to first hierarchicalCode when no annotation."""
        code_urn = "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF:CL_FIRST(1.0+.0).A"
        hierarchies = {"H1": {"hierarchicalCodes": [{"code": code_urn}]}}
        mapping = build_hierarchy_to_codelist_map(hierarchies)
        assert mapping == {"H1": "CL_FIRST"}

    def test_no_match(self):
        """Empty hierarchy yields nothing."""
        assert build_hierarchy_to_codelist_map({"H1": {}}) == {}

    def test_annotation_without_urn(self):
        """Annotation with empty URN falls back to hierarchicalCodes."""
        hierarchies = {
            "H1": {
                "annotations": [{"id": "owningCodelistUrn", "text": ""}],
                "hierarchicalCodes": [
                    {
                        "code": (
                            "urn:sdmx:org.sdmx.infomodel.codelist.Code="
                            "IMF:CL_FALLBACK(1.0+.0).A"
                        )
                    }
                ],
            }
        }
        mapping = build_hierarchy_to_codelist_map(hierarchies)
        assert mapping == {"H1": "CL_FALLBACK"}


class TestBuildCodelistToHierarchiesMap:
    """Tests for build_codelist_to_hierarchies_map."""

    def test_basic(self):
        """Reverse mapping covers all codelists."""
        urn1 = "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF:CL_A(1.0+.0).X"
        urn2 = "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF:CL_B(1.0+.0).Y"
        hierarchies = {
            "H1": {"hierarchicalCodes": [{"code": urn1}, {"code": urn2}]},
            "H2": {"hierarchicalCodes": [{"code": urn1}]},
        }
        mapping = build_codelist_to_hierarchies_map(hierarchies)
        assert set(mapping["CL_A"]) == {"H1", "H2"}
        assert mapping["CL_B"] == ["H1"]

    def test_dedupes_hierarchy(self):
        """Same hierarchy ID is not duplicated."""
        urn = "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF:CL_A(1.0+.0).X"
        hierarchies = {"H1": {"hierarchicalCodes": [{"code": urn}, {"code": urn}]}}
        mapping = build_codelist_to_hierarchies_map(hierarchies)
        assert mapping["CL_A"] == ["H1"]


class TestTranslateErrorMessage:
    """Tests for translate_error_message."""

    def test_dim_translation(self):
        """COUNTRY/INDICATOR mapped to user-friendly names."""
        msg = "Invalid value for 'COUNTRY'"
        assert "'country'" in translate_error_message(msg)

    def test_frequency_value_translation(self):
        """Frequency code 'A' maps to 'annual'."""
        msg = "Invalid value 'A'"
        out = translate_error_message(msg)
        assert "'annual'" in out

    def test_dimension_phrase_replacement(self):
        """`'X'` quoted dimensions are translated."""
        msg = "Invalid dimension 'BOP_ACCOUNTING_ENTRY'"
        out = translate_error_message(msg)
        assert "'accounting_entry'" in out

    def test_codes_phrase_replacement(self):
        """`X codes` becomes `<param> codes`."""
        msg = "Available SECTOR codes: x"
        out = translate_error_message(msg)
        assert "sector codes" in out

    def test_double_quote_variant(self):
        """Double-quoted dimension name is also translated."""
        msg = 'Invalid value for "COUNTRY"'
        assert '"country"' in translate_error_message(msg)
