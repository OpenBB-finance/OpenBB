"""Earnings calendar data model."""


from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class EarningsCalendarQueryParams(QueryParams, BaseSymbol):
    """Earnings calendar rating Query."""

    limit: Optional[int] = Field(
        default=50, description=QUERY_DESCRIPTIONS.get("limit", "")
    )


class EarningsCalendarData(Data, BaseSymbol):
    """Earnings calendar Data."""

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
