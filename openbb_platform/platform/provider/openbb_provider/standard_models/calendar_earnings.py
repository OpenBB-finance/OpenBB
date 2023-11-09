"""Earnings calendar data model."""


from datetime import date as dateType
from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class CalendarEarningsQueryParams(QueryParams):
    """Earnings calendar rating Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    limit: Optional[int] = Field(
        default=50, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class CalendarEarningsData(Data):
    """Earnings calendar Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    eps: Optional[float] = Field(
        default=None, description="EPS of the earnings calendar."
    )
    eps_estimated: Optional[float] = Field(
        default=None, description="Estimated EPS of the earnings calendar."
    )
    time: str = Field(description="Time of the earnings calendar.")
    revenue: Optional[float] = Field(
        default=None, description="Revenue of the earnings calendar."
    )
    revenue_estimated: Optional[float] = Field(
        default=None, description="Estimated revenue of the earnings calendar."
    )
    updated_from_date: dateType = Field(
        default=None, description="Updated from date of the earnings calendar."
    )
    fiscal_date_ending: dateType = Field(
        description="Fiscal date ending of the earnings calendar."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
