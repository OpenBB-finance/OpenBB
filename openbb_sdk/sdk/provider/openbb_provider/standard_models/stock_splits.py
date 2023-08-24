"""Stock Split Calendar data model."""


from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class StockSplitCalendarQueryParams(QueryParams):
    """Stock Split Calendar query model."""

    start_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )


class StockSplitCalendarData(Data):
    """Stock Split Calendar data."""

    date: dateType = Field(description="Date of the stock splits.")
    label: str = Field(description="Label of the stock splits.")
    symbol: str = Field(description="Symbol of the company.")
    numerator: float = Field(description="Numerator of the stock splits.")
    denominator: float = Field(description="Denominator of the stock splits.")
