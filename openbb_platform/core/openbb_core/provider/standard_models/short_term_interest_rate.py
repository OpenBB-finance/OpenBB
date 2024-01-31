"""Short Term Interest Rates Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class STIRQueryParams(QueryParams):
    """Short Term Interest Rates Query."""

    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class STIRData(Data):
    """Short Term Interest Rates Data."""

    date: Optional[dateType] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date")
    )
    rate: Optional[float] = Field(
        default=None,
        description="Interest rate, as a normalized percent. (e.g. 0.0001 == 0.01%)",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    country: Optional[str] = Field(
        default=None,
        description="Country for which interest rate is given",
    )
