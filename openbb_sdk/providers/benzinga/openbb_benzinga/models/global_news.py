"""Benzinga Global News Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.global_news import GlobalNewsQueryParams
from openbb_provider.utils.helpers import get_querystring
from pydantic import Field

from openbb_benzinga.utils.helpers import BenzingaStockNewsData, get_data


class BenzingaGlobalNewsQueryParams(GlobalNewsQueryParams):
    """Benzinga Global News query.

    Source: https://docs.benzinga.io/benzinga/newsfeed-v2.html
    """

    pageSize: int = Field(
        default=15, description="Number of results to return per page."
    )
    displayOutput: Literal["headline", "summary", "full", "all"] = Field(
        default="headline", description="Type of data to return."
    )
    date: Optional[datetime] = Field(
        default=None, description="Date of the news to retrieve."
    )
    dateFrom: Optional[datetime] = Field(
        default=None, description="Start date of the news to retrieve."
    )
    dateTo: Optional[datetime] = Field(
        default=None, description="End date of the news to retrieve."
    )
    updatedSince: Optional[int] = Field(
        default=None,
        description="Number of seconds since the news was updated.",
    )
    publishedSince: Optional[int] = Field(
        default=None,
        description="Number of seconds since the news was published.",
    )
    sort: Optional[
        Literal[
            "published_at",
            "updated_at",
            "title",
            "author",
            "channel",
            "ticker",
            "topic",
            "content_type",
        ]
    ] = Field(default=None, description="Order in which to sort the news. ")
    isin: Optional[str] = Field(
        default=None, description="The ISIN of the news to retrieve."
    )
    cusip: Optional[str] = Field(
        default=None, description="The CUSIP of the news to retrieve."
    )
    tickers: Optional[str] = Field(
        default=None, description="Tickers of the news to retrieve."
    )
    channels: Optional[str] = Field(
        default=None, description="Channels of the news to retrieve."
    )
    topics: Optional[str] = Field(
        default=None, description="Topics of the news to retrieve."
    )
    authors: Optional[str] = Field(
        default=None, description="Authors of the news to retrieve."
    )
    content_types: Optional[str] = Field(
        default=None, description="Content types of the news to retrieve."
    )


class BenzingaGlobalNewsFetcher(
    Fetcher[
        BenzingaGlobalNewsQueryParams,
        List[BenzingaStockNewsData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BenzingaGlobalNewsQueryParams:
        return BenzingaGlobalNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BenzingaGlobalNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        api_key = credentials.get("benzinga_api_key") if credentials else ""

        base_url = "https://api.benzinga.com/api/v2/news"
        querystring = get_querystring(query.dict(by_alias=True), [])
        request_url = f"{base_url}?{querystring}&token={api_key}"
        data = get_data(request_url, **kwargs)

        if len(data) == 0:
            raise RuntimeError("No news found")

        return data

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[BenzingaStockNewsData]:
        return [BenzingaStockNewsData.from_dict(d) for d in data]
