"""DeFiLlama TVL Chains model"""

from typing import Any, Dict, List, Optional

from defillama import tvl
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class DeFiLlamaTvlChainsQueryParams(QueryParams):
    """DeFiLlama TVL Chains Query Parameters"""

    pass


class DeFiLlamaTvlChainsData(Data):
    """DeFiLlama TVL Chains Data"""

    gecko_id: Optional[str] = Field(
        default=None, description="CoinGecko ID of the chain"
    )
    tvl: float = Field(description="Current TVL in the chain")
    token_symbol: Optional[str] = Field(
        default=None, description="Chain symbol (e.g. ETH)", alias="tokenSymbol"
    )
    cmc_id: Optional[str] = Field(
        default=None, description="CoinMarketCap ID of the chain", alias="cmcId"
    )
    name: str = Field(description="Given name of the chain")
    chain_id: Optional[int] = Field(
        default=None, description="DeFillama ID of the chain", alias="chainId"
    )


class DeFiLlamaTvlChainsFetcher(
    Fetcher[DeFiLlamaTvlChainsQueryParams, List[DeFiLlamaTvlChainsData]]
):
    """Fetcher for DeFiLlama TVL Chains data"""

    @staticmethod
    def transform_query(params: DeFiLlamaTvlChainsQueryParams) -> Dict[str, Any]:
        """Transform query parameters"""
        return DeFiLlamaTvlChainsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaTvlChainsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Extract data from DeFiLlama API"""
        return tvl.get_chains()

    @staticmethod
    def transform_data(
        query: DeFiLlamaTvlChainsQueryParams, data: List[Dict[str, Any]], **kwargs: Any
    ) -> List[DeFiLlamaTvlChainsData]:
        """Transform the data into the desired format"""
        return [DeFiLlamaTvlChainsData.model_validate(d) for d in data]
