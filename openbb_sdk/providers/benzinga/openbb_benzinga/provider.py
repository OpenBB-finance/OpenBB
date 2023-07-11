"""Benzinga provider module."""

# IMPORT STANDARD

# IMPORT THIRD-PARTY

# IMPORT INTERNAL
from builtin_providers.benzinga.global_news import BenzingaGlobalNewsFetcher
from builtin_providers.benzinga.stock_news import BenzingaStockNewsFetcher
from openbb_provider.provider.abstract.provider import Provider, ProviderNameType

# mypy: disable-error-code="list-item"


benzinga_provider = Provider(
    name=ProviderNameType("benzinga"),
    description="Provider for Benzinga.",
    fetcher_list=[BenzingaGlobalNewsFetcher, BenzingaStockNewsFetcher],
)
