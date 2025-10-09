"""Price Target Consensus Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class PriceTargetConsensusQueryParams(QueryParams):
    """Price Target Consensus Query."""

    symbol: str | None = Field(
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
    name: str | None = Field(default=None, description="The company name")
    target_high: float | None = Field(
        default=None, description="High target of the price target consensus."
    )
    target_low: float | None = Field(
        default=None, description="Low target of the price target consensus."
    )
    target_consensus: float | None = Field(
        default=None, description="Consensus target of the price target consensus."
    )
    target_median: float | None = Field(
        default=None, description="Median target of the price target consensus."
    )
