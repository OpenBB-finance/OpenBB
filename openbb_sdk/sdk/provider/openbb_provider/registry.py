from typing import Dict

import pkg_resources

from openbb_provider.abstract.provider import Provider


class Registry:
    """Class to maintain registry of providers"""

    def __init__(self) -> None:
        self._providers: Dict[str, Provider] = {}

    @property
    def providers(self):
        return self._providers

    def include_provider(self, provider: Provider) -> None:
        self._providers[provider.name.lower()] = provider


class LoadingError(Exception):
    pass


class RegistryLoader:
    @staticmethod
    def from_extensions() -> Registry:
        registry = Registry()
        for entry_point in pkg_resources.iter_entry_points("openbb_provider_extension"):
            try:
                registry.include_provider(
                    provider=entry_point.load(),
                )
            except Exception as e:
                raise LoadingError(f"Invalid provider '{entry_point.name}': {e}") from e

        return registry
