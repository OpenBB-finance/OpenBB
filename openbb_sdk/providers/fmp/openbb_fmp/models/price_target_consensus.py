"""FMP Price Target Consensus fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.price_target_consensus import (
    PriceTargetConsensusData,
    PriceTargetConsensusQueryParams,
)

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPPriceTargetConsensusQueryParams(PriceTargetConsensusQueryParams):
    """FMP Price Target Consensus Query.

    Source: https://site.financialmodelingprep.com/developer/docs/price-target-consensus-api/
    """


class FMPPriceTargetConsensusData(PriceTargetConsensusData):
    """FMP Price Target Consensus Data."""

    class Config:
        fields = {
            "target_high": "targetHigh",
            "target_low": "targetLow",
            "target_consensus": "targetConsensus",
            "target_median": "targetMedian",
        }


class FMPPriceTargetConsensusFetcher(
    Fetcher[
        PriceTargetConsensusQueryParams,
        PriceTargetConsensusData,
        FMPPriceTargetConsensusQueryParams,
        FMPPriceTargetConsensusData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPPriceTargetConsensusQueryParams:
        return FMPPriceTargetConsensusQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPPriceTargetConsensusQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPPriceTargetConsensusData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "price-target-consensus", api_key, query)
        return get_data_many(url, FMPPriceTargetConsensusData)

    @staticmethod
    def transform_data(
        data: List[FMPPriceTargetConsensusData],
    ) -> List[FMPPriceTargetConsensusData]:
        return data
