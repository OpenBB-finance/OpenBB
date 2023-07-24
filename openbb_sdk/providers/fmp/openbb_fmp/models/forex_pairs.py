"""FMP Forex available pairs fetcher."""


from typing import Dict, List, Optional

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.forex_pairs import ForexPairsData, ForexPairsQueryParams

from openbb_fmp.utils.helpers import get_data_many


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
        query: FMPForexPairsQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPForexPairsData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/symbol/available-forex-currency-pairs?apikey={api_key}"
        return get_data_many(url, FMPForexPairsData)

    @staticmethod
    def transform_data(data: List[FMPForexPairsData]) -> List[ForexPairsData]:
        return data_transformer(data, ForexPairsData)
