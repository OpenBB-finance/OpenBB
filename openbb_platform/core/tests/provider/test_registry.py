"""Test the Registry."""

from openbb_core.provider.abstract.provider import Provider
from openbb_core.provider.registry import Registry, RegistryLoader


def test_registry():
    """Test the registry."""
    registry = Registry()
    assert registry.providers == {}

    mock_provider = Provider(name="TestProvider", description="Just a test provider.")
    registry.include_provider(mock_provider)

    assert "testprovider" in registry.providers
    assert registry.providers["testprovider"] == mock_provider


def test_registry_loader_integration():
    """Execute the loading process."""
    core_providers = ["fmp", "polygon", "fred", "benzinga", "intrinio"]
    registry = RegistryLoader.from_extensions()

    assert len(registry.providers) > 0

    for provider in core_providers:
        assert provider in registry.providers

    for provider in registry.providers.values():
        assert isinstance(provider, Provider)
