"""Query executor module."""
from typing import Any, Dict, Optional, Type

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.abstract.provider import Provider
from openbb_provider.registry import Registry, RegistryLoader


class ProviderError(Exception):
    """Exception raised for errors in the provider."""


class QueryExecutor:
    """Class to execute queries from providers."""

    def __init__(self, registry: Optional[Registry] = None) -> None:
        """Initialize the query executor."""
        self.registry = registry or RegistryLoader.from_extensions()

    def get_provider(self, provider_name: str) -> Provider:
        """Get a provider from the registry."""
        name = provider_name.lower()
        if name not in self.registry.providers:
            raise ProviderError(
                f"Provider '{name}' not found in the registry."
                f"Available providers: {list(self.registry.providers.keys())}"
            )
        return self.registry.providers[name]

    def get_fetcher(self, provider: Provider, model_name: str) -> Type[Fetcher]:
        """Get a fetcher from a provider."""
        if model_name not in provider.fetcher_dict:
            raise ProviderError(
                f"Fetcher not found for model '{model_name}' in provider '{provider.name}'."
            )
        return provider.fetcher_dict[model_name]

    @staticmethod
    def verify_credentials(provider: Provider, credentials: Optional[Dict[str, str]]):
        """Verify credentials to match provider requirements."""
        if provider.required_credentials is not None:
            if credentials is None:
                credentials = {}
            for c in provider.required_credentials:
                credential_value = credentials.get(c)
                if c not in credentials or credential_value is None:
                    raise ProviderError(f"Missing credential '{c}'.")

    def execute(
        self,
        provider_name: str,
        model_name: str,
        params: Dict[str, Any],
        credentials: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Any:
        """Execute query.

        Parameters
        ----------
        provider_name : str
            Name of the provider, for example: "fmp".
        model_name : str
            Name of the model, for example: "StockHistorical".
        params : Dict[str, Any]
            Query parameters, for example: {"symbol": "AAPL"}
        credentials : Optional[Dict[str, str]], optional
            Credentials for the provider, by default None
            For example, {"fmp_api_key": "1234"}.

        Returns
        -------
        Any
            Query result.
        """
        provider = self.get_provider(provider_name)
        self.verify_credentials(provider, credentials)
        fetcher = self.get_fetcher(provider, model_name)

        try:
            return fetcher.fetch_data(params, credentials, **kwargs)
        except Exception as e:
            raise ProviderError(e) from e
