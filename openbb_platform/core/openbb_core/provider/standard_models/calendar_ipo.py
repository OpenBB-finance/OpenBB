"""IPO Calendar Standard Model."""

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


class CalendarIpoQueryParams(QueryParams):
    """IPO Calendar Query."""

    symbol: Optional[str] = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", ""), default=None
    )
    start_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )
    limit: Optional[int] = Field(
        description=QUERY_DESCRIPTIONS.get("limit", ""), default=100
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: str):
        """Convert symbol to uppercase."""
        return v.upper() if v else None

    @field_validator("start_date", mode="before", check_fields=False)
    @classmethod
    def start_date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strftime(v, "%Y-%m-%d") if v else None

    @field_validator("end_date", mode="before", check_fields=False)
    @classmethod
    def end_date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strftime(v, "%Y-%m-%d") if v else None


class CalendarIpoData(Data):
    """IPO Calendar Data."""

    symbol: Optional[str] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    ipo_date: Optional[dateType] = Field(
        description="The date of the IPO, when the stock first trades on a major exchange.",
        default=None,
    )

    @field_validator("ipo_date", mode="before", check_fields=False)
    @classmethod
    def ipo_date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None
