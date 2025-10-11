"""Share Price Index Standard Model."""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class SharePriceIndexQueryParams(QueryParams):
    """Share Price Index Query."""

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country", ""),
        default="united_states",
    )
    frequency: Literal["monthly", "quarter", "annual"] = Field(
        description=QUERY_DESCRIPTIONS.get("frequency", ""),
        default="monthly",
        json_schema_extra={"choices": ["monthly", "quarter", "annual"]},
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class SharePriceIndexData(Data):
    """Share Price Index Data."""

    date: dateType | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date")
    )
    country: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("country", ""),
    )
    value: float | None = Field(
        default=None,
        description="Share price index value.",
    )
