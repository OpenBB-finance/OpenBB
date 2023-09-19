"""Share Statistics Data Model."""


from datetime import date as dateType
from typing import List, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class ShareStatisticsQueryParams(QueryParams):
    """Share Statistics Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class ShareStatisticsData(Data):
    """Return Share Statistics Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    date: dateType = Field(description=QUERY_DESCRIPTIONS.get("date", ""))
    free_float: float = Field(
        description="Percentage of unrestricted shares of a publicly-traded company."
    )
    float_shares: float = Field(
        description="Number of shares available for trading by the general public."
    )
    outstanding_shares: float = Field(
        description="Total number of shares of a publicly-traded company."
    )
    source: str = Field(description="Source of the received data.")

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
