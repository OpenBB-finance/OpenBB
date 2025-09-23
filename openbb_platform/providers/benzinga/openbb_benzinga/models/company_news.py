"""Benzinga Company News Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
from pydantic import Field, field_validator


class BenzingaCompanyNewsQueryParams(CompanyNewsQueryParams):
    """Benzinga Company News Query.

    Source: https://docs.benzinga.io/benzinga/newsfeed-v2.html
    """

    __alias_dict__ = {
        "symbol": "tickers",
        "display": "displayOutput",
        "limit": "pageSize",
        "start_date": "dateFrom",
        "end_date": "dateTo",
        "updated_since": "updatedSince",
        "published_since": "publishedSince",
    }
    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

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
    isin: Optional[str] = Field(default=None, description="The company's ISIN.")
    cusip: Optional[str] = Field(default=None, description="The company's CUSIP.")
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


class BenzingaCompanyNewsData(CompanyNewsData):
    """Benzinga Company News Data."""

    __alias_dict__ = {
        "symbols": "stocks",
        "date": "created",
        "excerpt": "teaser",
        "images": "image",
    }

    channels: Optional[str] = Field(
        default=None,
        description="Channels associated with the news.",
    )
    tags: Optional[str] = Field(
        description="Tags associated with the news.",
        default=None,
    )
    updated: Optional[datetime] = Field(
        default=None, description="Updated date of the news."
    )
    id: str = Field(description="Article ID.")
    original_id: Optional[str] = Field(
        default=None, description="Original ID of the news article."
    )

    @field_validator("date", "updated", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%a, %d %b %Y %H:%M:%S %z")

    @field_validator("symbols", "channels", "tags", mode="before", check_fields=False)
    def list_validate(cls, v):  # pylint: disable=E0213
        """Return the list as a string."""
        return ",".join([item.get("name") for item in v if item.get("name")])

    @field_validator("id", "original_id", mode="before", check_fields=False)
    def id_validate(cls, v):  # pylint: disable=E0213
        """Return the id as a string."""
        return str(v) if v else None


class BenzingaCompanyNewsFetcher(
    Fetcher[
        BenzingaCompanyNewsQueryParams,
        List[BenzingaCompanyNewsData],
    ]
):
    """Transform the query, extract and transform the data from the Benzinga endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BenzingaCompanyNewsQueryParams:
        """Transform query params."""
        return BenzingaCompanyNewsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: BenzingaCompanyNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import math
        from openbb_core.provider.utils.helpers import amake_request, get_querystring
        from openbb_benzinga.utils.helpers import response_callback

        token = credentials.get("benzinga_api_key") if credentials else ""
        base_url = "https://api.benzinga.com/api/v2/news"
        query.limit = query.limit if query.limit else 2500
        model = query.model_dump(by_alias=True)
        model["sort"] = (
            f"{query.sort}:{query.order}" if query.sort and query.order else ""
        )
        querystring = get_querystring(model, ["order", "pageSize"])
        page_size = 100 if query.limit and query.limit > 100 else query.limit
        pages = math.ceil(query.limit / page_size) if query.limit else 1
        urls = [
            f"{base_url}?{querystring}&page={page}&pageSize={page_size}&token={token}"
            for page in range(pages)
        ]
        results: list = []

        async def get_one(url):
            """Get data for one url."""
            try:
                response = await amake_request(
                    url,
                    response_callback=response_callback,
                    **kwargs,
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
        query: BenzingaCompanyNewsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[BenzingaCompanyNewsData]:
        """Transform data."""
        return [BenzingaCompanyNewsData.model_validate(item) for item in data]
