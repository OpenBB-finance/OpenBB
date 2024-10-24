"""DeFiLlama Coins Historical Model."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from defillama import coins
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class DeFiLlamaCoinsHistoricalQueryParams(QueryParams):
    """DeFiLlama Coins Historical Query.

    Source: https://defillama.com/docs/api
    """

    token: str = Field(description="The token to get historical data for.")
    timestamp: Union[int, str, datetime] = Field(
        description="The timestamp to get historical data for."
    )
    search_width: str = Field(
        default="6h",
        description="Time range to get the current price for. Acceptable format: <int>W, <int>D, <int>H, or <int>M (case insensitive).",  # noqa: E501
    )

    @field_validator("timestamp", mode="before")
    def validate_timestamp(cls, v):
        if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()):
            return int(v)
        elif isinstance(v, str):
            try:
                return int(datetime.fromisoformat(v).timestamp())
            except ValueError as e:
                raise ValueError(f"Invalid timestamp format: {v}") from e
        elif isinstance(v, datetime):
            return int(v.timestamp())
        else:
            raise ValueError(f"Invalid timestamp type: {type(v)}")

    @field_validator("search_width", mode="before")
    def validate_search_width(cls, v):
        pattern = re.compile(r"^(\d+)[WwDdHhMm]$")
        if not pattern.match(v):
            raise ValueError(
                "search_width must be in the format <int>W, <int>D, <int>H, or <int>M (case insensitive)"
            )
        return v.lower()


class DeFiLlamaCoinsHistoricalData(Data):
    """DeFiLlama Coins Historical Data."""

    chain: str = Field(description="The chain the token is on.")
    address: str = Field(description="The address of the token.")
    price: float = Field(description="The price of the token.")
    symbol: str = Field(description="The symbol of the token.")
    timestamp: datetime = Field(description="The timestamp of the data.")
    decimals: Optional[int] = Field(
        default=None,
        description="Smallest unit of the token that can be traded or transferred",
    )

    @field_validator("symbol", mode="before")
    def validate_symbol(cls, v):
        return v.upper()


class DeFiLlamaCoinsHistoricalFetcher(
    Fetcher[DeFiLlamaCoinsHistoricalQueryParams, List[DeFiLlamaCoinsHistoricalData]]
):
    """DeFiLlama Coins Historical Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> DeFiLlamaCoinsHistoricalQueryParams:
        """Transform query parameters."""
        return DeFiLlamaCoinsHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaCoinsHistoricalQueryParams,
        credentials: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Fetch data from DeFiLlama."""
        token = [{query.token.split(":")[0]: query.token.split(":")[1]}]
        return coins.get_historical_prices(
            tokens=token, timestamp=query.timestamp, search_width=query.search_width
        )

    @staticmethod
    def transform_data(
        query: DeFiLlamaCoinsHistoricalQueryParams, data: Dict[str, Any], **kwargs: Any
    ) -> List[DeFiLlamaCoinsHistoricalData]:
        """Transform the data into the desired format."""
        transformed_data: List[Dict[str, Any]] = []

        transformed_data = [
            {
                "chain": k.split(":")[0],
                "address": k.split(":")[1],
                "price": v["price"],
                "symbol": v["symbol"],
                "timestamp": v["timestamp"],
                "decimals": v.get("decimals", None),
            }
            for k, v in data.items()
        ]

        return [
            DeFiLlamaCoinsHistoricalData.model_validate(d) for d in transformed_data
        ]
