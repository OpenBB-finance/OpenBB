"""Tiingo Company News Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil import parser
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class TiingoCompanyNewsQueryParams(CompanyNewsQueryParams):
    """Tiingo Company News Query.

    Source: https://www.tiingo.com/documentation/news
    """

    __alias_dict__ = {
        "symbol": "tickers",
        "start_date": "startDate",
        "end_date": "endDate",
    }
    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "source": {"multiple_items_allowed": True},
    }

    offset: Optional[int] = Field(
        default=0, description="Page offset, used in conjunction with limit."
    )
    source: Optional[str] = Field(
        default=None, description="A comma-separated list of the domains requested."
    )


class TiingoCompanyNewsData(CompanyNewsData):
    """Tiingo Company News data."""

    __alias_dict__ = {
        "symbols": "tickers",
        "date": "publishedDate",
        "text": "description",
        "article_id": "id",
    }

    tags: Optional[str] = Field(
        default=None, description="Tags associated with the news article."
    )
    article_id: int = Field(description="Unique ID of the news article.")
    source: str = Field(description="News source.")
    crawl_date: datetime = Field(description="Date the news article was crawled.")

    @field_validator("tags", "symbols", mode="before")
    @classmethod
    def list_to_string(cls, v):
        """Convert list to string."""
        return ",".join(v) if v else None

    @field_validator("crawl_date", mode="before")
    @classmethod
    def validate_date(cls, v):
        """Validate the date."""
        return parser.parse(v)


class TiingoCompanyNewsFetcher(
    Fetcher[
        TiingoCompanyNewsQueryParams,
        List[TiingoCompanyNewsData],
    ]
):
    """Transform the query, extract and transform the data from the Tiingo endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TiingoCompanyNewsQueryParams:
        """Transform the query params."""
        return TiingoCompanyNewsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TiingoCompanyNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the tiingo endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import math
        from openbb_core.provider.utils.helpers import get_querystring
        from openbb_tiingo.utils.helpers import get_data

        api_key = credentials.get("tiingo_token") if credentials else ""

        base_url = "https://api.tiingo.com/tiingo/news"
        query_str = get_querystring(
            query.model_dump(by_alias=False), ["limit", "offset"]
        )

        limit = query.limit if query.limit else 1000
        pages = 0
        if limit > 1000:
            pages = math.ceil(limit / 1000)
            limit = 1000
            urls = [
                f"{base_url}?{query_str}&token={api_key}&limit={limit}&offset={page * 1000 if page > 0 else 0}"
                for page in range(0, pages)
            ]
        else:
            urls = [f"{base_url}?{query_str}&token={api_key}&limit={limit}"]

        results: list = []

        async def get_one(url):
            """Get data for one URL and append results to list."""
            response = await get_data(url)
            if isinstance(response, list):
                results.extend(response)
            elif isinstance(response, dict):
                results.append(response)

        await asyncio.gather(*[get_one(url) for url in urls])

        if not results:
            raise EmptyDataError()

        return results

    @staticmethod
    def transform_data(
        query: TiingoCompanyNewsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TiingoCompanyNewsData]:
        """Return the transformed data."""
        return [TiingoCompanyNewsData.model_validate(d) for d in data[: query.limit]]
