"""DeFiLlama Coins Change Model."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from defillama import coins
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class DeFiLlamaCoinsChangeQueryParams(QueryParams):
    token: str = Field(description="The token to fetch data for.")
    timestamp: Union[int, str, datetime] = Field(
        description="The timestamp to fetch the block for. If a string is provided, it should follow the 'day-first' format."
    )
    look_forward: bool = Field(
        default=False,
        description="Whether to look after the provided timestamp or not.",
    )
    period: str = Field(
        default="24h",
        description="Time range to get the current price for. Acceptable format: <int>W, <int>D, <int>H, or <int>M (case insensitive).",
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

    @field_validator("period", mode="before")
    def validate_search_width(cls, v):
        pattern = re.compile(r"^(\d+)[WwDdHhMm]$")
        if not pattern.match(v):
            raise ValueError(
                "search_width must be in the format <int>W, <int>D, <int>H, or <int>M (case insensitive)"
            )
        return v.lower()


class DeFiLlamaCoinsChangeData(Data):
    """DeFiLlama Coins Change Data."""

    chain: str = Field(description="The chain the token is on.")
    address: str = Field(description="The address of the token.")
    change: float = Field(description="The percentage change in price.")


class DeFiLlamaCoinsChangeFetcher(
    Fetcher[DeFiLlamaCoinsChangeQueryParams, List[DeFiLlamaCoinsChangeData]]
):
    @staticmethod
    def transform_query(params: DeFiLlamaCoinsChangeQueryParams) -> Dict[str, Any]:
        return DeFiLlamaCoinsChangeQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaCoinsChangeQueryParams,
        credentials: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Fetch data from DeFiLlama."""
        token = [{query.token.split(":")[0]: query.token.split(":")[1]}]
        return coins.get_percentage(
            tokens=token,
            timestamp=query.timestamp,
            look_forward=query.look_forward,
            period=query.period,
        )

    @staticmethod
    def transform_data(
        query: DeFiLlamaCoinsChangeQueryParams, data: Dict[str, Any], **kwargs: Any
    ) -> List[DeFiLlamaCoinsChangeData]:
        """Transform the data into the desired format."""

        transformed_data: List[Dict[str, Any]] = []

        transformed_data = [
            {
                "chain": k.split(":")[0],
                "address": k.split(":")[1],
                "change": v,
            }
            for k, v in data.items()
        ]

        return [DeFiLlamaCoinsChangeData.model_validate(d) for d in transformed_data]
