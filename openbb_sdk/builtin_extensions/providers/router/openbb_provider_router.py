import re
from typing import Annotated, Type, TypeVar

from fastapi import Depends
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.abstract.provider import ProviderName
from openbb_provider.provider.provider_map import build_provider_mapping
from openbb_sdk_core.app.model.command_context import CommandContext
from openbb_sdk_core.app.model.command_output import CommandOutput
from openbb_sdk_core.app.router import Router

from openbb_sdk.builtin_extensions.providers.model.item.registry import build_registry

registry = build_registry()
meta_router = Router()

Q = TypeVar("Q", bound=QueryParams)
D = TypeVar("D", bound=Data)


def create_standardized(
    QueryParamsType: Type[QueryParams],
    DataType: Type[Data],
    provider: ProviderName,
):
    def standardized(
        cc: CommandContext,
        query: Annotated[QueryParamsType, Depends()],  # type: ignore
    ) -> CommandOutput[DataType]:  # type: ignore
        registry.api_keys[provider] = getattr(
            cc.user_settings.credentials, provider + "_api_key"
        )
        results = registry.standardized(
            provider_name=provider,
            query=query,
        )
        return CommandOutput(results=results)

    return standardized


def create_simple(
    QueryParamsType: Type[QueryParams],
    DataType: Type[Data],
    provider: ProviderName,
):
    def simple(
        cc: CommandContext,
        query: Annotated[QueryParamsType, Depends()],  # type: ignore
    ) -> CommandOutput[DataType]:  # type: ignore
        registry.api_keys[provider] = getattr(
            cc.user_settings.credentials, provider + "_api_key"
        )
        results = registry.simple(
            provider_name=provider,
            query=query,
        )
        return CommandOutput(results=results)

    return simple


def find_fetcher(
    provider_name: ProviderName, endpoint_name: str, provider_registry_mapping: dict
) -> Fetcher:
    """Find the Provider-specific Fetcher based on a given endpoint name.

    Parameter
    ----------
        provider_name (ProviderName): The name of the data provider.
        endpoint_name (str): The name of the data endpoint.
        provider_registry_mapping (dict): The internal provider registry mapping.

    Return
    -------
        Fetcher: The Fetcher that is used for creating an endpoint.
    """
    # TODO: We receive the ProviderName as a lowercase string (benzinga), but the
    # fetcher name convention is CamelCase (BenzingaStockPriceFetcher)
    # or all capital (FMPStockPriceFetcher).
    # It will break in the case that the Fetcher name is in CamelCase (BenZingaStockPriceFetcher).
    # Solution: Have a mapping of provider names to fetcher names.
    # {"benzinga": "BenZinga", "fmp": "FMP", "polygon": "Polygon"}
    try:
        query_params = provider_name.capitalize() + endpoint_name + "QueryParams"
        fetcher = provider_registry_mapping[provider_name].__dict__["fetcher_dict"][
            "get_provider_query_type"
        ][query_params]
    except KeyError:
        query_params = provider_name.upper() + endpoint_name + "QueryParams"
        fetcher = provider_registry_mapping[provider_name].__dict__["fetcher_dict"][
            "get_provider_query_type"
        ][query_params]

    return fetcher


def fix_path(path: str) -> str:
    """Fixes the path by trimming underscores in between single letters.
    Example: s_e_c_filings -> sec_fillings

    Parameter
    ---------
        path (str): The path of the endpoint.

    Return
    -------
        str: The updated path of the endpoint.
    """
    words = path.split("_")
    merged_words = []
    merged_word = []

    for word in words:
        if len(word) == 1:
            merged_word.append(word)
        else:
            if merged_word:
                merged_words.append("".join(merged_word))
                merged_word = []
            merged_words.append(word)

    if merged_word:
        merged_words.append("".join(merged_word))

    return "_".join(merged_words)


def build_meta_router(provider_registry_mapping: dict, func) -> Router:
    """Create a meta router that dynamically includes all the routes and commands.

    Parameter
    ----------
        provider_registry_mapping (dict): provider table mapping
        standard (bool): whether to use the OpenBB standard path

    Return
    -------
        Router: meta router
    """

    provider_mapping = build_provider_mapping()

    for data_endpoint in provider_mapping["Data"]:
        providers = list(provider_mapping["Data"][data_endpoint].keys())
        if "openbb" in providers:
            providers.remove("openbb")

        endpoint_name = data_endpoint.replace("Data", "")
        subpath = "_".join(re.findall("[A-Z][^A-Z]*", endpoint_name)).lower()
        subpath = fix_path(path=subpath)

        for provider_name in providers:
            data_router = Router(prefix=f"/{provider_name}/{subpath}")
            fetcher = find_fetcher(
                provider_name, endpoint_name, provider_registry_mapping
            )

            command_args = {}
            if "simple" in func.__name__:
                query_type = fetcher.get_provider_query_type()
                data_type = fetcher.get_provider_data_type()
                command_args["path"] = "/simple"
            elif "standardized" in func.__name__:
                query_type = fetcher.get_provider_query_type()
                data_type = fetcher.get_data_type()
                command_args["path"] = "/standardized"

            data_router.command(
                func=func(query_type, data_type, provider_name),
                description=data_type.__doc__,
                **command_args,
            )
            meta_router.include_router(router=data_router)

    return meta_router


init_meta_dict = {
    "create_standardized": {
        "func": create_standardized,
    },
    "create_simple": {
        "func": create_simple,
    },
}

for key, value in init_meta_dict.items():
    router = Router()
    # router = build_meta_router(
    #     provider_registry_mapping=registry.provider_mapping,
    #     func=value["func"],
    # )
