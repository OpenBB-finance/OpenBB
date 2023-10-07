"""Earnings Calendar data model."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class EarningsCalendarQueryParams(QueryParams):
    """Earnings Calendar Query."""

    start_date: Optional[dateType] = Field(
        default=None, description="The start date to filter from."
    )
    end_date: Optional[dateType] = Field(
        default=None, description="The end date to filter to."
    )
    date: Optional[dateType] = Field(
        default=None, description="An alias for start/end dates being the same."
    )

    @field_validator("start_date", mode="before", check_fields=False)
    def start_date_validate(cls, v: str):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        try:
            return datetime.strftime(v, "%Y-%m-%d") if v else None
        except TypeError:
            return datetime.strptime(v, "%Y-%m-%d") if v else None

    @field_validator("end_date", mode="before", check_fields=False)
    def end_date_validate(cls, v: str):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        try:
            return datetime.strftime(v, "%Y-%m-%d") if v else None
        except TypeError:
            return datetime.strptime(v, "%Y-%m-%d") if v else None

    @field_validator("date", mode="before", check_fields=False)
    def date_validate(cls, v: str):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        try:
            return datetime.strftime(v, "%Y-%m-%d") if v else None
        except TypeError:
            return datetime.strptime(v, "%Y-%m-%d") if v else None


class EarningsCalendarData(Data):
    """Earnings Calendar Data."""

    date: Optional[dateType] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    announce_time: Optional[str] = Field(
        default=None, description="Time of the earnings announcement."
    )
    eps_actual: Optional[float] = Field(
        default=None, description="Actual EPS from the earnings announcement."
    )
    eps_estimated: Optional[float] = Field(
        default=None, description="Estimated EPS for the earnings announcement."
    )
