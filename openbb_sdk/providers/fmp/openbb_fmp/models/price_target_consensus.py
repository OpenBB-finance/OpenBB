"""FMP Price Target Consensus fetcher."""


from enum import Enum
from typing import Dict, List, Optional

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer


from openbb_provider.models.price_target_consensus import (
    PriceTargetConsensusData,
    PriceTargetConsensusQueryParams,
)

# IMPORT THIRD-PARTY
from openbb_fmp.utils.helpers import create_url, get_data_many


class Interval(str, Enum):
    oneminute = "1min"
    fiveminute = "5min"
    fifteenminute = "15min"
    thirtyminute = "30min"
    onehour = "1hour"
    fourhour = "4hour"
    day = "day"


class FMPPriceTargetConsensusQueryParams(PriceTargetConsensusQueryParams):
    """FMP Price Target Consensus query.

    Source: https://site.financialmodelingprep.com/developer/docs/price-target-consensus-api/

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class FMPPriceTargetConsensusData(Data):
    symbol: str
    targetHigh: float
    targetLow: float
    targetConsensus: float
    targetMedian: float


class FMPPriceTargetConsensusFetcher(
    Fetcher[
        PriceTargetConsensusQueryParams,
        PriceTargetConsensusData,
        FMPPriceTargetConsensusQueryParams,
        FMPPriceTargetConsensusData,
    ]
):
    @staticmethod
    def transform_query(
        query: PriceTargetConsensusQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPPriceTargetConsensusQueryParams:
        return FMPPriceTargetConsensusQueryParams(symbol=query.symbol)

    @staticmethod
    def extract_data(
        query: FMPPriceTargetConsensusQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPPriceTargetConsensusData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        url = create_url(4, "price-target-consensus", api_key, query)
        return get_data_many(url, FMPPriceTargetConsensusData)

    @staticmethod
    def transform_data(
        data: List[FMPPriceTargetConsensusData],
    ) -> List[PriceTargetConsensusData]:
        return data_transformer(data, PriceTargetConsensusData)
