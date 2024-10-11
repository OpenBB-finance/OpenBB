"""DefiLlama Yields Pools Model."""

from typing import Any, Dict, List, Optional

from defillama import yields
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class DeFiLlamaYieldsPoolsQueryParams(QueryParams):
    """DefiLlama Yields Pools Query Params."""

    pass


class DeFiLlamaYieldsPoolsData(Data):
    """DefiLlama Yields Pools Data."""

    chain: str = Field(description="Chain of the yield")
    project: str = Field(description="Project of the yield")
    symbol: str = Field(description="Symbol of the yield")
    pool: str = Field(description="Pool of the yield", alias="pool")
    tvl_usd: float = Field(description="TVL of the yield in USD", alias="tvlUsd")
    apy_base: Optional[float] = Field(
        default=None, description="APY Base of the yield", alias="apyBase"
    )
    apy_reward: Optional[float] = Field(
        default=None, description="APY Reward of the yield", alias="apyReward"
    )
    apy: float = Field(description="APY of the yield")
    reward_tokens: Optional[List[str]] = Field(
        default=None, description="Reward tokens of the yield", alias="rewardTokens"
    )
    apy_pct_1d: Optional[float] = Field(
        default=None, description="APY % 1D of the yield", alias="apyPct1D"
    )
    apy_pct_7d: Optional[float] = Field(
        default=None, description="APY % 7D of the yield", alias="apyPct7D"
    )
    apy_pct_30d: Optional[float] = Field(
        default=None, description="APY % 30D of the yield", alias="apyPct30D"
    )
    stablecoin: bool = Field(description="Stablecoin of the yield")
    il_risk: str = Field(description="IL Risk of the yield", alias="ilRisk")
    exposure: str = Field(description="Exposure of the yield")
    predictions: Dict[str, Any] = Field(description="Predictions of the yield")
    pool_meta: Optional[str] = Field(
        default=None, description="Pool metadata of the yield", alias="poolMeta"
    )
    mu: float = Field(description="Mu of the yield")
    sigma: float = Field(description="Sigma of the yield")
    count: int = Field(description="Count of the yield")
    outlier: bool = Field(description="Outlier of the yield")
    underlying_tokens: Optional[List[str]] = Field(
        default=None,
        description="Underlying tokens of the yield",
        alias="underlyingTokens",
    )
    il_7d: Optional[float] = Field(
        default=None, description="IL 7d of the yield", alias="il7d"
    )
    apy_base_7d: Optional[float] = Field(
        default=None, description="APY Base 7d of the yield", alias="apyBase7d"
    )
    apy_mean_30d: Optional[float] = Field(
        default=None, description="APY Mean 30d of the yield", alias="apyMean30d"
    )
    volume_usd_1d: Optional[float] = Field(
        default=None, description="Volume USD 1d of the yield", alias="volumeUsd1d"
    )
    volume_usd_7d: Optional[float] = Field(
        default=None, description="Volume USD 7d of the yield", alias="volumeUsd7d"
    )
    apy_base_inception: Optional[float] = Field(
        default=None,
        description="APY Base Inception of the yield",
        alias="apyBaseInception",
    )

    @field_validator("underlying_tokens", "reward_tokens", mode="before")
    def validate_list(cls, v):
        if isinstance(v, list) and any(item is None for item in v):
            return None
        return v


class DeFiLlamaYieldsPoolsFetcher(
    Fetcher[DeFiLlamaYieldsPoolsQueryParams, List[DeFiLlamaYieldsPoolsData]]
):
    """Fetcher for DeFiLlama Yields Pools data"""

    @staticmethod
    def transform_query(params: DeFiLlamaYieldsPoolsQueryParams) -> Dict[str, Any]:
        """Transform query parameters"""
        return DeFiLlamaYieldsPoolsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaYieldsPoolsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Extract data from DeFiLlama API"""
        if data := yields.get_pools():
            return data

        return {}

    @staticmethod
    def transform_data(
        query: DeFiLlamaYieldsPoolsQueryParams,
        data: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> List[DeFiLlamaYieldsPoolsData]:
        """Transform the data into the desired format"""
        return [DeFiLlamaYieldsPoolsData.model_validate(d) for d in data]
