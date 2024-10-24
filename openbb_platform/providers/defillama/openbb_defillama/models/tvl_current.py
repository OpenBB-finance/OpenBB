"""DeFiLlama TVL Current model"""

from typing import Any, Dict, List, Optional

from defillama import tvl
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field


class DeFiLlamaTvlCurrentQueryParams(QueryParams):
    """DeFiLlama TVL Current Query Parameters.

    Source: https://defillama.com/docs/api
    """

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "") + " Should be a protocol."
    )


class DeFiLlamaTvlCurrentData(Data):
    """DeFiLlama TVL Current Data."""

    protocol: str = Field(description="Protocol name")
    tvl: float = Field(description="Current TVL in USD")


class DeFiLlamaTvlCurrentFetcher(
    Fetcher[DeFiLlamaTvlCurrentQueryParams, List[DeFiLlamaTvlCurrentData]]
):
    """DeFiLlama TVL Current Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> DeFiLlamaTvlCurrentQueryParams:
        """Transform query parameters."""
        return DeFiLlamaTvlCurrentQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaTvlCurrentQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Extract data from DeFiLlama API."""
        if current_tvl := tvl.get_protocol_tvl(query.symbol):
            return {"protocol": query.symbol, "tvl": current_tvl}
        else:
            return {}

    @staticmethod
    def transform_data(
        query: DeFiLlamaTvlCurrentQueryParams, data: Dict[str, Any], **kwargs: Any
    ) -> DeFiLlamaTvlCurrentData:
        """Transform the data into the desired format."""
        return DeFiLlamaTvlCurrentData.model_validate(data)
