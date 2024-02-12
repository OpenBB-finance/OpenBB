"""Recent Performance Standard Model."""

from typing import Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class RecentPerformanceQueryParams(QueryParams):
    """Recent Performance Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol")
    @classmethod
    def upper_symbol(cls, v: str) -> str:
        """Convert symbol to uppercase."""
        return v.upper()


class RecentPerformanceData(Data):
    """Recent Performance Data."""

    one_day: Optional[float] = Field(description="One-day return.", default=None)
    wtd: Optional[float] = Field(description="Week to date return.", default=None)
    one_week: Optional[float] = Field(description="One-week return.", default=None)
    mtd: Optional[float] = Field(description="Month to date return.", default=None)
    one_month: Optional[float] = Field(description="One-month return.", default=None)
    qtd: Optional[float] = Field(description="Quarter to date return.", default=None)
    three_month: Optional[float] = Field(
        description="Three-month return.", default=None
    )
    six_month: Optional[float] = Field(description="Six-month return.", default=None)
    ytd: Optional[float] = Field(description="Year to date return.", default=None)
    one_year: Optional[float] = Field(description="One-year return.", default=None)
    three_year: Optional[float] = Field(description="Three-year return.", default=None)
    five_year: Optional[float] = Field(description="Five-year return.", default=None)
    ten_year: Optional[float] = Field(description="Ten-year return.", default=None)
    max: Optional[float] = Field(
        description="Return from the beginning of the time series.", default=None
    )
