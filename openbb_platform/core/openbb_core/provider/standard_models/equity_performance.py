"""Equity Performance Standard Model."""

from typing import Literal, Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS


class EquityPerformanceQueryParams(QueryParams):
    """Equity Performance Query."""

    sort: Literal["asc", "desc"] = Field(
        default="desc",
        description="Sort order. Possible values: 'asc', 'desc'. Default: 'desc'.",
    )

    @field_validator("sort", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: Optional[str]) -> Optional[str]:
        """Convert field to lowercase."""
        return v.lower() if v else v


class EquityPerformanceData(Data):
    """Equity Performance Data."""

    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    name: str = Field(
        description="Name of the entity.",
    )
    price: float = Field(
        description="Last price.",
    )
    change: float = Field(
        description="Change in price value.",
    )
    percent_change: float = Field(
        description="Percent change.",
    )
    volume: float = Field(
        description=DATA_DESCRIPTIONS.get("volume", ""),
    )
