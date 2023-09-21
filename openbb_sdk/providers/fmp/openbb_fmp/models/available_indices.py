"""FMP Available Indices fetcher."""


from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.available_indices import (
    AvailableIndicesData,
    AvailableIndicesQueryParams,
)
from pydantic import Field


class FMPAvailableIndicesQueryParams(AvailableIndicesQueryParams):
    """FMP Available Indices Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-stock-index-prices
    """


class FMPAvailableIndicesData(AvailableIndicesData):
    """FMP Available Indices Data."""

    class Config:
        """Pydantic alias config using fields Dict."""

    stock_exchange: str = Field(
        description="Stock exchange where the index is listed.", alias="stockExchange"
    )
    exchange_short_name: str = Field(
        description="Short name of the stock exchange where the index is listed.",
        alias="exchangeShortName",
    )


class FMPAvailableIndicesFetcher(
    Fetcher[
        FMPAvailableIndicesQueryParams,
        List[FMPAvailableIndicesData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPAvailableIndicesQueryParams:
        """Transform the query params."""
        return FMPAvailableIndicesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPAvailableIndicesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/symbol/available-indexes?apikey={api_key}"

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPAvailableIndicesData]:
        """Return the transformed data."""
        return [FMPAvailableIndicesData.parse_obj(d) for d in data]
