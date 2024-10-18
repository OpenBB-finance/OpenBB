"""Benzinga World News Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.world_news import (
    WorldNewsData,
    WorldNewsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
from pydantic import Field, field_validator


class BenzingaWorldNewsQueryParams(WorldNewsQueryParams):
    """Benzinga World News Query.

    Source: https://docs.benzinga.io/benzinga/newsfeed-v2.html
    """

    __alias_dict__ = {
        "display": "displayOutput",
        "limit": "pageSize",
        "start_date": "dateFrom",
        "end_date": "dateTo",
        "updated_since": "updatedSince",
        "published_since": "publishedSince",
    }
    date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("date", "")
    )
    display: Literal["headline", "abstract", "full"] = Field(
        default="full",
        description="Specify headline only (headline), headline + teaser (abstract), or headline + full body (full).",
    )
    updated_since: Optional[int] = Field(
        default=None,
        description="Number of seconds since the news was updated.",
    )
    published_since: Optional[int] = Field(
        default=None,
        description="Number of seconds since the news was published.",
    )
    sort: Literal["id", "created", "updated"] = Field(
        default="created", description="Key to sort the news by."
    )
    order: Literal["asc", "desc"] = Field(
        default="desc", description="Order to sort the news by."
    )
    isin: Optional[str] = Field(
        default=None, description="The ISIN of the news to retrieve."
    )
    cusip: Optional[str] = Field(
        default=None, description="The CUSIP of the news to retrieve."
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


class BenzingaWorldNewsData(WorldNewsData):
    """Benzinga World News Data."""

    __alias_dict__ = {"date": "created", "text": "body", "images": "image"}

    id: str = Field(description="Article ID.")
    author: Optional[str] = Field(default=None, description="Author of the news.")
    teaser: Optional[str] = Field(description="Teaser of the news.", default=None)
    channels: Optional[str] = Field(
        default=None,
        description="Channels associated with the news.",
    )
    stocks: Optional[str] = Field(
        description="Stocks associated with the news.",
        default=None,
    )
    tags: Optional[str] = Field(
        description="Tags associated with the news.",
        default=None,
    )
    updated: Optional[datetime] = Field(
        default=None, description="Updated date of the news."
    )

    @field_validator("date", "updated", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%a, %d %b %Y %H:%M:%S %z")

    @field_validator("stocks", "channels", "tags", mode="before", check_fields=False)
    @classmethod
    def list_validate(cls, v):
        """Return the list as a string."""
        v = ",".join([item.get("name", None) for item in v if item.get("name", None)])
        return v if v != "" else None

    @field_validator(
        "id", "text", "teaser", "title", "author", mode="before", check_fields=False
    )
    @classmethod
    def id_validate(cls, v):
        """Return the a string if the field is not empty."""
        return str(v) if v else None

    @field_validator("images", mode="before", check_fields=False)
    @classmethod
    def empty_list(cls, v):
        """Return None instead of []"""
        return None if v == [] else v


class BenzingaWorldNewsFetcher(
    Fetcher[
        BenzingaWorldNewsQueryParams,
        List[BenzingaWorldNewsData],
    ]
):
    """Transform the query, extract and transform the data from the Benzinga endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BenzingaWorldNewsQueryParams:
        """Transform the query parameters."""
        return BenzingaWorldNewsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: BenzingaWorldNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import math
        from openbb_core.provider.utils.helpers import amake_request, get_querystring
        from openbb_benzinga.utils.helpers import response_callback

        token = credentials.get("benzinga_api_key") if credentials else ""
        base_url = "https://api.benzinga.com/api/v2/news"

        query = query.model_copy(update={"sort": f"{query.sort}:{query.order}"})
        querystring = get_querystring(query.model_dump(by_alias=True), ["order"])

        pages = math.ceil(query.limit / 100)

        urls = [
            f"{base_url}?{querystring}&page={page}&token={token}"
            for page in range(pages)
        ]

        results: list = []

        async def get_one(url):
            """Get data for one url."""
            try:
                response = await amake_request(
                    url, response_callback=response_callback, **kwargs
                )
                if response:
                    results.extend(response)
            except (OpenBBError, UnauthorizedError) as e:
                raise e from e

        await asyncio.gather(*[get_one(url) for url in urls])

        if not results:
            raise EmptyDataError("The request was returned empty.")

        return sorted(
            results, key=lambda x: x.get("created"), reverse=query.order == "desc"
        )[: query.limit if query.limit else len(results)]

    @staticmethod
    def transform_data(
        query: BenzingaWorldNewsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[BenzingaWorldNewsData]:
        """Transform the data."""
        return [BenzingaWorldNewsData.model_validate(item) for item in data]
