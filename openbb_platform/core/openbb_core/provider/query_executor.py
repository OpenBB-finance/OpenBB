"""Query executor module."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.provider import Provider
from openbb_core.provider.registry import Registry, RegistryLoader
from pydantic import SecretStr


class QueryExecutor:
    """Class to execute queries from providers."""

    def __init__(self, registry: Registry | None = None) -> None:
        """Initialize the query executor."""
        self.registry = registry or RegistryLoader.from_extensions()

    def get_provider(self, provider_name: str) -> Provider:
        """Get a provider from the registry."""
        name = provider_name.lower()
        if name not in self.registry.providers:
            raise OpenBBError(
                f"Provider '{name}' not found in the registry.Available providers: {list(self.registry.providers.keys())}"
            )
        return self.registry.providers[name]

    def get_fetcher(self, provider: Provider, model_name: str) -> type[Fetcher]:
        """Get a fetcher from a provider."""
        if model_name not in provider.fetcher_dict:
            raise OpenBBError(
                f"Fetcher not found for model '{model_name}' in provider '{provider.name}'."
            )
        return provider.fetcher_dict[model_name]

    @staticmethod
    def filter_credentials(
        credentials: dict[str, SecretStr] | None,
        provider: Provider,
        require_credentials: bool,
    ) -> dict[str, str]:
        """Filter credentials and check if they match provider requirements."""
        filtered_credentials = {}

        if provider.credentials:
            if credentials is None:
                credentials = {}

            for c in provider.credentials:
                v = credentials.get(c)
                secret = v.get_secret_value() if v else None
                if c not in credentials or not secret:
                    if require_credentials:
                        website = provider.website or ""
                        extra_msg = f" Check {website} to get it." if website else ""
                        raise OpenBBError(
                            f"Missing credential '{c}'.{extra_msg} Refer to the documentation for setting provider "
                            "credentials at https://docs.openbb.co/platform/settings/user_settings/api_keys."
                        )
                else:
                    filtered_credentials[c] = secret

        return filtered_credentials

    async def execute(
        self,
        provider_name: str,
        model_name: str,
        params: dict[str, Any],
        credentials: dict[str, SecretStr] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Execute query.

        Parameters
        ----------
        provider_name : str
            Name of the provider, for example: "fmp".
        model_name : str
            Name of the model, for example: "EquityHistorical".
        params : Dict[str, Any]
            Query parameters, for example: {"symbol": "AAPL"}
        credentials : Optional[Dict[str, SecretStr]], optional
            Credentials for the provider, by default None
            For example, {"fmp_api_key": SecretStr("1234")}.

        Returns
        -------
        Any
            Query result.
        """
        provider = self.get_provider(provider_name)
        fetcher = self.get_fetcher(provider, model_name)
        filtered_credentials = self.filter_credentials(
            credentials, provider, fetcher.require_credentials
        )
        return await fetcher.fetch_data(params, filtered_credentials, **kwargs)
