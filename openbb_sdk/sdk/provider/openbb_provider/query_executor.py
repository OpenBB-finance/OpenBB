from typing import Any, Dict, Optional

from openbb_provider.abstract.provider import Provider
from openbb_provider.registry import Registry, RegistryLoader


class ProviderError(Exception):
    pass


class QueryExecutor:
    """Class to execute queries from providers"""

    def __init__(self, registry: Optional[Registry] = None) -> None:
        self.registry = registry or RegistryLoader.from_extensions()

    def get_provider(self, provider_name: str):
        """Get a provider from the registry."""
        # raise exception if provider not found
        return self.registry.providers[provider_name.lower()]

    def get_fetcher(self, provider: Provider, model_name: str):
        """Get a fetcher from a provider"""
        # raise exception if fetcher not found
        fetcher_name = (provider.name + model_name + "fetcher").lower()
        return provider.fetcher_dict[fetcher_name]

    def match_credentials(
        self, provider: Provider, credentials: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        """Filter received credentials to match provider requirements"""
        if provider.required_credentials is None:
            return {}

        if credentials is None:
            credentials = {}

        result: Dict[str, str] = {}
        for c in provider.formatted_credentials:
            credential_value = credentials.get(c)
            if c not in credentials or credential_value is None:
                raise ProviderError(f"Missing credential '{c}' for '{provider.name}'.")

            result[c] = credential_value

        return result

    def execute(
        self,
        provider_name: str,
        model_name: str,
        params: Dict[str, Any],
        credentials: Optional[Dict[str, str]] = None,
    ):
        """Execute query"""

        provider = self.get_provider(provider_name)
        Fetcher_ = self.get_fetcher(provider, model_name)
        matched_credentials = self.match_credentials(provider, credentials)

        try:
            return Fetcher_.fetch_data(params, matched_credentials)
        except Exception as e:
            raise ProviderError(e) from e
