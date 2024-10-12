"""DeFiLlama Coins Current Model."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from defillama import coins
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class DeFiLlamaCoinsCurrentQueryParams(QueryParams):
    """DeFiLlama Coins Current Query."""

    token: str = Field(
        description="Token to fetch data for. Must be in chain:address format."
    )
    search_width: str = Field(
        default="6h",
        description="Time range to get the current price for. Acceptable format: <int>W, <int>D, <int>H, or <int>M (case insensitive).",
    )

    @field_validator("search_width", mode="before")
    def validate_search_width(cls, v):
        pattern = re.compile(r"^(\d+)[WwDdHhMm]$")
        if not pattern.match(v):
            raise ValueError(
                "search_width must be in the format <int>W, <int>D, <int>H, or <int>M (case insensitive)"
            )
        return v.lower()


class DeFiLlamaCoinsCurrentData(Data):
    """DeFiLlama Coins Current Data."""

    chain: str = Field(description="The chain the token is on.")
    address: str = Field(description="The address of the token.")
    price: float = Field(description="The current price of the token.")
    symbol: str = Field(description="The token symbol.")
    timestamp: datetime = Field(description="The timestamp of the data.")
    confidence: float = Field(description="The confidence of the data.")

    @field_validator("symbol", mode="before")
    def validate_symbol(cls, v):
        return v.upper()

    @field_validator("timestamp", mode="before")
    def validate_timestamp(cls, v):
        return datetime.fromtimestamp(v)


class DeFiLlamaCoinsCurrentFetcher(
    Fetcher[DeFiLlamaCoinsCurrentQueryParams, List[DeFiLlamaCoinsCurrentData]]
):
    """Fetcher for DeFiLlama Coins Current data"""

    @staticmethod
    def transform_query(params: DeFiLlamaCoinsCurrentQueryParams) -> Dict[str, Any]:
        """Transform query parameters"""
        return DeFiLlamaCoinsCurrentQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaCoinsCurrentQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Extract data from DeFiLlama API"""
        token = [{query.token.split(":")[0]: query.token.split(":")[1]}]

        return coins.get_current_prices(
            tokens=token,
            search_width=query.search_width,
        )

    @staticmethod
    def transform_data(
        query: DeFiLlamaCoinsCurrentQueryParams, data: Dict[str, Any], **kwargs: Any
    ) -> List[DeFiLlamaCoinsCurrentData]:
        """Transform the data into the desired format"""
        transformed_data: List[Dict[str, Any]] = []

        transformed_data = [
            {
                "chain": k.split(":")[0],
                "address": k.split(":")[1],
                "price": v["price"],
                "symbol": v["symbol"],
                "timestamp": v["timestamp"],
                "confidence": v["confidence"],
            }
            for k, v in data.items()
        ]

        return [DeFiLlamaCoinsCurrentData.model_validate(d) for d in transformed_data]
