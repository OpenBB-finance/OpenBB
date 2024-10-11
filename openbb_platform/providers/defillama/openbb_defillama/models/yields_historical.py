"""Crypto Yields Historical Price Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional

from defillama import yields
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class DeFiLlamaYieldsHistoricalQueryParams(QueryParams):
    """DeFiLlama Yields Historical Price Query."""

    pool_id: str = Field(description="The pool id to get data for.")


class DeFiLlamaYieldsHistoricalData(Data):
    """DeFiLlama Yields Historical Price Data."""

    date: datetime = Field(description="The timestamp of the data.", alias="timestamp")
    tvl_usd: float = Field(description="The TVL of the pool in USD.", alias="tvlUsd")
    apy: float = Field(description="The APY of the pool.")
    apy_base: float = Field(description="The base APY of the pool.", alias="apyBase")
    apy_reward: Optional[float] = Field(
        default=None, description="The reward APY of the pool.", alias="apyReward"
    )
    il_7d: Optional[float] = Field(
        default=None, description="The 7-day illiquidity of the pool.", alias="il7d"
    )
    apy_base7d: Optional[float] = Field(
        default=None, description="The 7-day base APY of the pool.", alias="apyBase7d"
    )


class DeFiLlamaYieldsHistoricalFetcher(
    Fetcher[
        DeFiLlamaYieldsHistoricalQueryParams,
        List[DeFiLlamaYieldsHistoricalData],
    ]
):
    """DeFiLlama Yields Historical Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> DeFiLlamaYieldsHistoricalQueryParams:
        """Transform the query params."""

        return DeFiLlamaYieldsHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaYieldsHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract raw data from the Polygon endpoint."""

        return yields.get_pool_chart(query.pool_id)

    @staticmethod
    def transform_data(
        query: DeFiLlamaYieldsHistoricalQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[DeFiLlamaYieldsHistoricalData]:
        """Transform the data."""
        return [DeFiLlamaYieldsHistoricalData.model_validate(d) for d in data]
