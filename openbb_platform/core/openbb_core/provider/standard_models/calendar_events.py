"""Company Events Calendar Standard Model."""

from datetime import date as dateType
from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class CalendarEventsQueryParams(QueryParams):
    """Company Events Calendar Query."""

    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class CalendarEventsData(Data):
    """Company Events Calendar Data."""

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", "") + " The date of the event."
    )
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
