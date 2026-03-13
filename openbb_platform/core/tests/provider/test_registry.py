"""Test the Registry."""

from unittest.mock import patch

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


def test_registry_loader_from_extensions():
    """Test the RegistryLoader loads providers from extensions."""
    # Clear the lru_cache to ensure fresh loading
    RegistryLoader.from_extensions.cache_clear()

    mock_provider_a = Provider(name="MockProviderA", description="Mock provider A")
    mock_provider_b = Provider(name="MockProviderB", description="Mock provider B")

    with patch(
        "openbb_core.provider.registry.ExtensionLoader"
    ) as mock_extension_loader:
        mock_extension_loader.return_value.provider_objects = {
            "mock_provider_a": mock_provider_a,
            "mock_provider_b": mock_provider_b,
        }

        registry = RegistryLoader.from_extensions()

        assert len(registry.providers) == 2
        assert "mockprovidera" in registry.providers
        assert "mockproviderb" in registry.providers
        assert registry.providers["mockprovidera"] == mock_provider_a
        assert registry.providers["mockproviderb"] == mock_provider_b

    # Clear cache after test
    RegistryLoader.from_extensions.cache_clear()
