"""ProviderRegistry class and Builder class."""


from typing import Any, Dict, List, Literal, Optional, Tuple, Union
from warnings import warn

import pkg_resources

from openbb_provider.abstract.data import QueryParams
from openbb_provider.abstract.fetcher import ProviderDataType
from openbb_provider.abstract.provider import Provider, ProviderNameType
from openbb_provider.settings import Settings, settings

orients = Literal["LIST", "RECORDS"]


def process(
    data: Union[List[ProviderDataType], ProviderDataType], orientation: orients
) -> Any:
    """
    Convert the data into the desired orientation.

    Naming is based on the pandas to_dict() method:
    https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_dict.html

    Parameters
    ----------
    data: Union[List[ProviderDataType], ProviderDataType]
        The data to be processed.
    orientation: orients
        The orientation of the data to be returned.

    Returns
    -------
    Any
        The processed data.
    """
    if not isinstance(data, list):
        # TODO: how do we want to handle this?
        return data
    if orientation == "RECORDS":
        return data
    if orientation == "LIST":
        layout = data[0].dict()
        new_dict: Dict[str, list] = {x: [] for x in layout}
        for item in data:
            for key, value in item.dict().items():
                new_dict[key].append(value)
        return [new_dict]
    raise ValueError(f"Orientation {orientation} is not supported.")


class ProviderRegistry:
    """A Provider Registry is the central executor for dynamically retrieving data."""

    def __init__(self) -> None:
        self.provider_mapping: Dict[ProviderNameType, Provider] = {}
        self.api_keys: Dict[ProviderNameType, str] = {}

    def add(self, provider: Provider) -> None:
        """Add a provider to the ProviderRegistry."""
        if provider.name not in self.provider_mapping:
            self.provider_mapping[provider.name] = provider
        else:
            raise ValueError(
                f"Provider {provider.name} is already in the ProviderRegistry."
            )

    def __fetch_factory__(  # noqa: PLR0913
        self,
        provider_name: ProviderNameType,
        query: QueryParams,
        extra_params: Optional[Dict],
        query_name: str,
        data_name: str,  # type: ignore
        data_orientation: orients,
    ):
        """Create method for fetching data from a provider."""
        if not self.provider_mapping:
            raise ValueError(
                "Provider Mapping is empty. Please confirm plugins are loaded."
            )
        try:
            provider = self.provider_mapping[provider_name]
        except KeyError as e:
            raise ValueError(
                f"{provider_name} is not part of the ProviderRegistry. "
                f"Available providers are: {list(self.provider_mapping.keys())}"
            ) from e
        api_key = self.api_keys[provider_name]

        fetch_dict = provider.fetcher_dict[query_name]
        fetcher = fetch_dict.get(query.__name__)  # type: ignore
        if fetcher is None:
            raise ValueError(
                f"This query is not supported by the {provider_name} provider. "
                f"Please try another provider: {ProviderNameType.__args__}"
            )

        try:
            if data_name == "standardized":
                result = getattr(fetcher, data_name)(query, api_key)
            else:
                result = getattr(fetcher, data_name)(query, extra_params, api_key)
            return process(result, data_orientation)
        except Exception as e:
            raise RuntimeError(
                f"The {provider_name} provider failed to fetch the data: {e}"
            ) from e

    def fetch(
        self,
        provider_name: ProviderNameType,
        query: QueryParams,
        extra_params: Optional[Dict] = None,
        data_orientation: orients = "RECORDS",
    ):
        """Fetch data from a provider by using the OpenBB standard."""
        return self.__fetch_factory__(
            provider_name,
            query,
            extra_params,
            "get_query_type",
            "fetch_data",
            data_orientation,
        )

    def fetch_provider_data(
        self,
        provider_name: ProviderNameType,
        query: QueryParams,
        extra_params: Optional[Dict] = None,
        data_orientation: orients = "RECORDS",
    ):
        """Fetch data from a provider by using provider-specific QueryParams."""
        return self.__fetch_factory__(
            provider_name,
            query,
            extra_params,
            "get_query_type",
            "fetch_provider_data",
            data_orientation,
        )

    def standardized(
        self,
        provider_name: ProviderNameType,
        query: QueryParams,
        extra_params: Optional[Dict] = None,
        data_orientation: orients = "RECORDS",
    ):
        """Obtain only standardized data from a provider by using the OpenBB standard."""
        return self.__fetch_factory__(
            provider_name,
            query,
            extra_params,
            "get_provider_query_type",
            "standardized",
            data_orientation,
        )

    def simple(
        self,
        provider_name: ProviderNameType,
        query: QueryParams,
        extra_params: Optional[Dict] = None,
        data_orientation: orients = "RECORDS",
    ):
        """Obtain raw data from a provider by only using provider-specific QueryParams."""
        return self.__fetch_factory__(
            provider_name,
            query,
            extra_params,
            "get_provider_query_type",
            "simple",
            data_orientation,
        )


class Builder:
    """Build out the provider table by adding providers and their API keys to it.

    It can build multiple different types of Provider Registries with their own state.
    """

    def __init__(self) -> None:
        self.provider_registry = ProviderRegistry()
        self.api_keys: Dict[ProviderNameType, str] = {}

    def add_providers(self, providers: List[Provider]):
        """Add a list of providers to the ProviderRegistry."""
        for provider in providers:
            self.provider_registry.add(provider)
        return f"{len(providers)} providers have been added."

    def add_api_key(self, provider_name: ProviderNameType, api_key: str) -> str:
        """Add an API key to the ProviderRegistry."""
        if provider_name not in self.api_keys:
            self.api_keys[provider_name] = api_key
        else:
            raise ValueError(
                f"API key for {provider_name} is already in the ProviderRegistry."
            )

        self.provider_registry.api_keys[provider_name] = api_key
        return f"API key for {provider_name} has been added."

    def add_keys(self, api_keys: Dict[ProviderNameType, str]) -> str:
        """Add a dictionary of API keys to the ProviderRegistry."""
        for provider_name, api_key in api_keys.items():
            self.add_api_key(provider_name, api_key)

        return f"{len(api_keys)} API keys have been added."

    def build(self) -> ProviderRegistry:
        """Build the ProviderRegistry."""
        return self.provider_registry


def update_settings(base_settings: Settings, extension) -> Settings:
    """Update the settings with the API key placeholders."""
    if getattr(extension, "credentials", False):
        provider_name = extension.name.upper()
        updated_settings = base_settings.copy(update={f"{provider_name}_API_KEY": None})

        return updated_settings
    return base_settings


def load_extensions(
    entry_point_group: str = "openbb_provider_extension",
) -> Tuple[list, dict]:
    """Load extensions from entry points and their API keys from settings.

    Parameters
    ----------
    entry_point_group : str
        The entry point group to load extensions from.

    Returns
    -------
    Tuple[list, dict]
        A tuple of the extensions and their API keys.
    """
    extensions = []
    extension_api_keys = {}

    entry_points = pkg_resources.iter_entry_points(entry_point_group)
    for entry_point in entry_points:
        extensions.append(entry_point.load())

    for extension in extensions:
        extension_name = extension.name
        updated_settings = update_settings(settings, extension)
        try:
            if extension_name in ProviderNameType.__args__:
                extension_api_keys[extension_name] = getattr(
                    updated_settings, f"{extension_name.upper()}_API_KEY"
                )
        except AttributeError as exc:
            if getattr(extension, "credentials", False):
                warn(f"API key for {extension_name} is not set.", UserWarning)
            elif getattr(extension, "credentials", False) is False:
                # The extension does not require credentials, so we can pass.
                pass
            else:
                raise ValueError(
                    f"Credentials for {extension_name} are not set."
                    "Please indicate if the extension requires credentials."
                ) from exc

    return extensions, extension_api_keys


def build_provider_registry() -> ProviderRegistry:
    """Build a provider registry."""
    provider_registry_builder = Builder()
    extensions = []

    entry_points = pkg_resources.iter_entry_points("openbb_provider_extension")
    for entry_point in entry_points:
        extensions.append(entry_point.load())

    provider_registry_builder.add_providers(extensions)
    return provider_registry_builder.build()


entry_point_extensions, entry_point_extension_api_keys = load_extensions(
    "openbb_provider_extension"
)
builder = Builder()
builder.add_keys(entry_point_extension_api_keys)
builder.add_providers(entry_point_extensions)
provider_registry = builder.build()
