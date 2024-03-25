"""Sales Estimates Standard Model."""

from datetime import date as dateType
from typing import List, Literal, Set, Union, Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)


class SalesEstimatesQueryParams(QueryParams):
    """Sales Estimates Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    fiscal_year: Optional[int] = Field(
        default=None,
        description="Only for the given fiscal year."
    )
    fiscal_period: Optional[Literal["Q1TTM", "Q2TTM", "Q3TTM", "FY", "Q1", "Q2", "Q3", "Q4", "Q2YTD", "Q3YTD"]] = Field(
        default=None,
        description="The fiscal period"
    )
    calendar_year: Optional[int] = Field(
        default=None,
        description="Only for the given calendar year."
    )
    calendar_period: Optional[Literal["Q1TTM", "Q2TTM", "Q3TTM", "FY", "Q1", "Q2", "Q3", "Q4", "Q2YTD", "Q3YTD"]] = Field(
        default=None,
        description="The calendar period"
    )
    next_page: Optional[int] = Field(
        default=None,
        description="Gets the next page of data from a previous API call."
    )
    page_size: Optional[int] = Field(
        default=None,
        description="The number of results to return."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: str) -> str:
        """Convert symbol to uppercase."""
        return v.upper()


class SalesEstimatesData(Data):
    """Sales Estimates data."""
    estimates: List[float] = Field(description="Zacks Sales estimate data for a given date range.")
    date: Union[date, str] = Field(description="The period end date.")
    fiscal_year: Optional[int] = Field(
        default=None,
        description="The company's fiscal year for the reported period."
    )
    fiscal_period: Optional[str] = Field(
        default=None,
        description="The company's fiscal quarter for the reported period."
    )
    calendar_year: Optional[int] = Field(
        default=None,
        description="The closest calendar year for the company's fiscal year."
    )
    calendar_period: Optional[str] = Field(
        default=None,
        description="The closest calendar quarter for the company's fiscal year."
    )
    count: Optional[int] = Field(
        default=None,
        description="The number of estimates for the period."
    )
    mean: Optional[float] = Field(
        default=None,
        description="The sales estimate mean estimate for the period."
    )
    median: Optional[float] = Field(
        default=None,
        description="The sales estimate median estimate for the period."
    )
    high: Optional[float] = Field(
        default=None,
        description="The sales estimate high estimate for the period."
    )
    low: Optional[float] = Field(
        default=None,
        description="The sales estimate low estimate for the period."
    )
    standard_deviation: Optional[float] = Field(
        default=None,
        description="The sales estimate standard deviation estimate for the period."
    )
    analyst_revisions_percent_change_1w: Optional[float] = Field(
        default=None,
        description="The analyst revisions percent change in estimate for the period of 1 week."
    )
    analyst_revisions_up_1w: Optional[float] = Field(
        default=None,
        description="The analyst revisions going up for the period of 1 week."
    )
    analyst_revisions_down_1w: Optional[float] = Field(
        default=None,
        description="The analyst revisions going down for the period of 1 week."
    )
    analyst_revisions_percent_change_1m: Optional[float] = Field(
        default=None,
        description="The analyst revisions percent change in estimate for the period of 1 month."
    )
    analyst_revisions_up_1m: Optional[float] = Field(
        default=None,
        description="The analyst revisions going up for the period of 1 month."
    )
    analyst_revisions_down_1m: Optional[float] = Field(
        default=None,
        description="The analyst revisions going down for the period of 1 month."
    )
    analyst_revisions_percent_change_3m: Optional[float] = Field(
        default=None,
        description="The analyst revisions percent change in estimate for the period of 3 months."
    )
    analyst_revisions_up_3m: Optional[float] = Field(
        default=None,
        description="The analyst revisions going up for the period of 3 months."
    )
    analyst_revisions_down_3m: Optional[float] = Field(
        default=None,
        description="The analyst revisions going down for the period of 3 months."
    )
    next_page: Optional[str] = Field(
        default=None,
        description="The token required to request the next page of the data. If null, no further results are available."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)]) if v else None
