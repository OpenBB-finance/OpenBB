"""FMP Forex available pairs fetcher."""

# IMPORT STANDARD
from typing import Dict, List, Optional

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.forex_pairs import ForexPairsData, ForexPairsQueryParams
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer

from builtin_providers.fmp.helpers import get_data_many


class FMPForexPairsQueryParams(QueryParams):
    """FMP Forex available pairs query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-Forex-Price

    """


class FMPForexPairsData(Data):
    """FMP Forex available pairs data."""


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
        query: FMPForexPairsQueryParams, api_key: str
    ) -> List[FMPForexPairsData]:
        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/symbol/available-forex-currency-pairs?apikey={api_key}"
        return get_data_many(url, FMPForexPairsData)

    @staticmethod
    def transform_data(data: List[FMPForexPairsData]) -> List[ForexPairsData]:
        return data_transformer(data, ForexPairsData)
