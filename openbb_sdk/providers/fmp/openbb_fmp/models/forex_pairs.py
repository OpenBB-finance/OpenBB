"""FMP Forex available pairs fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.forex_pairs import (
    ForexPairsData,
    ForexPairsQueryParams,
)
from pydantic import Field

from openbb_fmp.utils.helpers import get_data_many


class FMPForexPairsQueryParams(ForexPairsQueryParams):
    """FMP Forex available pairs Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-Forex-Price
    """


class FMPForexPairsData(ForexPairsData):
    """FMP Forex available pairs Data."""

    symbol: str = Field(description="The symbol of the currency pair.")
    currency: str = Field(description="The base currency of the currency pair.")
    stockExchange: Optional[str] = Field(
        description="The stock exchange of the currency pair.",
        alias="stock_exchange",
    )
    exchange_short_name: Optional[str] = Field(
        description="The short name of the stock exchange of the currency pair.",
        alias="exchange_short_name",
    )


class FMPForexPairsFetcher(
    Fetcher[
        FMPForexPairsQueryParams,
        List[FMPForexPairsData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPForexPairsQueryParams:
        return FMPForexPairsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPForexPairsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPForexPairsData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/symbol/available-forex-currency-pairs?apikey={api_key}"

        return get_data_many(url, FMPForexPairsData, **kwargs)

    @staticmethod
    def transform_data(data: List[FMPForexPairsData]) -> List[FMPForexPairsData]:
        return data
