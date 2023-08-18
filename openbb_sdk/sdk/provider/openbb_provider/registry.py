"""Provider Registry Module."""

from typing import Dict

from importlib_metadata import entry_points

from openbb_provider.abstract.provider import Provider


class Registry:
    """Maintain registry of providers."""

    def __init__(self) -> None:
        """Initialize the registry."""
        self._providers: Dict[str, Provider] = {}

    @property
    def providers(self):
        """Return a dictionary of providers."""
        return self._providers

    def include_provider(self, provider: Provider) -> None:
        """Include a provider in the registry."""
        self._providers[provider.name.lower()] = provider


class LoadingError(Exception):
    """Error loading provider."""


class RegistryLoader:
    """Load providers from entry points."""

    @staticmethod
    def from_extensions() -> Registry:
        """Load providers from entry points."""
        registry = Registry()
        for entry_point in sorted(entry_points(group="openbb_provider_extension")):
            try:
                registry.include_provider(provider=entry_point.load())
            except Exception as e:
                raise LoadingError(f"Invalid provider '{entry_point.name}': {e}") from e

        return registry
