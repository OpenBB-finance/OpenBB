"""FMP Price Target Consensus fetcher."""

# IMPORT STANDARD
from enum import Enum
from typing import Dict, List, Optional

from openbb_provider.model.abstract.data import Data

# IMPORT INTERNAL
from openbb_provider.model.data.price_target_consensus import (
    PriceTargetConsensusData,
    PriceTargetConsensusQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer

# IMPORT THIRD-PARTY
from builtin_providers.fmp.helpers import create_url, get_data_many


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

    __name__ = "FMPPriceTargetConsensusQueryParams"


class FMPPriceTargetConsensusData(Data):
    __name__ = "FMPPriceTargetConsensusData"

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
        query: FMPPriceTargetConsensusQueryParams, api_key: str
    ) -> List[FMPPriceTargetConsensusData]:
        url = create_url(4, "price-target-consensus", api_key, query)
        return get_data_many(url, FMPPriceTargetConsensusData)

    @staticmethod
    def transform_data(
        data: List[FMPPriceTargetConsensusData],
    ) -> List[PriceTargetConsensusData]:
        return data_transformer(data, PriceTargetConsensusData)
