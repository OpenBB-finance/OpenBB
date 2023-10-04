"""Recent Performance  data model."""

from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class RecentPerformanceQueryParams(QueryParams):
    """Recent Performance Query Params"""

    symbol: str = Field(description="The ticker symbol to fetch.")

    @field_validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class RecentPerformanceData(Data):
    """Recent Performance Data."""

    one_day: Optional[float] = Field(description="One-day return.", default=None)
    one_week: Optional[float] = Field(description="One-week return.", default=None)
    mtd: Optional[float] = Field(description="MTD return.", default=None)
    qtd: Optional[float] = Field(description="QTD return.", default=None)
    ytd: Optional[float] = Field(description="YTD return.", default=None)
    ttm: Optional[float] = Field(description="TTM return.", default=None)
    one_year: Optional[float] = Field(description="One-year return.", default=None)
