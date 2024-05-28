"""CPI Standard Model."""

from datetime import date as dateType
from typing import Literal, Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class ConsumerPriceIndexQueryParams(QueryParams):
    """CPI Query."""

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country"),
        default="united_states",
    )
    transform: Literal["index", "yoy", "period"] = Field(
        description="Transformation of the CPI data. Period represents the change since previous."
        + " Defaults to change from one year ago (yoy).",
        default="yoy",
        json_schema_extra={"choices": ["index", "yoy", "period"]},
    )
    frequency: Literal["annual", "quarter", "monthly"] = Field(
        default="monthly",
        description=QUERY_DESCRIPTIONS.get("frequency"),
        json_schema_extra={"choices": ["annual", "quarter", "monthly"]},
    )
    harmonized: bool = Field(
        default=False, description="If true, returns harmonized data."
    )
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v):
        """Convert country to lower case."""
        return v.replace(" ", "_").lower()


class ConsumerPriceIndexData(Data):
    """CPI data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    country: str = Field(description=DATA_DESCRIPTIONS.get("country"))
    value: float = Field(description="CPI index value or period change.")
