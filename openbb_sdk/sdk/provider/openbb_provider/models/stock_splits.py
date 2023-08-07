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

    date: dateType = Field(description="The date of the stock splits.")
    label: str = Field(description="The label of the stock splits.")
    symbol: str = Field(description="The symbol of the company.")
    numerator: float = Field(description="The numerator of the stock splits.")
    denominator: float = Field(description="The denominator of the stock splits.")
