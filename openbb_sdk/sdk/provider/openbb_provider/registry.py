from openbb_provider.abstract.provider import Provider
import pkg_resources


class Registry:
    """Class to maintain registry of providers"""

    def __init__(self) -> None:
        self._providers = {}

    @property
    def providers(self):
        return self._providers

    def include_provider(self, name: str, provider: Provider) -> None:
        self._providers[name.lower()] = provider


class ExtensionError(Exception):
    pass


class RegistryLoader:
    @staticmethod
    def from_extensions() -> Registry:
        registry = Registry()
        for entry_point in pkg_resources.iter_entry_points("openbb_provider_extension"):
            try:
                registry.include_provider(
                    name=entry_point.name,
                    provider=entry_point.load(),
                )
            except Exception as e:
                raise ExtensionError(
                    f"Invalid provider '{entry_point.name}': {e}"
                ) from e

        return registry
