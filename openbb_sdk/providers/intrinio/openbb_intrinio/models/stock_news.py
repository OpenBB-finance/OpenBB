"""Intrinio Stock News fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_news import (
    StockNewsData,
    StockNewsQueryParams,
)
from openbb_provider.utils.helpers import get_querystring
from pydantic import Field, validator

from openbb_intrinio.utils.helpers import get_data_many


class IntrinioStockNewsQueryParams(StockNewsQueryParams):
    """Intrinio Stock News query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_news_v2
    """

    __alias_dict__ = {"symbols": "symbols", "page": "next_page", "limit": "page_size"}

    symbols: str = Field(
        description="A Company identifier (Ticker, CIK, LEI, Intrinio ID)."
    )
    next_page: Optional[str] = Field(
        description="Token to get the next page of data from a previous API call."
    )
    # TODO: Add support for all_pages
    all_pages: Optional[bool] = Field(
        default=False,
        description="Returns all pages of data from the API call at once.",
    )


class IntrinioStockNewsData(StockNewsData):
    """Intrinio Stock News data."""

    __alias_dict__ = {"date": "publication_date", "text": "summary"}

    id: str = Field(description="Article ID.")

    @validator("publication_date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.000Z")


class IntrinioStockNewsFetcher(
    Fetcher[
        IntrinioStockNewsQueryParams,
        List[IntrinioStockNewsData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioStockNewsQueryParams:
        """Transform the query params."""

        return IntrinioStockNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: IntrinioStockNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""

        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com"
        query_str = get_querystring(query.dict(by_alias=True), ["symbols", "all_pages"])
        url = f"{base_url}/companies/{query.symbols}/news?{query_str}&api_key={api_key}"

        return get_data_many(url, "news", **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[IntrinioStockNewsData]:
        """Return the transformed data."""

        return [IntrinioStockNewsData(**d) for d in data]
