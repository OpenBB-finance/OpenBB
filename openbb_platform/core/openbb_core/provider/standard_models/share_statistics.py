"""Share Statistics Standard Model."""

from datetime import date as dateType
from typing import List, Optional, Set, Union

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class ShareStatisticsQueryParams(QueryParams):
    """Share Statistics Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class ShareStatisticsData(Data):
    """Share Statistics Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    date: Optional[dateType] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    free_float: Optional[float] = Field(
        default=None,
        description="Percentage of unrestricted shares of a publicly-traded company.",
    )
    float_shares: Optional[float] = Field(
        default=None,
        description="Number of shares available for trading by the general public.",
    )
    outstanding_shares: Optional[float] = Field(
        default=None, description="Total number of shares of a publicly-traded company."
    )
    source: Optional[str] = Field(
        default=None, description="Source of the received data."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: Union[str, List[str], Set[str]]):
        """Convert field to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
