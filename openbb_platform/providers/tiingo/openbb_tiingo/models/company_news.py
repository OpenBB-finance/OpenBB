"""Tiingo Company News Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil import parser
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_tiingo.utils.helpers import get_data_many
from pydantic import Field, field_validator


class TiingoCompanyNewsQueryParams(CompanyNewsQueryParams):
    """Tiingo Company News Query.

    Source: https://www.tiingo.com/documentation/news
    """

    __alias_dict__ = {"symbols": "tickers"}

    source: Optional[str] = Field(
        default=None, description="A comma-separated list of the domains requested."
    )


class TiingoCompanyNewsData(CompanyNewsData):
    """Tiingo Company News data."""

    __alias_dict__ = {
        "symbols": "tickers",
        "date": "publishedDate",
        "text": "description",
    }

    article_id: int = Field(description="Unique ID of the news article.", alias="id")
    site: str = Field(description="Name of the news source.", alias="source")
    tags: str = Field(description="Tags associated with the news article.")
    crawl_date: datetime = Field(description="Date the news article was crawled.")

    @field_validator("tags", "symbols", mode="before")
    @classmethod
    def list_to_string(cls, v):
        """Convert list to string."""
        return ",".join(v)

    @field_validator("crawl_date", mode="before")
    @classmethod
    def validate_date(cls, v):
        """Validate the date."""
        return parser.parse(v)

    @field_validator("symbols", mode="after")
    @classmethod
    def symbols_validate(cls, v: str):
        """Convert symbols to upper case."""
        return v.upper()


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
    def extract_data(
        query: TiingoCompanyNewsQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the tiingo endpoint."""
        api_key = credentials.get("tiingo_token") if credentials else ""

        base_url = "https://api.tiingo.com/tiingo/news"
        query_str = get_querystring(query.model_dump(by_alias=True), [])
        url = f"{base_url}?{query_str}&token={api_key}"

        return get_data_many(url)

    @staticmethod
    def transform_data(
        query: TiingoCompanyNewsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TiingoCompanyNewsData]:
        """Return the transformed data."""
        return [TiingoCompanyNewsData.model_validate(d) for d in data]
