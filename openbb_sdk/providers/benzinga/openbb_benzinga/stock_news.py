"""Benzinga Stock News Fetcher."""

# IMPORT STANDARD
from datetime import datetime
from typing import Dict, List, Optional

from builtin_providers.benzinga.helpers import BenzingaBaseNewsData, get_data

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import QueryParams
from openbb_provider.model.data.stock_news import StockNewsData, StockNewsQueryParams
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer, get_querystring

# IMPORT THIRD-PARTY
from pydantic import Field


class BenzingaStockNewsQueryParams(QueryParams):
    """Benzinga Stock News query.

    Source: https://docs.benzinga.io/benzinga/newsfeed-v2.html

    Parameter
    ---------
    page : int (default: 0)
        The page of the data to retrieve.
    symbols: str
        The symbols of the companies.
    pageSize : int (default: 15)
        The number of results to return per page.
    headline : str
        The type of data to return. Options are "headline", "summary", "full", "all".
    date : Optional[datetime]
        The date of the news to retrieve.
    dateFrom : Optional[datetime]
        The start date of the news to retrieve.
    dateTo : Optional[datetime]
        The end date of the news to retrieve.
    updatedSince : Optional[int]
        The number of seconds since the news was updated.
    publishedSince : Optional[int]
        The number of seconds since the news was published.
    sort : Optional[str]
        The order in which to sort the news. Options are:
        "published_at", "updated_at", "title", "author", "channel", "ticker", "topic", "content_type".
    isin : Optional[str]
        The ISIN of the news to retrieve.
    cusip : Optional[str]
        The CUSIP of the news to retrieve.
    channels : Optional[str]
        The channels of the news to retrieve.
    topics : Optional[str]
        The topics of the news to retrieve.
    authors : Optional[str]
        The authors of the news to retrieve.
    content_types : Optional[str]
        The content types of the news to retrieve.
    """

    tickers: str = Field(alias="symbols")
    page: int = Field(default=0)
    pageSize: int = Field(default=15)
    displayOutput: str = Field(default="headline")
    date: Optional[datetime] = None
    dateFrom: Optional[datetime] = None
    dateTo: Optional[datetime] = None
    updatedSince: Optional[int] = None
    publishedSince: Optional[int] = None
    sort: Optional[str] = None
    isin: Optional[str] = None
    cusip: Optional[str] = None
    channels: Optional[str] = None
    topics: Optional[str] = None
    authors: Optional[str] = None
    content_types: Optional[str] = None


class BenzingaStockNewsData(BenzingaBaseNewsData):
    """Benzinga Stock News data."""


class BenzingaStockNewsFetcher(
    Fetcher[
        StockNewsQueryParams,
        StockNewsData,
        BenzingaStockNewsQueryParams,
        BenzingaStockNewsData,
    ]
):
    @staticmethod
    def transform_query(
        query: StockNewsQueryParams, extra_params: Optional[Dict] = None
    ) -> BenzingaStockNewsQueryParams:
        return BenzingaStockNewsQueryParams(
            page=query.page,
            symbols=query.symbols,  # type: ignore
            **extra_params if extra_params else {},
        )

    @staticmethod
    def extract_data(
        query: BenzingaStockNewsQueryParams, api_key: str
    ) -> List[BenzingaStockNewsData]:
        base_url = "https://api.benzinga.com/api/v2/news"
        querystring = get_querystring(query.dict(), [])
        request_url = f"{base_url}?{querystring}&token={api_key}"
        data = get_data(request_url)

        if len(data) == 0:
            raise RuntimeError("No news found")

        return [BenzingaStockNewsData(**d) for d in data]

    @staticmethod
    def transform_data(data: List[BenzingaStockNewsData]) -> List[StockNewsData]:
        processors = {"image": lambda x: "" if x == [] else x[0].url}
        return data_transformer(data, StockNewsData, processors)
