"""Test coverage for the router module."""


from unittest.mock import patch

from openbb_core.api.router.coverage import get_command_coverage, get_provider_coverage


@patch("openbb_core.api.router.coverage.CommandMap")
def test_get_provider_coverage(mock_command_map):
    """Test get provider coverage."""
    mock_command_map.return_value.provider_coverage = {
        "provider1": ["coverage1", "coverage2"]
    }

    response = get_provider_coverage(mock_command_map)

    assert response


@patch("openbb_core.api.router.coverage.CommandMap")
def test_get_command_coverage(mock_command_map):
    """Test get command coverage."""
    mock_command_map.return_value.command_coverage = {
        "command1": ["coverage1", "coverage2"]
    }

    response = get_command_coverage(mock_command_map)
    assert response


@patch("openbb_core.api.router.coverage.CommandMap")
@patch("openbb_core.api.router.coverage.ProviderInterface")
def test_get_command_model(mock_provider_interface, mock_command_map):
    """Test get command model."""
    mock_command_map.return_value.commands_model = {"command1": "model1"}
    mock_provider_interface.return_value.map = {"model1": "provider1"}

    response = get_command_coverage(mock_command_map)
    assert response
