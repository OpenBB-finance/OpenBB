"""Tests for IMF helper utilities."""

# ruff: noqa: I001
# pylint: disable=W0621,W0613,W0612,W0212,R0903,C0302,C0415

from unittest.mock import MagicMock, patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_imf.utils.helpers import (
    detect_indicator_dimensions,
    detect_transform_dimension,
    normalize_country_label,
    resolve_country_code,
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

        # Direct codes should be accessible (case-insensitive)
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
        # Mock get_dataflow_parameters to return dimension -> codes mapping
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

        # "UNKNOWN" is not in any dimension - raises OpenBBError
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

        # Compound code: S1_I1 (underscore separator)
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

        # Compound code with missing dimension: S1 (implies wildcard for INDICATOR)
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

        # When metadata fails, the function should raise an error for invalid codes
        with pytest.raises(OpenBBError):
            detect_indicator_dimensions("TEST", ["GDP", "CPI"], mock_metadata)
