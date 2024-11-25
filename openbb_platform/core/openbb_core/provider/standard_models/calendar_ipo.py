"""IPO Calendar Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

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
