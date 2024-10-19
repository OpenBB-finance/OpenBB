"""DeFiLlama Stablecoins Current Model."""

from typing import Any, Dict, List, Optional

from defillama import stablecoins
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class DeFiLlamaStablecoinsCurrentQueryParams(QueryParams):
    """DeFiLlama Stablecoins Current Query."""

    pass


class DeFiLlamaStablecoinsCurrentData(Data):
    """DeFiLlama Stablecoins Current Data."""

    gecko_id: Optional[str] = Field(description="CoinGecko ID of the stablecoin.")
    total_circulating_usd: Dict[str, float] = Field(
        description="Total circulating USD of the stablecoin.",
        alias="totalCirculatingUSD",
    )
    token_symbol: Optional[str] = Field(
        description="Symbol of the stablecoin.", alias="tokenSymbol"
    )
    name: str = Field(description="Name of the stablecoin.")

    @field_validator("token_symbol", mode="before")
    def validate_token_symbol(cls, v):
        return v.upper() if v else None


class DeFiLlamaStablecoinsCurrentFetcher(
    Fetcher[DeFiLlamaStablecoinsCurrentQueryParams, List[DeFiLlamaStablecoinsCurrentData]]
):
    """Fetcher for DeFiLlama Stablecoins Current data"""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> DeFiLlamaStablecoinsCurrentQueryParams:
        """Transform query parameters"""
        return DeFiLlamaStablecoinsCurrentQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaStablecoinsCurrentQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Fetch data from DeFiLlama"""
        return stablecoins.get_chains()

    @staticmethod
    def transform_data(
        query: DeFiLlamaStablecoinsCurrentQueryParams, data: Dict[str, Any], **kwargs: Any
    ) -> List[DeFiLlamaStablecoinsCurrentData]:
        """Transform the data into the desired format"""
        return [DeFiLlamaStablecoinsCurrentData.model_validate(d) for d in data]
