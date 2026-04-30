"""Test the Registry."""

import warnings
from unittest.mock import patch

import pytest

from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.provider.abstract.provider import Provider
from openbb_core.provider.registry import LoadingError, Registry, RegistryLoader


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


def test_registry_loader_warns_on_bad_provider_when_not_debug(monkeypatch):
    RegistryLoader.from_extensions.cache_clear()

    class _BadProvider:
        name = None

    monkeypatch.setattr(
        "openbb_core.provider.registry.ExtensionLoader",
        type("L", (), {"provider_objects": {"bad": _BadProvider()}}),
    )
    monkeypatch.setattr(
        "openbb_core.provider.registry.Env",
        type("E", (), {"DEBUG_MODE": False}),
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        registry = RegistryLoader.from_extensions()

    assert registry.providers == {}
    assert any(isinstance(item.message, OpenBBWarning) for item in caught)
    RegistryLoader.from_extensions.cache_clear()


def test_registry_loader_raises_loading_error_in_debug(monkeypatch):
    RegistryLoader.from_extensions.cache_clear()

    class _BadProvider:
        name = None

    monkeypatch.setattr(
        "openbb_core.provider.registry.ExtensionLoader",
        type("L", (), {"provider_objects": {"bad": _BadProvider()}}),
    )
    monkeypatch.setattr(
        "openbb_core.provider.registry.Env",
        type("E", (), {"DEBUG_MODE": True}),
    )
    monkeypatch.setattr(
        "openbb_core.provider.registry.traceback.print_exception", lambda *_a: None
    )

    with pytest.raises(LoadingError, match="Error loading extension: bad"):
        RegistryLoader.from_extensions()
    RegistryLoader.from_extensions.cache_clear()
