"""Euro Area Yield Curve Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class EUYieldCurveQueryParams(QueryParams):
    """Euro Area Yield Curve Query."""

    date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("date", "")
    )


class EUYieldCurveData(Data):
    """Euro Area Yield Curve Data."""

    maturity: Optional[float] = Field(description="Maturity, in years.", default=None)
    rate: Optional[float] = Field(
        description="Yield curve rate, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
