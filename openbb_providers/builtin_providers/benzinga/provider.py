"""Benzinga provider module."""

# IMPORT STANDARD

# IMPORT THIRD-PARTY

from builtin_providers.benzinga.global_news import BenzingaGlobalNewsFetcher
from builtin_providers.benzinga.stock_news import BenzingaStockNewsFetcher

# IMPORT INTERNAL
from openbb_provider.provider.abstract.provider import Provider

# mypy: disable-error-code="list-item"


#  ignoring because I dont know how to type the string properly
benzinga_provider = Provider(
    name="benzinga",  # type: ignore
    description="Provider for Benzinga.",
    fetcher_list=[BenzingaGlobalNewsFetcher, BenzingaStockNewsFetcher],
)
