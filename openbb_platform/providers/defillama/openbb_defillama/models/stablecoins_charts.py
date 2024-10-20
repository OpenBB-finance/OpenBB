"""DeFiLlama Stablecoins Charts Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from defillama import stablecoins
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class DeFiLlamaStablecoinsChartsQueryParams(QueryParams):
    """DeFiLlama Stablecoins Charts Query."""

    stablecoin: Optional[str] = Field(
        default=None,
        description="Stablecoin to get the mcap of.",
    )
    chain: Optional[str] = Field(
        default=None,
        description="Chain of the stablecoin.",
    )


class DeFiLlamaStablecoinsChartsData(Data):
    """DeFiLlama Stablecoins Charts Data."""

    date: datetime = Field(description="Date of the data.")
    total_circulating: Dict[str, float] = Field(
        description="Total circulating of the stablecoin on each chain.",
        alias="totalCirculating",
    )
    total_circulating_usd: Dict[str, float] = Field(
        description="Total circulating of the stablecoin in USD on each chain.",
        alias="totalCirculatingUSD",
    )
    total_unreleased: Optional[Dict[str, float]] = Field(
        default=None,
        description="Total unreleased amount of the stablecoin on each chain.",
        alias="totalUnreleased",
    )
    total_minted_usd: Optional[Dict[str, float]] = Field(
        default=None,
        description="Total minted amount of the stablecoin in USD on each chain.",
        alias="totalMintedUSD",
    )

    @field_validator("date", mode="before")
    def validate_date(cls, v):
        return datetime.fromtimestamp(int(v))


class DeFiLlamaStablecoinsChartsFetcher(
    Fetcher[
        DeFiLlamaStablecoinsChartsQueryParams,
        List[DeFiLlamaStablecoinsChartsData],
    ]
):
    """Fetcher for DeFiLlama Stablecoins Charts data"""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> DeFiLlamaStablecoinsChartsQueryParams:
        """Transform query parameters"""
        return DeFiLlamaStablecoinsChartsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaStablecoinsChartsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """Fetch data from DeFiLlama"""
        return stablecoins.get_charts(chain=query.chain, stablecoin=query.stablecoin)

    @staticmethod
    def transform_data(
        query: DeFiLlamaStablecoinsChartsQueryParams,
        data: List[Dict[str, Any]],
        **kwargs: Any
    ) -> List[DeFiLlamaStablecoinsChartsData]:
        """Transform the data into the desired format"""
        return [DeFiLlamaStablecoinsChartsData.model_validate(d) for d in data]
