"""FMP Available Indices fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.available_indices import (
    AvailableIndicesData,
    AvailableIndicesQueryParams,
)

from openbb_fmp.utils.helpers import get_data_many


class FMPAvailableIndicesQueryParams(AvailableIndicesQueryParams):
    """FMP Available Indices Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-stock-index-prices
    """


class FMPAvailableIndicesData(AvailableIndicesData):
    """FMP Available Indices Data."""

    class Config:
        fields = {
            "stock_exchange": "stockExchange",
            "exchange_short_name": "exchangeShortName",
        }


class FMPAvailableIndicesFetcher(
    Fetcher[
        FMPAvailableIndicesQueryParams,
        List[FMPAvailableIndicesData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPAvailableIndicesQueryParams:
        return FMPAvailableIndicesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPAvailableIndicesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPAvailableIndicesData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/symbol/available-indexes?apikey={api_key}"
        return get_data_many(url, FMPAvailableIndicesData, **kwargs)

    @staticmethod
    def transform_data(
        data: List[FMPAvailableIndicesData],
    ) -> List[FMPAvailableIndicesData]:
        return data
