"""Benzinga Global News Fetcher."""


import math
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_benzinga.utils.helpers import get_data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.global_news import (
    GlobalNewsData,
    GlobalNewsQueryParams,
)
from openbb_provider.utils.helpers import get_querystring
from pydantic import Field, validator


class BenzingaGlobalNewsQueryParams(GlobalNewsQueryParams):
    """Benzinga Global News query.

    Source: https://docs.benzinga.io/benzinga/newsfeed-v2.html
    """

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {
            "display": "displayOutput",
            "limit": "pageSize",
            "start_date": "dateFrom",
            "end_date": "dateTo",
            "updated_since": "updatedSince",
            "published_since": "publishedSince",
        }

    display: Literal["headline", "abstract", "full"] = Field(
        default="full",
        description="Specify headline only (headline), headline + teaser (abstract), or headline + full body (full).",
    )
    date: Optional[str] = Field(
        default=None, description="Date of the news to retrieve."
    )
    start_date: Optional[str] = Field(
        default=None, description="Start date of the news to retrieve."
    )
    end_date: Optional[str] = Field(
        default=None, description="End date of the news to retrieve."
    )
    updated_since: Optional[int] = Field(
        default=None,
        description="Number of seconds since the news was updated.",
    )
    published_since: Optional[int] = Field(
        default=None,
        description="Number of seconds since the news was published.",
    )
    sort: Optional[
        Literal[
            "id",
            "created",
            "updated",
        ]
    ] = Field(default="created", description="Key to sort the news by.")
    order: Optional[Literal["asc", "desc"]] = Field(
        default="desc", description="Order to sort the news by."
    )
    isin: Optional[str] = Field(
        default=None, description="The ISIN of the news to retrieve."
    )
    cusip: Optional[str] = Field(
        default=None, description="The CUSIP of the news to retrieve."
    )
    # tickers: Optional[str] = Field(
    #     default=None, description="Tickers of the news to retrieve."
    # )
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


class BenzingaGlobalNewsData(GlobalNewsData):
    """Benzinga Global News Data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {
            "date": "created",
            "text": "body",
        }

    image: List[Dict[str, str]] = Field(description="Images associated with the news.")
    id: str = Field(description="ID of the news.")
    author: str = Field(description="Author of the news.")
    updated: datetime = Field(description="Updated date of the news.")
    teaser: Optional[str] = Field(description="Teaser of the news.")
    channels: str = Field(description="Channels associated with the news.")
    stocks: str = Field(description="Stocks associated with the news.")
    tags: str = Field(description="Tags associated with the news.")

    @validator("date", "updated", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%a, %d %b %Y %H:%M:%S %z")


class BenzingaGlobalNewsFetcher(
    Fetcher[
        BenzingaGlobalNewsQueryParams,
        List[BenzingaGlobalNewsData],
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
    ) -> Dict:
        token = credentials.get("benzinga_api_key") if credentials else ""
        base_url = "https://api.benzinga.com/api/v2/news"

        query.sort = f"{query.sort}:{query.order}"
        querystring = get_querystring(query.dict(by_alias=True), ["order"])

        pages = math.ceil(query.limit / 100)
        data = []

        for page in range(pages):
            url = f"{base_url}?{querystring}&page={page}&token={token}"
            response = get_data(url, **kwargs)
            data.extend(response)

        data = data[: query.limit]

        return data

    @staticmethod
    def transform_data(
        data: Dict,
    ) -> List[BenzingaGlobalNewsData]:
        data = [
            {
                **item,
                "channels": ",".join(
                    [channel["name"] for channel in item.get("channels", None)]
                ),
                "stocks": ",".join(
                    [stock["name"] for stock in item.get("stocks", None)]
                ),
                "tags": ",".join([tag["name"] for tag in item.get("tags", None)]),
            }
            for item in data
        ]

        return [BenzingaGlobalNewsData.parse_obj(d) for d in data]
