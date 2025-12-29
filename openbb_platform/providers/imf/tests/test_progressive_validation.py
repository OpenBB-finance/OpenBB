"""Tests for progressive validation logic in ImfParamsBuilder and ImfQueryBuilder."""

# ruff: noqa: I001
# pylint: disable=W0621,W0613,W0212,R0903,C0302,C0415

from unittest.mock import MagicMock, patch

import pytest


class TestImfParamsBuilderInit:
    """Tests for ImfParamsBuilder initialization."""

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_valid_dataflow_initializes(self, mock_metadata_cls):
        """Valid dataflow should initialize successfully."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {
                "structureRef": {"id": "DSD_BOP"},
                "agencyID": "IMF",
            }
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [
                    {"id": "REF_AREA", "position": 1},
                    {"id": "INDICATOR", "position": 2},
                    {"id": "FREQ", "position": 3},
                ],
            }
        }
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfParamsBuilder("BOP")
        assert builder.dataflow_id == "BOP"
        assert builder._dimensions == ["REF_AREA", "INDICATOR", "FREQ"]
        assert builder.current_dimension == "REF_AREA"

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_invalid_dataflow_raises_keyerror(self, mock_metadata_cls):
        """Invalid dataflow should raise KeyError with helpful message."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {"BOP": {}, "IFS": {}}
        mock_metadata_cls.return_value = mock_metadata

        with pytest.raises(KeyError) as exc_info:
            ImfParamsBuilder("INVALID")

        assert "INVALID" in str(exc_info.value)
        assert "Available dataflows" in str(exc_info.value)

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_dimensions_sorted_by_position(self, mock_metadata_cls):
        """Dimensions should be sorted by position."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "TEST": {
                "structureRef": {"id": "DSD_TEST"},
                "agencyID": "IMF",
            }
        }
        # Dimensions in reverse order
        mock_metadata.datastructures = {
            "DSD_TEST": {
                "id": "DSD_TEST",
                "dimensions": [
                    {"id": "THIRD", "position": 3},
                    {"id": "FIRST", "position": 1},
                    {"id": "SECOND", "position": 2},
                ],
            }
        }
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfParamsBuilder("TEST")
        assert builder._dimensions == ["FIRST", "SECOND", "THIRD"]

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_time_period_excluded_from_dimensions(self, mock_metadata_cls):
        """TIME_PERIOD should be excluded from dimensions list."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "TEST": {
                "structureRef": {"id": "DSD_TEST"},
            }
        }
        mock_metadata.datastructures = {
            "DSD_TEST": {
                "dimensions": [
                    {"id": "REF_AREA", "position": 1},
                    {"id": "TIME_PERIOD", "position": 2},
                    {"id": "INDICATOR", "position": 3},
                ],
            }
        }
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfParamsBuilder("TEST")
        assert "TIME_PERIOD" not in builder._dimensions
        assert builder._dimensions == ["REF_AREA", "INDICATOR"]


class TestDimensionSelection:
    """Tests for set_dimension and selection tracking."""

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_set_dimension_updates_selection(self, mock_metadata_cls):
        """Setting a dimension should update selections."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {"BOP": {"structureRef": {"id": "DSD_BOP"}}}
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "dimensions": [
                    {"id": "REF_AREA", "position": 1},
                    {"id": "INDICATOR", "position": 2},
                ],
            }
        }
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfParamsBuilder("BOP")
        result = builder.set_dimension(("REF_AREA", "US"))

        assert result["REF_AREA"] == "US"
        assert result["INDICATOR"] is None

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_set_dimension_clears_downstream(self, mock_metadata_cls):
        """Setting an upstream dimension should clear downstream selections."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {"BOP": {"structureRef": {"id": "DSD_BOP"}}}
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "dimensions": [
                    {"id": "REF_AREA", "position": 1},
                    {"id": "INDICATOR", "position": 2},
                    {"id": "FREQ", "position": 3},
                ],
            }
        }
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfParamsBuilder("BOP")
        builder._selections = {"REF_AREA": "US", "INDICATOR": "IND1", "FREQ": "A"}

        # Re-set REF_AREA - should clear INDICATOR and FREQ
        result = builder.set_dimension(("REF_AREA", "GB"))

        assert result["REF_AREA"] == "GB"
        assert result["INDICATOR"] is None
        assert result["FREQ"] is None

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_set_invalid_dimension_raises_keyerror(self, mock_metadata_cls):
        """Setting an invalid dimension should raise KeyError."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {"BOP": {"structureRef": {"id": "DSD_BOP"}}}
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfParamsBuilder("BOP")

        with pytest.raises(KeyError) as exc_info:
            builder.set_dimension(("INVALID_DIM", "VALUE"))

        assert "INVALID_DIM" in str(exc_info.value)
        assert "Valid dimensions" in str(exc_info.value)

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_get_next_dimension_to_select(self, mock_metadata_cls):
        """get_next_dimension_to_select should return first unselected dimension."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {"BOP": {"structureRef": {"id": "DSD_BOP"}}}
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "dimensions": [
                    {"id": "DIM1", "position": 1},
                    {"id": "DIM2", "position": 2},
                    {"id": "DIM3", "position": 3},
                ],
            }
        }
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfParamsBuilder("BOP")

        assert builder.get_next_dimension_to_select() == "DIM1"

        builder.set_dimension(("DIM1", "VAL1"))
        assert builder.get_next_dimension_to_select() == "DIM2"

        builder.set_dimension(("DIM2", "VAL2"))
        assert builder.get_next_dimension_to_select() == "DIM3"

        builder.set_dimension(("DIM3", "VAL3"))
        assert builder.get_next_dimension_to_select() is None


# =============================================================================
# Get Options Tests
# =============================================================================


class TestGetOptionsForDimension:
    """Tests for get_options_for_dimension constraint checking."""

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_get_options_returns_available_values(self, mock_metadata_cls):
        """get_options_for_dimension should return available values from constraints."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [{"id": "REF_AREA", "values": ["US", "GB", "DE"]}]
        }
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfParamsBuilder("BOP")
        options = builder.get_options_for_dimension("REF_AREA")

        assert len(options) == 3
        assert {"label": "US", "value": "US"} in options
        assert {"label": "GB", "value": "GB"} in options
        assert {"label": "DE", "value": "DE"} in options

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_get_options_uses_codelist_labels(self, mock_metadata_cls):
        """get_options_for_dimension should use codelist for human-readable labels."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [{"id": "REF_AREA", "values": ["US", "GB"]}]
        }
        mock_metadata._resolve_codelist_id.return_value = "CL_AREA"
        mock_metadata._get_codelist_map.return_value = {
            "US": "United States",
            "GB": "United Kingdom",
        }
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfParamsBuilder("BOP")
        options = builder.get_options_for_dimension("REF_AREA")

        assert {"label": "United States", "value": "US"} in options
        assert {"label": "United Kingdom", "value": "GB"} in options

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_get_options_for_invalid_dimension_raises(self, mock_metadata_cls):
        """get_options_for_dimension with invalid dimension should raise ValueError."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {"BOP": {"structureRef": {"id": "DSD_BOP"}}}
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfParamsBuilder("BOP")

        with pytest.raises(ValueError) as exc_info:
            builder.get_options_for_dimension("INVALID")

        assert "INVALID" in str(exc_info.value)

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_get_options_uses_wildcards_for_unselected(self, mock_metadata_cls):
        """Unselected dimensions should use '*' wildcard in key."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [
                    {"id": "DIM1", "position": 1},
                    {"id": "DIM2", "position": 2},
                    {"id": "DIM3", "position": 3},
                ],
            }
        }
        mock_metadata.get_available_constraints.return_value = {"key_values": []}
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfParamsBuilder("BOP")
        builder.set_dimension(("DIM1", "VAL1"))
        builder.get_options_for_dimension("DIM2")

        # Check the key passed to get_available_constraints
        call_args = mock_metadata.get_available_constraints.call_args
        assert call_args.kwargs["key"] == "VAL1.*.*"


# =============================================================================
# Query Builder Validation Tests
# =============================================================================


class TestValidateDimensionConstraints:
    """Tests for ImfQueryBuilder.validate_dimension_constraints."""

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_valid_values_pass_validation(self, mock_metadata_cls):
        """Valid dimension values should pass validation without error."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [
                    {"id": "REF_AREA", "position": 1},
                    {"id": "INDICATOR", "position": 2},
                ],
            }
        }
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [
                {"id": "REF_AREA", "values": ["US", "GB"]},
                {"id": "INDICATOR", "values": ["IND1", "IND2"]},
            ]
        }
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()
        # Should not raise
        builder.validate_dimension_constraints(
            dataflow="BOP", REF_AREA="US", INDICATOR="IND1"
        )

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_invalid_value_raises_valueerror(self, mock_metadata_cls):
        """Invalid dimension value should raise ValueError with details."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [
                    {"id": "REF_AREA", "position": 1},
                ],
            }
        }
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [
                {"id": "REF_AREA", "values": ["US", "GB"]},
            ]
        }
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()

        with pytest.raises(ValueError) as exc_info:
            builder.validate_dimension_constraints(
                dataflow="BOP", REF_AREA="INVALID_COUNTRY"
            )

        error_msg = str(exc_info.value)
        assert "INVALID_COUNTRY" in error_msg
        assert "REF_AREA" in error_msg
        assert "available values" in error_msg.lower()

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_wildcard_always_valid(self, mock_metadata_cls):
        """Wildcard '*' should always be accepted."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata.get_available_constraints.return_value = {"key_values": []}
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()
        # Should not raise
        builder.validate_dimension_constraints(dataflow="BOP", REF_AREA="*")

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_comma_separated_values_validated(self, mock_metadata_cls):
        """Comma-separated values should all be validated."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [
                {"id": "REF_AREA", "values": ["US", "GB", "DE"]},
            ]
        }
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()
        # Valid comma-separated should pass
        builder.validate_dimension_constraints(dataflow="BOP", REF_AREA="US,GB")

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_comma_separated_with_invalid_raises(self, mock_metadata_cls):
        """Comma-separated with one invalid value should raise."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [
                {"id": "REF_AREA", "values": ["US", "GB"]},
            ]
        }
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()

        with pytest.raises(ValueError) as exc_info:
            builder.validate_dimension_constraints(
                dataflow="BOP", REF_AREA="US,INVALID"
            )

        assert "INVALID" in str(exc_info.value)

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_plus_separated_values_validated(self, mock_metadata_cls):
        """Plus-separated values should all be validated."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [
                {"id": "REF_AREA", "values": ["US", "GB", "DE"]},
            ]
        }
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()
        # Valid plus-separated should pass
        builder.validate_dimension_constraints(dataflow="BOP", REF_AREA="US+GB+DE")

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_empty_value_skipped(self, mock_metadata_cls):
        """Empty/None values should be skipped in validation."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()
        # Should not raise - empty values skipped
        builder.validate_dimension_constraints(dataflow="BOP", REF_AREA="")
        builder.validate_dimension_constraints(dataflow="BOP", REF_AREA=None)


# =============================================================================
# Time Period Validation Tests
# =============================================================================


class TestTimePeriodValidation:
    """Tests for time period range validation."""

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_start_date_after_available_range_raises(self, mock_metadata_cls):
        """Start date after available data range should raise ValueError."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [{"id": "REF_AREA", "values": ["US"]}],
            "full_response": {
                "data": {
                    "dataConstraints": [
                        {
                            "annotations": [
                                {"id": "time_period_start", "title": "2000-01"},
                                {"id": "time_period_end", "title": "2023-12"},
                            ]
                        }
                    ]
                }
            },
        }
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()

        with pytest.raises(ValueError) as exc_info:
            builder.validate_dimension_constraints(
                dataflow="BOP", REF_AREA="US", start_date="2025-01"
            )

        error_msg = str(exc_info.value)
        assert "2025-01" in error_msg
        assert "after" in error_msg.lower()
        assert "2023-12" in error_msg

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_end_date_before_available_range_raises(self, mock_metadata_cls):
        """End date before available data range should raise ValueError."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [{"id": "REF_AREA", "values": ["US"]}],
            "full_response": {
                "data": {
                    "dataConstraints": [
                        {
                            "annotations": [
                                {"id": "time_period_start", "title": "2000-01"},
                                {"id": "time_period_end", "title": "2023-12"},
                            ]
                        }
                    ]
                }
            },
        }
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()

        with pytest.raises(ValueError) as exc_info:
            builder.validate_dimension_constraints(
                dataflow="BOP", REF_AREA="US", end_date="1990-01"
            )

        error_msg = str(exc_info.value)
        assert "1990-01" in error_msg
        assert "before" in error_msg.lower()
        assert "2000-01" in error_msg

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_valid_date_range_passes(self, mock_metadata_cls):
        """Valid date range within available data should pass."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [{"id": "REF_AREA", "values": ["US"]}],
            "full_response": {
                "data": {
                    "dataConstraints": [
                        {
                            "annotations": [
                                {"id": "time_period_start", "title": "2000-01"},
                                {"id": "time_period_end", "title": "2023-12"},
                            ]
                        }
                    ]
                }
            },
        }
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()
        # Should not raise
        builder.validate_dimension_constraints(
            dataflow="BOP", REF_AREA="US", start_date="2010-01", end_date="2020-12"
        )


# =============================================================================
# Progressive Constraint Propagation Tests
# =============================================================================


class TestProgressiveConstraintPropagation:
    """Tests for how prior selections affect subsequent option availability."""

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_prior_selection_constrains_options(self, mock_metadata_cls):
        """Prior selections should constrain available options for subsequent dimensions."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [
                    {"id": "REF_AREA", "position": 1},
                    {"id": "INDICATOR", "position": 2},
                ],
            }
        }

        # First call returns all countries
        # Second call (after country selected) returns fewer indicators
        call_count = [0]

        def mock_constraints(dataflow_id, key, component_id):
            call_count[0] += 1
            if component_id == "INDICATOR" and "US" in key:
                # US has fewer indicators
                return {"key_values": [{"id": "INDICATOR", "values": ["IND1", "IND2"]}]}
            elif component_id == "INDICATOR" and "GB" in key:
                # GB has more indicators
                return {
                    "key_values": [
                        {"id": "INDICATOR", "values": ["IND1", "IND2", "IND3", "IND4"]}
                    ]
                }
            return {"key_values": []}

        mock_metadata.get_available_constraints.side_effect = mock_constraints
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfParamsBuilder("BOP")

        # Select US
        builder.set_dimension(("REF_AREA", "US"))
        us_options = builder.get_options_for_dimension("INDICATOR")
        assert len(us_options) == 2

        # Reset and select GB
        builder._selections = {"REF_AREA": None, "INDICATOR": None}
        builder.set_dimension(("REF_AREA", "GB"))
        gb_options = builder.get_options_for_dimension("INDICATOR")
        assert len(gb_options) == 4

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_validate_considers_prior_selections_in_error(self, mock_metadata_cls):
        """Error message should include prior selections for context."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [
                    {"id": "REF_AREA", "position": 1},
                    {"id": "INDICATOR", "position": 2},
                ],
            }
        }

        def mock_constraints(dataflow_id, key, component_id):
            if component_id == "REF_AREA":
                return {"key_values": [{"id": "REF_AREA", "values": ["US", "GB"]}]}
            elif component_id == "INDICATOR":
                # Only IND1 available for US
                return {"key_values": [{"id": "INDICATOR", "values": ["IND1"]}]}
            return {"key_values": []}

        mock_metadata.get_available_constraints.side_effect = mock_constraints
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()

        with pytest.raises(ValueError) as exc_info:
            builder.validate_dimension_constraints(
                dataflow="BOP", REF_AREA="US", INDICATOR="IND_NOT_AVAILABLE_FOR_US"
            )

        error_msg = str(exc_info.value)
        # Error should mention the invalid value
        assert "IND_NOT_AVAILABLE_FOR_US" in error_msg
        # Error should show prior selections
        assert "REF_AREA" in error_msg


class TestValidationEdgeCases:
    """Edge cases in progressive validation."""

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_no_key_values_in_constraints_response(self, mock_metadata_cls):
        """Empty key_values should result in no available values."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata.get_available_constraints.return_value = {"key_values": []}
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfParamsBuilder("BOP")
        options = builder.get_options_for_dimension("REF_AREA")

        assert options == []  # pylint: disable=C1803

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_missing_dimension_in_constraints_response(self, mock_metadata_cls):
        """Missing dimension in key_values should return empty options."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [
                    {"id": "REF_AREA", "position": 1},
                    {"id": "INDICATOR", "position": 2},
                ],
            }
        }
        # Response only has REF_AREA, not INDICATOR
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [{"id": "REF_AREA", "values": ["US"]}]
        }
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfParamsBuilder("BOP")
        options = builder.get_options_for_dimension("INDICATOR")

        assert options == []  # pylint: disable=C1803

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_list_input_validated(self, mock_metadata_cls):
        """List input for dimension value should be validated."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [{"id": "REF_AREA", "values": ["US", "GB"]}]
        }
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()
        # List input should work
        builder.validate_dimension_constraints(dataflow="BOP", REF_AREA=["US", "GB"])

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_whitespace_in_comma_separated_trimmed(self, mock_metadata_cls):
        """Whitespace around comma-separated values should be trimmed."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [{"id": "REF_AREA", "values": ["US", "GB"]}]
        }
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()
        # Whitespace should be trimmed
        builder.validate_dimension_constraints(dataflow="BOP", REF_AREA="  US  ,  GB  ")

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_metadata_keyerror_warns_instead_of_raising(self, mock_metadata_cls):
        """KeyError from metadata should warn, not raise."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder
        import warnings

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {}  # No dataflows
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()

        # Should warn, not raise
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            builder.validate_dimension_constraints(
                dataflow="NONEXISTENT", REF_AREA="US"
            )

            # Check that a warning was issued
            assert len(w) == 1
            assert "could not validate" in str(w[0].message).lower()

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_no_time_constraints_in_response(self, mock_metadata_cls):
        """Missing time period constraints should not cause errors."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [{"id": "REF_AREA", "values": ["US"]}],
            # No time_period key
        }
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()
        builder.validate_dimension_constraints(dataflow="BOP", REF_AREA="US")

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_irfcl_compatibility_filtering(self, mock_metadata_cls):
        """Test that IRFCL hierarchies are filtered for compatibility."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "IRFCL": {"structureRef": {"id": "DSD_IRFCL"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_IRFCL": {
                "id": "DSD_IRFCL",
                "dimensions": [{"id": "INDICATOR", "position": 1}],
            }
        }
        # Mock constraints returning a specific indicator
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [{"id": "INDICATOR", "values": ["RAF_USD"]}]
        }
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()

        # If we validate constraints for IRFCL, it should pass if the indicator is compatible
        builder.validate_dimension_constraints(dataflow="IRFCL", INDICATOR="RAF_USD")

        # If we try an incompatible one (not in constraints)
        with pytest.raises(ValueError):
            builder.validate_dimension_constraints(
                dataflow="IRFCL", INDICATOR="INCOMPATIBLE"
            )

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_long_multi_code_input_wildcard(self, mock_metadata_cls):
        """Test that long multi-code inputs are treated as wildcards during validation."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        # Constraints return everything (wildcard)
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [{"id": "REF_AREA", "values": ["US", "GB", "FR"]}]
        }
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()

        # Create a long list of codes
        long_list = ["US"] * 50

        # Validation should pass because it should treat it as wildcard or check against constraints
        builder.validate_dimension_constraints(dataflow="BOP", REF_AREA=long_list)

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [{"id": "REF_AREA", "position": 1}],
            }
        }
        # No time period annotations
        mock_metadata.get_available_constraints.return_value = {
            "key_values": [{"id": "REF_AREA", "values": ["US"]}],
            "full_response": {"data": {}},
        }
        mock_metadata._resolve_codelist_id.return_value = None
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfQueryBuilder()
        # Should not raise even with dates provided
        builder.validate_dimension_constraints(
            dataflow="BOP", REF_AREA="US", start_date="2020-01", end_date="2023-12"
        )


# =============================================================================
# Build URL Tests
# =============================================================================


class TestBuildUrl:
    """Tests for ImfParamsBuilder.build_url."""

    @patch("openbb_imf.utils.query_builder.ImfMetadata")
    def test_build_url_uses_selections(self, mock_metadata_cls):
        """build_url should use current selections."""
        from openbb_imf.utils.progressive_helper import ImfParamsBuilder

        mock_metadata = MagicMock()
        mock_metadata.dataflows = {
            "BOP": {"structureRef": {"id": "DSD_BOP"}, "agencyID": "IMF"}
        }
        mock_metadata.datastructures = {
            "DSD_BOP": {
                "id": "DSD_BOP",
                "dimensions": [
                    {"id": "REF_AREA", "position": 1},
                    {"id": "INDICATOR", "position": 2},
                ],
            }
        }
        mock_metadata_cls.return_value = mock_metadata

        builder = ImfParamsBuilder("BOP")
        builder.set_dimension(("REF_AREA", "US"))
        builder.set_dimension(("INDICATOR", "IND1"))

        # Just verify the internal builder.build_url is called with correct args
        with patch.object(
            builder._builder, "build_url", return_value="http://test.url"
        ) as mock_build:
            result = builder.build_url(start_date="2020-01", end_date="2023-12")

            mock_build.assert_called_once_with(
                dataflow="BOP",
                start_date="2020-01",
                end_date="2023-12",
                REF_AREA="US",
                INDICATOR="IND1",
            )
            assert result == "http://test.url"
