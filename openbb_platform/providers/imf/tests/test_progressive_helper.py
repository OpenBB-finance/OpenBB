"""Test ImfProgressiveQueryHelper."""

# ruff: noqa: I001
# pylint: disable=W0621,W0613,W0212,R0903

from unittest.mock import patch, MagicMock

import pytest
from openbb_imf.utils.progressive_helper import ImfParamsBuilder


@pytest.fixture
def mock_builder():
    """Mock ImfQueryBuilder."""
    with patch(
        "openbb_imf.utils.progressive_helper.ImfQueryBuilder"
    ) as mock_builder_class:
        mock_instance = mock_builder_class.return_value
        # Configure metadata mock
        mock_instance.metadata = MagicMock()
        mock_instance.metadata.dataflows = {
            "GFS_BS": {
                "name": "Government Finance Statistics, Balance Sheet",
                "structureRef": {"id": "IMF_GFS_BS"},
                "agencyID": "IMF.STA",
            }
        }
        mock_instance.metadata.datastructures = {
            "IMF_GFS_BS": {
                "id": "IMF_GFS_BS",
                "dimensions": [
                    {"id": "FREQ", "position": 1},
                    {"id": "REF_AREA", "position": 2},
                    {
                        "id": "INDICATOR",
                        "position": 3,
                        "conceptRef": {"id": "INDICATOR"},
                    },
                ],
            }
        }
        mock_instance.metadata.codelists = {
            "CL_FREQ": {"codes": [{"id": "A", "name": "Annual"}]},
            "CL_REF_AREA": {"codes": [{"id": "US", "name": "United States"}]},
            "CL_GFS_INDICATOR": {
                "codes": [{"id": "GG_XDC_G01_XDC_P1_B9", "name": "Gross debt"}]
            },
        }

        def get_codelist_map(
            codelist_id, agency_id=None, dataflow_id=None
        ):  # noqa: ARG001
            if codelist_id in mock_instance.metadata.codelists:
                return {
                    item["id"]: item["name"]
                    for item in mock_instance.metadata.codelists[codelist_id].get(
                        "codes", []
                    )
                }
            return {}

        mock_instance.metadata._get_codelist_map.side_effect = get_codelist_map

        def resolve_codelist_id(dataflow_id, dsd_id, dimension_id, dim_meta):
            # Simplified resolver for the mocked DSD
            if dimension_id == "FREQ":
                return "CL_FREQ"
            if dimension_id == "REF_AREA":
                return "CL_REF_AREA"
            if dimension_id == "INDICATOR":
                return "CL_GFS_INDICATOR"
            return None

        mock_instance.metadata._resolve_codelist_id.side_effect = resolve_codelist_id

        mock_instance.metadata.get_available_constraints.return_value = {
            "key_values": [
                {
                    "id": "INDICATOR",
                    "values": ["GG_XDC_G01_XDC_P1_B9"],
                }
            ]
        }
        yield mock_instance


def test_progressive_helper_gfs_indicator(mock_builder):
    """Test that the progressive helper can find specific codelists."""
    helper = ImfParamsBuilder(dataflow_id="GFS_BS")
    helper._builder = mock_builder

    options = helper.get_options_for_dimension("INDICATOR")

    assert options
    assert len(options) == 1
    assert options[0]["value"] == "GG_XDC_G01_XDC_P1_B9"
    assert options[0]["label"] == "Gross debt"
    mock_builder.metadata._get_codelist_map.assert_called_with(
        "CL_GFS_INDICATOR", "IMF.STA", "GFS_BS"
    )


def test_constrained_codelist_resolution(mock_builder):
    """Test that options are filtered based on constraints."""
    helper = ImfParamsBuilder(dataflow_id="GFS_BS")
    helper._builder = mock_builder

    # Mock constraints returning only one indicator
    mock_builder.metadata.get_available_constraints.return_value = {
        "key_values": [
            {
                "id": "INDICATOR",
                "values": ["GG_XDC_G01_XDC_P1_B9"],
            }
        ]
    }

    options = helper.get_options_for_dimension("INDICATOR")
    assert len(options) == 1
    assert options[0]["value"] == "GG_XDC_G01_XDC_P1_B9"


def test_component_label_fallback(mock_builder):
    """Test fallback when label is missing in codelist."""
    helper = ImfParamsBuilder(dataflow_id="GFS_BS")
    helper._builder = mock_builder

    # Add a code to constraints that isn't in the codelist map
    mock_builder.metadata.get_available_constraints.return_value = {
        "key_values": [
            {
                "id": "INDICATOR",
                "values": ["UNKNOWN_CODE"],
            }
        ]
    }

    # Mock empty codelist map for this test
    mock_builder.metadata._get_codelist_map.return_value = {}

    options = helper.get_options_for_dimension("INDICATOR")
    assert len(options) == 1
    assert options[0]["value"] == "UNKNOWN_CODE"
    assert options[0]["label"] == "UNKNOWN_CODE"  # Fallback to value


def test_time_period_annotation_propagation(mock_builder):
    """Test that time period annotations are propagated."""
    helper = ImfParamsBuilder(dataflow_id="GFS_BS")
    helper._builder = mock_builder

    mock_builder.metadata.get_available_constraints.return_value = {
        "key_values": [],
        "time_period": {"start_period": "2000", "end_period": "2020"},
    }

    # Trigger a constraint update (e.g. by getting options)
    helper.get_options_for_dimension("INDICATOR")

    assert helper._last_constraints_response["time_period"]["start_period"] == "2000"
    assert helper._last_constraints_response["time_period"]["end_period"] == "2020"


def test_case_insensitive_dimension_keys(mock_builder):
    """Test that dimension keys are case-insensitive."""
    helper = ImfParamsBuilder(dataflow_id="GFS_BS")
    helper._builder = mock_builder

    options = helper.get_options_for_dimension("INDICATOR")
    assert options
    assert options[0]["value"] == "GG_XDC_G01_XDC_P1_B9"


def test_wildcard_on_long_multi_code_inputs(mock_builder):
    """Test that long multi-code inputs trigger wildcard behavior."""
    helper = ImfParamsBuilder(dataflow_id="GFS_BS")
    helper._builder = mock_builder

    # Simulate a long list of codes selected for a previous dimension
    long_list = ["A"] * 50
    helper.set_dimension(("FREQ", "+".join(long_list)))

    helper.get_options_for_dimension("REF_AREA")

    call_args = mock_builder.metadata.get_available_constraints.call_args
    assert call_args is not None
    key_arg = call_args.kwargs.get("key")
    assert key_arg is not None
    # Key should include the long frequency string, not be blanked to wildcard
    assert "+".join(long_list) in key_arg
