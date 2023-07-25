"""Benzinga Global News Fetcher."""


from datetime import datetime
from typing import Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer, get_querystring
from openbb_provider.models.global_news import GlobalNewsData, GlobalNewsQueryParams
from pydantic import Field

from openbb_benzinga.utils.helpers import BenzingaBaseNewsData, get_data


class BenzingaGlobalNewsQueryParams(GlobalNewsQueryParams):
    """Benzinga Global News query.

    Source: https://docs.benzinga.io/benzinga/newsfeed-v2.html
    """

    pageSize: int = Field(
        default=15, description="The number of results to return per page."
    )
    displayOutput: Literal["headline", "summary", "full", "all"] = Field(
        default="headline", description="The type of data to return."
    )
    date: Optional[datetime] = Field(
        default=None, description="The date of the news to retrieve."
    )
    dateFrom: Optional[datetime] = Field(
        default=None, description="The start date of the news to retrieve."
    )
    dateTo: Optional[datetime] = Field(
        default=None, description="The end date of the news to retrieve."
    )
    updatedSince: Optional[int] = Field(
        default=None,
        description="The number of seconds since the news was updated.",
    )
    publishedSince: Optional[int] = Field(
        default=None,
        description="The number of seconds since the news was published.",
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
    ] = Field(
        default=None,
        description="The order in which to sort the news. Options are: published_at, updated_at, title, author, channel, ticker, topic, content_type.",
    )
    isin: Optional[str] = Field(
        default=None, description="The ISIN of the news to retrieve."
    )
    cusip: Optional[str] = Field(
        default=None, description="The CUSIP of the news to retrieve."
    )
    tickers: Optional[str] = Field(
        default=None, description="The tickers of the news to retrieve."
    )
    channels: Optional[str] = Field(
        default=None, description="The channels of the news to retrieve."
    )
    topics: Optional[str] = Field(
        default=None, description="The topics of the news to retrieve."
    )
    authors: Optional[str] = Field(
        default=None, description="The authors of the news to retrieve."
    )
    content_types: Optional[str] = Field(
        default=None, description="The content types of the news to retrieve."
    )


class BenzingaGlobalNewsData(BenzingaBaseNewsData):
    url: str


class BenzingaGlobalNewsFetcher(
    Fetcher[
        GlobalNewsQueryParams,
        GlobalNewsData,
        BenzingaGlobalNewsQueryParams,
        BenzingaGlobalNewsData,
    ]
):
    @staticmethod
    def transform_query(
        query: GlobalNewsQueryParams, extra_params: Optional[Dict] = None
    ) -> BenzingaGlobalNewsQueryParams:
        return BenzingaGlobalNewsQueryParams(
            page=query.page, **extra_params if extra_params else {}
        )

    @staticmethod
    def extract_data(
        query: BenzingaGlobalNewsQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[BenzingaGlobalNewsData]:
        if credentials:
            api_key = credentials.get("benzinga_api_key")

        base_url = "https://api.benzinga.com/api/v2/news"
        querystring = get_querystring(query.dict(), [])
        request_url = f"{base_url}?{querystring}&token={api_key}"
        data = get_data(request_url)

        if len(data) == 0:
            raise RuntimeError("No news found")

        return [BenzingaGlobalNewsData(**d) for d in data]

    @staticmethod
    def transform_data(
        data: List[BenzingaGlobalNewsData],
    ) -> List[GlobalNewsData]:
        processors = {"image": lambda x: "" if x == [] else x[0].url}
        return data_transformer(data, GlobalNewsData, processors)
