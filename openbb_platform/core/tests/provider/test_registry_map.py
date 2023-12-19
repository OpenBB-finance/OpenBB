"""Test the registry map."""
# pylint: disable=W0621

import pytest
from openbb_core.provider.registry_map import RegistryMap


@pytest.fixture
def load_registry_map():
    """Mock the registry map."""
    registry_map = RegistryMap()
    return registry_map


def test_get_credentials(load_registry_map):
    """Test if the _get_credentials method behaves as expected."""
    required_creds = load_registry_map.credentials

    assert "fmp_api_key" in required_creds


def test_get_available_providers(load_registry_map):
    """Test if the _get_available_providers method behaves as expected."""
    available_providers = load_registry_map.available_providers

    assert "fmp" in available_providers
    assert len(available_providers) > 0


def test_map_and_models(load_registry_map):
    """Test if the _get_map method behaves as expected."""
    map_, return_map = load_registry_map.map, load_registry_map.return_map
    models = load_registry_map.models

    assert "EquityHistorical" in map_
    assert "EquityHistorical" in return_map
    assert "EquityHistorical" in models
