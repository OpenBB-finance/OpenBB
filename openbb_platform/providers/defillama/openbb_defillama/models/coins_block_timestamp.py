"""DeFiLlama Coins Block Timestamp Model."""

from datetime import datetime
from typing import Any, Dict, Optional, Union

from defillama import coins
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class DeFiLlamaCoinsBlockTimestampQueryParams(QueryParams):
    """DeFiLlama Coins Block Timestamp Query.

    Source: https://defillama.com/docs/api
    """

    chain: str = Field(description="The chain to fetch the block timestamp for.")
    timestamp: Union[int, str, datetime] = Field(
        description="The timestamp to fetch the block for. If a string is provided, it should follow the 'day-first' format."  # noqa: E501
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


class DeFiLlamaCoinsBlockTimestampData(Data):
    """DeFiLlama Coins Block Timestamp Data."""

    height: int = Field(description="The block number.")
    timestamp: datetime = Field(description="The timestamp of the block.")


class DeFiLlamaCoinsBlockTimestampFetcher(
    Fetcher[DeFiLlamaCoinsBlockTimestampQueryParams, DeFiLlamaCoinsBlockTimestampData]
):
    """DeFiLlama Coins Block Timestamp Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> DeFiLlamaCoinsBlockTimestampQueryParams:
        """Transform query parameters"""
        return DeFiLlamaCoinsBlockTimestampQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaCoinsBlockTimestampQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Extract data from DeFiLlama API."""
        return coins.get_nearest_block(
            chain=query.chain,
            timestamp=query.timestamp,
        )

    @staticmethod
    def transform_data(
        query: DeFiLlamaCoinsBlockTimestampQueryParams,
        data: Dict[str, Any],
        **kwargs: Any,
    ) -> DeFiLlamaCoinsBlockTimestampData:
        """Transform the data into the desired format."""
        return DeFiLlamaCoinsBlockTimestampData.model_validate(data)
