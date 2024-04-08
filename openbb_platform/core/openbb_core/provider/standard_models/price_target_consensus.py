"""Price Target Consensus Standard Model."""

from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class PriceTargetConsensusQueryParams(QueryParams):
    """Price Target Consensus Query."""

    symbol: Optional[str] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("symbol", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v):
        """Convert field to uppercase."""
        return v.upper() if v else None


class PriceTargetConsensusData(Data):
    """Price Target Consensus Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: Optional[str] = Field(default=None, description="The company name")
    target_high: Optional[float] = Field(
        default=None, description="High target of the price target consensus."
    )
    target_low: Optional[float] = Field(
        default=None, description="Low target of the price target consensus."
    )
    target_consensus: Optional[float] = Field(
        default=None, description="Consensus target of the price target consensus."
    )
    target_median: Optional[float] = Field(
        default=None, description="Median target of the price target consensus."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: Union[str, List[str], Set[str]]):
        """Convert field to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
