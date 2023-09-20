"""FMP Forex available pairs fetcher."""


from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.forex_pairs import (
    ForexPairsData,
    ForexPairsQueryParams,
)
from pydantic import Field


class FMPForexPairsQueryParams(ForexPairsQueryParams):
    """FMP Forex available pairs Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-Forex-Price
    """


class FMPForexPairsData(ForexPairsData):
    """FMP Forex available pairs Data."""

    symbol: str = Field(description="Symbol of the currency pair.")
    currency: str = Field(description="Base currency of the currency pair.")
    stockExchange: Optional[str] = Field(
        description="Stock exchange of the currency pair.",
        alias="stock_exchange",
    )
    exchange_short_name: Optional[str] = Field(
        description="Short name of the stock exchange of the currency pair.",
        alias="exchange_short_name",
    )


class FMPForexPairsFetcher(
    Fetcher[
        FMPForexPairsQueryParams,
        List[FMPForexPairsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPForexPairsQueryParams:
        """Transform the query params."""
        return FMPForexPairsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPForexPairsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/symbol/available-forex-currency-pairs?apikey={api_key}"

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPForexPairsData]:
        """Return the transformed data."""
        return [FMPForexPairsData.parse_obj(d) for d in data]
