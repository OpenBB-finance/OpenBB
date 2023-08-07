"""Test provider interface."""
# pylint: disable=redefined-outer-name

import pytest
from openbb_core.app.provider_interface import (
    ProviderChoices,
    ProviderInterface,
    get_provider_interface,
)


@pytest.fixture(scope="module")
def provider_interface():
    """Set up provider_interface."""
    return ProviderInterface()


def test_init(provider_interface):
    """Test init."""
    assert provider_interface


def test_get_provider_interface():
    """Test get provider interface."""
    assert isinstance(get_provider_interface(), ProviderInterface)


def test_map(provider_interface):
    """Test map."""
    provider_interface_map = provider_interface.map
    assert isinstance(provider_interface_map, dict)
    assert len(provider_interface_map) > 0
    assert "StockEOD" in provider_interface_map


def test_required_credentials(provider_interface):
    """Test required credentials."""
    required_credentials = provider_interface.required_credentials
    assert isinstance(required_credentials, list)
    assert len(required_credentials) > 0


def test_model_providers(provider_interface):
    """Test model providers."""
    model_providers = provider_interface.model_providers
    assert isinstance(model_providers, dict)
    assert len(model_providers) > 0


def test_params(provider_interface):
    """Test params."""
    params = provider_interface.params
    assert isinstance(params, dict)
    assert len(params) > 0
    assert "StockEOD" in params


def test_data(provider_interface):
    """Test data."""
    data = provider_interface.data
    assert isinstance(data, dict)
    assert len(data) > 0
    assert "StockEOD" in data


def test_providers_literal(provider_interface):
    """Test providers literal."""
    providers_literal = provider_interface.providers_literal
    assert isinstance(type(providers_literal), type)
    assert len(providers_literal.__args__) > 0
    assert "openbb" not in providers_literal.__args__


def test_provider_choices(provider_interface):
    """Test provider choices."""
    provider_choices = provider_interface.provider_choices
    assert isinstance(provider_choices, type(ProviderChoices))


def test_models(provider_interface):
    """Test models."""
    models = provider_interface.models
    assert isinstance(models, list)
    assert len(models) > 0
    assert "StockEOD" in models
