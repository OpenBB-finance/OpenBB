"""FMP Global News fetcher."""

from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.global_news import (
    GlobalNewsData,
    GlobalNewsQueryParams,
)
from pydantic import Field

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPGlobalNewsQueryParams(GlobalNewsQueryParams):
    """FMP Global News query.

    Source: https://site.financialmodelingprep.com/developer/docs/general-news-api/
    """


class FMPGlobalNewsData(GlobalNewsData):
    """FMP Global News Data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {"date": "publishedDate"}

    site: str = Field(description="Site of the news.")


class FMPGlobalNewsFetcher(
    Fetcher[
        FMPGlobalNewsQueryParams,
        List[FMPGlobalNewsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPGlobalNewsQueryParams:
        """Transform the query params."""
        return FMPGlobalNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPGlobalNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "general_news", api_key, query)

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPGlobalNewsData]:
        """Return the transformed data."""
        return [FMPGlobalNewsData(**d) for d in data]
