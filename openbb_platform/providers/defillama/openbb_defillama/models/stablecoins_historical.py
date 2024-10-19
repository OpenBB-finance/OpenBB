"""DeFiLlama Stablecoins Historical Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from defillama import stablecoins
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class DeFiLlamaStablecoinsHistoricalQueryParams(QueryParams):
    """DeFiLlama Stablecoins Historical Query."""

    pass


class DeFiLlamaStablecoinsHistoricalData(Data):
    """DeFiLlama Stablecoins Historical Data."""

    date: datetime = Field(description="Date of the data.")
    prices: Dict[str, float] = Field(description="Prices of the stablecoin on each chain.")

    @field_validator("date", mode="before")
    def validate_date(cls, v):
        return datetime.fromtimestamp(v)


class DeFiLlamaStablecoinsHistoricalFetcher(
    Fetcher[
        DeFiLlamaStablecoinsHistoricalQueryParams,
        List[DeFiLlamaStablecoinsHistoricalData],
    ]
):
    """Fetcher for DeFiLlama Stablecoins Historical data"""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> DeFiLlamaStablecoinsHistoricalQueryParams:
        """Transform query parameters"""
        return DeFiLlamaStablecoinsHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaStablecoinsHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Fetch data from DeFiLlama"""
        return stablecoins.get_prices()

    @staticmethod
    def transform_data(
        query: DeFiLlamaStablecoinsHistoricalQueryParams,
        data: Dict[str, Any],
        **kwargs: Any
    ) -> List[DeFiLlamaStablecoinsHistoricalData]:
        """Transform the data into the desired format"""
        return [DeFiLlamaStablecoinsHistoricalData.model_validate(d) for d in data]
