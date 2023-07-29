"""Benzinga provider module."""


from openbb_provider.abstract.provider import Provider

from openbb_benzinga.models.global_news import BenzingaGlobalNewsFetcher
from openbb_benzinga.models.stock_news import BenzingaStockNewsFetcher

# mypy: disable-error-code="list-item"


benzinga_provider = Provider(
    name="benzinga",
    description="Provider for Benzinga.",
    required_credentials=["api_key"],
    fetcher_dict={
        "GlobalNews": BenzingaGlobalNewsFetcher,
        "StockNews": BenzingaStockNewsFetcher,
    },
)
