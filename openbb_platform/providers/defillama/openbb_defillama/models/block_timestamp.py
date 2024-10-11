"""DeFiLlama Block Timestamp Model."""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import Field, field_validator
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.abstract.fetcher import Fetcher
from defillama import coins


class DeFiLlamaBlockTimestampQueryParams(QueryParams):
    """DeFiLlama Block Timestamp Query."""

    chain: str = Field(description="The chain to fetch the block timestamp for.")
    timestamp: Union[int, str, datetime] = Field(
        description="The timestamp to fetch the block for. If a string is provided, it should follow the 'day-first' format."
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


class DeFiLlamaBlockTimestampData(Data):
    """DeFiLlama Block Timestamp Data."""

    height: int = Field(description="The block number.")
    timestamp: datetime = Field(description="The timestamp of the block.")


class DeFiLlamaBlockTimestampFetcher(
    Fetcher[DeFiLlamaBlockTimestampQueryParams, List[DeFiLlamaBlockTimestampData]]
):
    """Fetcher for DeFiLlama Block Timestampq data"""

    @staticmethod
    def transform_query(params: DeFiLlamaBlockTimestampQueryParams) -> Dict[str, Any]:
        """Transform query parameters"""
        return DeFiLlamaBlockTimestampQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeFiLlamaBlockTimestampQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Extract data from DeFiLlama API"""
        return coins.get_nearest_block(
            chain=query.chain,
            timestamp=query.timestamp,
        )

    @staticmethod
    def transform_data(
        query: DeFiLlamaBlockTimestampQueryParams, data: Dict[str, Any], **kwargs: Any
    ) -> DeFiLlamaBlockTimestampData:
        """Transform the data into the desired format"""
        return DeFiLlamaBlockTimestampData.model_validate(data)
