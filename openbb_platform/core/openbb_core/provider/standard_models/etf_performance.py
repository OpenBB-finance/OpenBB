"""ETF Performance Standard Model."""

from datetime import date as dateType
from typing import Literal, Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class ETFPerformanceQueryParams(QueryParams):
    """ETF Performance Query."""

    sort: Literal["asc", "desc"] = Field(
        default="desc",
        description="Sort order. Possible values: 'asc', 'desc'. Default: 'desc'.",
    )
    limit: int = Field(
        default=10,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )

    @field_validator("sort", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: Optional[str]) -> Optional[str]:
        """Convert field to lowercase."""
        return v.lower() if v else v


class ETFPerformanceData(Data):
    """ETF Performance Data."""

    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    name: str = Field(
        description="Name of the entity.",
    )
    last_price: float = Field(
        description="Last price.",
    )
    percent_change: float = Field(
        description="Percent change.",
    )
    net_change: float = Field(
        description="Net change.",
    )
    volume: float = Field(
        description=DATA_DESCRIPTIONS.get("volume", ""),
    )
    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
