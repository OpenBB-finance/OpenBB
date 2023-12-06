"""Provider Registry Module."""

import traceback
import warnings
from functools import lru_cache
from typing import Dict

from importlib_metadata import entry_points

from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.env import Env
from openbb_core.provider.abstract.provider import Provider


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
    @lru_cache
    def from_extensions() -> Registry:
        """Load providers from entry points."""
        registry = Registry()
        for entry_point in sorted(entry_points(group="openbb_provider_extension")):
            try:
                entry = entry_point.load()
                if isinstance(entry, Provider):
                    registry.include_provider(provider=entry)
            except Exception as e:
                msg = f"Error loading extension: {entry_point.name}\n"
                if Env().DEBUG_MODE:
                    traceback.print_exception(type(e), e, e.__traceback__)
                    raise LoadingError(msg + f"\033[91m{e}\033[0m") from e
                warnings.warn(
                    message=msg,
                    category=OpenBBWarning,
                )
        return registry
