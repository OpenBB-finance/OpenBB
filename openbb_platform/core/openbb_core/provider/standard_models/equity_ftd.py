"""Equity FTD Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class EquityFtdQueryParams(QueryParams):
    """Equity FTD Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """Convert field to uppercase."""
        return v.upper()


class EquityFtdData(Data):
    """Equity FTD Data."""

    settlement_date: Optional[dateType] = Field(
        description="The settlement date of the fail.", default=None
    )
    symbol: Optional[str] = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
        default=None,
    )
    cusip: Optional[str] = Field(
        description="CUSIP of the Security.",
        default=None,
    )
    quantity: Optional[int] = Field(
        description="The number of fails on that settlement date.",
        default=None,
    )
    price: Optional[float] = Field(
        description="The price at the previous closing price from the settlement date.",
        default=None,
    )
    description: Optional[str] = Field(
        description="The description of the Security.",
        default=None,
    )

    @field_validator("settlement_date", mode="before")
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strftime(v, "%Y-%m-%d")
