"""FMP Price Target Consensus Model."""

from typing import Any, Dict, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.price_target_consensus import (
    PriceTargetConsensusData,
    PriceTargetConsensusQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_one


class FMPPriceTargetConsensusQueryParams(PriceTargetConsensusQueryParams):
    """FMP Price Target Consensus Query.

    Source: https://site.financialmodelingprep.com/developer/docs/price-target-consensus-api/
    """


class FMPPriceTargetConsensusData(PriceTargetConsensusData):
    """FMP Price Target Consensus Data."""


class FMPPriceTargetConsensusFetcher(
    Fetcher[
        FMPPriceTargetConsensusQueryParams,
        FMPPriceTargetConsensusData,
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPPriceTargetConsensusQueryParams:
        """Transform the query params."""
        return FMPPriceTargetConsensusQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPPriceTargetConsensusQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "price-target-consensus", api_key, query)

        return get_data_one(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPPriceTargetConsensusQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> FMPPriceTargetConsensusData:
        """Return the transformed data."""
        return FMPPriceTargetConsensusData.model_validate(data)
