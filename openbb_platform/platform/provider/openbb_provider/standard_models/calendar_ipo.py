"""IPO Calendar  data model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class CalendarIpoQueryParams(QueryParams):
    """IPO Calendar Query Params."""

    symbol: Optional[str] = Field(
        description="Return IPOs with the given ticker (typically the IPO for the company).",
        default=None,
    )
    start_date: Optional[dateType] = Field(
        description="Return IPOs on or after the given date.",
        default=None,
    )
    end_date: Optional[dateType] = Field(
        description="Return IPOs on or before the given date.", default=None
    )
    limit: Optional[int] = Field(
        description="Limit the number of results returned by most recent.",
        default=300,
    )

    @field_validator("symbol", mode="before", check_fields=False)
    def upper_symbol(cls, v: str):
        """Convert symbol to uppercase."""
        return v.upper() if v else None

    @field_validator("start_date", mode="before", check_fields=False)
    def start_date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strftime(v, "%Y-%m-%d") if v else None

    @field_validator("end_date", mode="before", check_fields=False)
    def end_date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strftime(v, "%Y-%m-%d") if v else None


class CalendarIpoData(Data):
    """IPO Calendar Data."""

    date: Optional[dateType] = Field(
        description="The date of the IPO, when the stock first trades on a major exchange.",
        default=None,
    )
    symbol: Optional[str] = Field(
        description="The ticker under which the Company will be traded after the IPO takes place.",
        default=None,
        alias="ticker",
    )

    @field_validator("date", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None
