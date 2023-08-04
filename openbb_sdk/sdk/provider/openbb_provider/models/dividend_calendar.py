"""Dividend Calendar data model."""


from datetime import date as dateType
from typing import Optional

from pydantic import Field, NonNegativeFloat

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS
from openbb_provider.models.base import BaseSymbol


class DividendCalendarQueryParams(QueryParams):
    """Dividend Calendar Query."""

    start_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class DividendCalendarData(Data, BaseSymbol):
    """Dividend Calendar Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    label: str = Field(description="The date in human readable form in the calendar.")
    adj_dividend: Optional[NonNegativeFloat] = Field(
        description="The adjusted dividend on a date in the calendar.",
    )
    dividend: Optional[NonNegativeFloat] = Field(
        description="The dividend amount in the calendar."
    )
    record_date: Optional[dateType] = Field(
        description="The record date of the dividend in the calendar.",
    )
    payment_date: Optional[dateType] = Field(
        description="The payment date of the dividend in the calendar.",
    )
    declaration_date: Optional[dateType] = Field(
        description="The declaration date of the dividend in the calendar.",
    )
