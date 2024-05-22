"""Yield Curve Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class YieldCurveQueryParams(QueryParams):
    """Yield Curve Query."""

    date: Optional[str] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " By default is the current data.",
    )


class YieldCurveData(Data):
    """Yield Curve Data."""

    date: Optional[dateType] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    maturity: str = Field(description="Maturity length of the security.")
    rate: float = Field(
        description="The yield as a normalized percent (0.05 is 5%)",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
