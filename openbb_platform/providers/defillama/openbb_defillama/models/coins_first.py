"""DeFiLlama Coins First Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from defillama import coins
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class DeFiLlamaCoinsFirstQueryParams(QueryParams):
    """DeFiLlama Coins First Query."""

    token: str = Field(
        description="Token to fetch data for. Must be in chain:address format."
    )


class DeFiLlamaCoinsFirstData(Data):
    """DeFiLlama Coins First Data."""

    chain: str = Field(description="The chain the token is on.")
    address: str = Field(description="The address of the token.")
    symbol: str = Field(description="The symbol of the token.")
    price: float = Field(description="The price of the token.")
    timestamp: datetime = Field(description="The timestamp of the first data point.")

    @field_validator("symbol", mode="before")
    def validate_symbol(cls, v):
        return v.upper()

    @field_validator("timestamp", mode="before")
    def validate_timestamp(cls, v):
        return datetime.fromtimestamp(v)


class DeFiLlamaCoinsFirstFetcher(
    Fetcher[DeFiLlamaCoinsFirstQueryParams, List[DeFiLlamaCoinsFirstData]]
):
    """Fetcher for DeFiLlama Coins First data"""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> DeFiLlamaCoinsFirstQueryParams:
        """Transform query parameters"""
        return DeFiLlamaCoinsFirstQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaCoinsFirstQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Fetch data from DeFiLlama"""
        token = [{query.token.split(":")[0]: query.token.split(":")[1]}]
        return coins.get_first_prices(tokens=token)

    @staticmethod
    def transform_data(
        query: DeFiLlamaCoinsFirstQueryParams, data: Dict[str, Any], **kwargs: Any
    ) -> List[DeFiLlamaCoinsFirstData]:
        """Transform the data into the desired format"""

        transformed_data: List[Dict[str, Any]] = []

        transformed_data = [
            {
                "chain": k.split(":")[0],
                "address": k.split(":")[1],
                "price": v["price"],
                "symbol": v["symbol"],
                "timestamp": v["timestamp"],
            }
            for k, v in data.items()
        ]
        return [DeFiLlamaCoinsFirstData.model_validate(d) for d in transformed_data]
