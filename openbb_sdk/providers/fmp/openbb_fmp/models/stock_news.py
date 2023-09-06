"""FMP Stock News fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_news import (
    StockNewsData,
    StockNewsQueryParams,
)
from pydantic import Field

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPStockNewsQueryParams(StockNewsQueryParams):
    """FMP Stock News query.

    Source: https://site.financialmodelingprep.com/developer/docs/stock-news-api/
    """

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {"symbols": "tickers"}


class FMPStockNewsData(StockNewsData):
    """FMP Stock News data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {"date": "publishedDate"}

    symbol: str = Field(description="Ticker of the fetched news.")
    image: Optional[str] = Field(description="URL to the image of the news source.")
    site: str = Field(description="Name of the news source.")


class FMPStockNewsFetcher(
    Fetcher[
        FMPStockNewsQueryParams,
        List[FMPStockNewsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPStockNewsQueryParams:
        """Transform the query params."""
        return FMPStockNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPStockNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        url = create_url(3, "stock_news", api_key, query)

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPStockNewsData]:
        """Return the transformed data."""
        return [FMPStockNewsData(**d) for d in data]
