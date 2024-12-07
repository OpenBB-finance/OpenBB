"""Calendar Splits Standard Model."""

from datetime import date as dateType
from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class CalendarSplitsQueryParams(QueryParams):
    """Calendar Splits Query."""

    start_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )


class CalendarSplitsData(Data):
    """Calendar Splits Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    label: str = Field(description="Label of the stock splits.")
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    numerator: float = Field(description="Numerator of the stock splits.")
    denominator: float = Field(description="Denominator of the stock splits.")
