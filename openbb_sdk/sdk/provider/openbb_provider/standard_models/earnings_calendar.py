"""Earnings calendar data model."""


from datetime import date as dateType
from typing import List, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class EarningsCalendarQueryParams(QueryParams):
    """Earnings calendar rating Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    limit: Optional[int] = Field(
        default=50, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class EarningsCalendarData(Data):
    """Earnings calendar Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    eps: Optional[float] = Field(description="EPS of the earnings calendar.")
    eps_estimated: Optional[float] = Field(
        description="Estimated EPS of the earnings calendar."
    )
    time: str = Field(description="Time of the earnings calendar.")
    revenue: Optional[int] = Field(description="Revenue of the earnings calendar.")
    revenue_estimated: Optional[int] = Field(
        description="Estimated revenue of the earnings calendar."
    )
    updated_from_date: Optional[dateType] = Field(
        description="Updated from date of the earnings calendar."
    )
    fiscal_date_ending: dateType = Field(
        description="Fiscal date ending of the earnings calendar."
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
