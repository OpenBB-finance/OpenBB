"""Futures Curve Standard Model."""

from datetime import date as dateType
from typing import Optional, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class FuturesCurveQueryParams(QueryParams):
    """Futures Curve Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    date: Optional[Union[dateType, str]] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", ""),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v):
        """Convert field to uppercase."""
        return v.upper()


class FuturesCurveData(Data):
    """Futures Curve Data."""

    date: Optional[dateType] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    expiration: str = Field(description="Futures expiration month.")
    price: float = Field(
        default=None,
        description="The price of the futures contract.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
