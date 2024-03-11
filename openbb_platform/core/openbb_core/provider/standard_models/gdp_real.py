"""Real GDP Standard Model."""

from datetime import date as dateType
from typing import Literal, Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class GdpRealQueryParams(QueryParams):
    """Real GDP Query."""

    units: Literal["idx", "qoq", "yoy"] = Field(
        default="yoy",
        description=QUERY_DESCRIPTIONS.get("units", "")
        + " Either idx (indicating 2015=100), "
        + "qoq (previous period) "
        + "or yoy (same period, previous year).)",
    )
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )

    @field_validator("units", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: Optional[str]) -> Optional[str]:
        """Convert field to lowercase."""
        return v.lower() if v else v


class GdpRealData(Data):
    """Real GDP Data."""

    date: Optional[dateType] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date")
    )
    value: Optional[float] = Field(
        default=None, description="Nominal GDP value on the date."
    )
