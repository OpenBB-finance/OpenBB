"""CPI Standard Model."""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class ConsumerPriceIndexQueryParams(QueryParams):
    """CPI Query."""

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country"),
        default="united_states",
    )
    transform: str = Field(
        description="Transformation of the CPI data.",
        default="yoy",
    )
    frequency: Literal["annual", "quarter", "monthly"] = Field(
        default="monthly",
        description=QUERY_DESCRIPTIONS.get("frequency"),
    )
    harmonized: bool = Field(
        default=False, description="If true, returns harmonized data."
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class ConsumerPriceIndexData(Data):
    """CPI data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    country: str = Field(description=DATA_DESCRIPTIONS.get("country"))
    value: float = Field(description="CPI index value or period change.")
