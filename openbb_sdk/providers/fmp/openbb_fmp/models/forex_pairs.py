"""FMP Forex available pairs fetcher."""


from typing import Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.forex_pairs import ForexPairsData, ForexPairsQueryParams
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
        ForexPairsQueryParams,
        ForexPairsData,
        FMPForexPairsQueryParams,
        FMPForexPairsData,
    ]
):
    @staticmethod
    def transform_query(
        query: ForexPairsQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPForexPairsQueryParams:
        return FMPForexPairsQueryParams()

    @staticmethod
    def extract_data(
        query: FMPForexPairsQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPForexPairsData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/symbol/available-forex-currency-pairs?apikey={api_key}"

        return get_data_many(url, FMPForexPairsData)

    @staticmethod
    def transform_data(data: List[FMPForexPairsData]) -> List[ForexPairsData]:
        return data_transformer(data, ForexPairsData)
