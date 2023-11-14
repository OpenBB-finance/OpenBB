"""Tiingo Company News."""

import json
from typing import Any, Dict, List, Optional, Union

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)
from openbb_provider.utils.helpers import make_request
from pydantic import Field


class TiingoCompanyNewsQueryParams(CompanyNewsQueryParams):
    """tiingo Company News query.

    Source: https://www.tiingo.com/documentation/news
    """

    __alias_dict__ = {"symbols": "tickers"}
    domains: Optional[str] = Field(
        default=None, description="A comma-separated list of the domains requested."
    )


class TiingoCompanyNewsData(CompanyNewsData):
    """Tiingo Company News data."""

    __alias_dict__ = {
        "date": "publishedDate",
        "site": "source",
        "symbol": "tickers",
        "crawl_date": "crawlDate",
        "article_id": "id",
    }

    symbol: str = Field(description="Ticker tagged in the fetched news.")
    site: str = Field(description="Name of the news source.")
    article_id: int = Field(description="Unique ID of the news article.")
    tags: str = Field(description="Tags associated with the news article.")
    crawl_date: str = Field(description="Date the news article was crawled.")
    description: Optional[str] = Field(description="Description of the news article.")


class TiingoCompanyNewsFetcher(
    Fetcher[
        TiingoCompanyNewsQueryParams,
        List[TiingoCompanyNewsData],
    ]
):
    """Transform the query, extract and transform the data from the tiingo endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TiingoCompanyNewsQueryParams:
        """Transform the query params."""
        return TiingoCompanyNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TiingoCompanyNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the tiingo endpoint."""
        api_key = credentials.get("tiingo_token") if credentials else ""

        base_url = "https://api.tiingo.com/tiingo/news?"
        url = base_url + f"tickers={query.symbols}&token={api_key}"
        if query.domains:
            url += f"&source={query.domains}"

        request = make_request(url)
        request.raise_for_status()
        return request.json()

    @staticmethod
    def transform_data(
        query: TiingoCompanyNewsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TiingoCompanyNewsData]:
        """Return the transformed data."""
        transformed_data = []
        for d in data[::-1]:
            for key, value in d.items():
                if isinstance(value, list):
                    d[key] = json.dumps(value)
            transformed_data.append(TiingoCompanyNewsData.model_validate(d))
        return transformed_data
