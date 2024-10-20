"""DeFiLlama Stablecoins List Model."""

from typing import Any, Dict, List, Optional, Union

from defillama import stablecoins
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class DeFiLlamaStablecoinsListQueryParams(QueryParams):
    """DeFiLlama Stablecoins List Query."""

    include_prices: bool = Field(
        description="Whether to include prices.", default=False
    )


class DeFiLlamaStablecoinsListChainData(Data):
    """DeFiLlama Stablecoins List Chain Data."""

    chain: str = Field(description="Chain of the stablecoin.")
    current: Dict[str, float] = Field(
        description="Current circulating amount of the stablecoin by chain."
    )
    circulating_prev_day: Union[int, Dict[str, float]] = Field(
        default=0,
        description="Circulating amount of the stablecoin the previous day.",
        alias="circulatingPrevDay",
    )
    circulating_prev_week: Union[int, Dict[str, float]] = Field(
        default=0,
        description="Circulating amount of the stablecoin the previous week.",
        alias="circulatingPrevWeek",
    )
    circulating_prev_month: Union[int, Dict[str, float]] = Field(
        default=0,
        description="Circulating amount of the stablecoin the previous month.",
        alias="circulatingPrevMonth",
    )


class DeFiLlamaStablecoinsListData(Data):
    """DeFiLlama Stablecoins List Data."""

    id: str = Field(description="ID of the stablecoin.")
    name: str = Field(description="Name of the stablecoin.")
    symbol: str = Field(description="Symbol of the stablecoin.")
    gecko_id: Optional[str] = Field(
        default=None, description="CoinGecko ID of the stablecoin."
    )
    peg_type: str = Field(description="Peg type of the stablecoin.", alias="pegType")
    peg_mechanism: str = Field(
        description="Peg mechanism of the stablecoin.", alias="pegMechanism"
    )
    price: Optional[float] = Field(default=None, description="Price of the stablecoin.")
    price_source: Optional[str] = Field(
        default=None, description="Price source of the stablecoin.", alias="priceSource"
    )
    circulating: Dict[str, float] = Field(
        description="Circulating amount of the stablecoin."
    )
    circulating_prev_day: Union[int, Dict[str, float]] = Field(
        default=0,
        description="Circulating amount of the stablecoin the previous day.",
        alias="circulatingPrevDay",
    )
    circulating_prev_week: Union[int, Dict[str, float]] = Field(
        default=0,
        description="Circulating amount of the stablecoin the previous week.",
        alias="circulatingPrevWeek",
    )
    circulating_prev_month: Union[int, Dict[str, float]] = Field(
        default=0,
        description="Circulating amount of the stablecoin the previous month.",
        alias="circulatingPrevMonth",
    )
    chain_circulating: List[DeFiLlamaStablecoinsListChainData] = Field(
        description="Circulating amount of the stablecoin by chain.",
        alias="chainCirculating",
    )
    chains: List[str] = Field(description="Chains of the stablecoin.")

    @field_validator("symbol", mode="before")
    def validate_symbol(cls, v):
        return v.upper()

    @field_validator("chain_circulating", mode="before")
    def validate_chain_circulating(cls, v):
        return [DeFiLlamaStablecoinsListChainData.model_validate(chain) for chain in v]


class DeFiLlamaStablecoinsListFetcher(
    Fetcher[DeFiLlamaStablecoinsListQueryParams, List[DeFiLlamaStablecoinsListData]]
):
    """Fetcher for DeFiLlama Stablecoins List data"""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> DeFiLlamaStablecoinsListQueryParams:
        """Transform query parameters"""
        return DeFiLlamaStablecoinsListQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaStablecoinsListQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """Fetch data from DeFiLlama"""
        return stablecoins.get_stablecoins(include_prices=query.include_prices)

    @staticmethod
    def transform_data(
        query: DeFiLlamaStablecoinsListQueryParams,
        data: List[Dict[str, Any]],
        **kwargs: Any
    ) -> List[DeFiLlamaStablecoinsListData]:
        """Transform the data into the desired format"""

        transformed_data: List[Dict[str, Any]] = []

        transformed_data = [
            {
                **item,
                "chainCirculating": [
                    {
                        "chain": k,
                        "current": v["current"],
                        "circulatingPrevDay": v["circulatingPrevDay"],
                        "circulatingPrevWeek": v["circulatingPrevWeek"],
                        "circulatingPrevMonth": v["circulatingPrevMonth"],
                    }
                    for k, v in item["chainCirculating"].items()
                ],
            }
            for item in data
        ]

        return [
            DeFiLlamaStablecoinsListData.model_validate(d) for d in transformed_data
        ]
