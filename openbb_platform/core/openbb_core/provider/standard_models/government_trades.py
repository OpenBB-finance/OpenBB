"""Government Trades Standard Model."""

from datetime import date as dateType
from typing import Literal, Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, NonNegativeInt, field_validator


class GovernmentTradesQueryParams(QueryParams):
    """Government Trades Query."""

    symbol: Optional[str] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("symbol", "")
    )
    chamber: Literal["house", "senate", "all"] = Field(
        description="Government Chamber."
    )
    limit: Optional[NonNegativeInt] = Field(
        default=100, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class GovernmentTradesData(Data):
    """Government Trades data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    transaction_date: dateType = Field(default=None, description="Date of Transaction.")
    representative: Optional[str] = Field(
        default=None, description="Name of Representative."
    )
