"""Test the registry map."""

# pylint: disable=W0621

import pytest
from openbb_core.provider.registry_map import RegistryMap


@pytest.fixture
def load_registry_map():
    """Mock the registry map."""
    return RegistryMap()


def test_get_credentials(load_registry_map):
    """Test if the _get_credentials method behaves as expected."""
    required_creds = load_registry_map.credentials

    assert "fmp" in required_creds
    assert required_creds["fmp"] == ["fmp_api_key"]


def test_get_available_providers(load_registry_map):
    """Test if the _get_available_providers method behaves as expected."""
    available_providers = load_registry_map.available_providers

    assert "fmp" in available_providers
    assert len(available_providers) > 0


def test_map_and_models(load_registry_map):
    """Test if the _get_map method behaves as expected."""
    standard_extra, original_models = (
        load_registry_map.standard_extra,
        load_registry_map.original_models,
    )
    models = load_registry_map.models

    assert "EquityHistorical" in standard_extra
    assert "EquityHistorical" in original_models
    assert "EquityHistorical" in models
