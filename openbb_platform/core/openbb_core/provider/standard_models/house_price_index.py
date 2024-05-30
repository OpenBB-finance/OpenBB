"""House Price Index Standard Model."""

from datetime import date as dateType
from typing import Literal, Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class HousePriceIndexQueryParams(QueryParams):
    """House Price Index Query."""

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country", ""),
        default="united_states",
    )
    frequency: Literal["monthly", "quarter", "annual"] = Field(
        description=QUERY_DESCRIPTIONS.get("frequency", ""),
        default="quarter",
        json_schema_extra={"choices": ["monthly", "quarter", "annual"]},
    )
    transform: Literal["index", "yoy", "period"] = Field(
        description="Transformation of the CPI data. Period represents the change since previous."
        + " Defaults to change from one year ago (yoy).",
        default="index",
        json_schema_extra={"choices": ["index", "yoy", "period"]},
    )
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class HousePriceIndexData(Data):
    """House Price Index Data."""

    date: Optional[dateType] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date")
    )
    country: Optional[str] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("country", ""),
    )
    value: Optional[float] = Field(
        default=None,
        description="Share price index value.",
    )
