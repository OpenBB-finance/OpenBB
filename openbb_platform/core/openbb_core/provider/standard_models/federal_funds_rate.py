"""Federal Funds Rate Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class FederalFundsRateQueryParams(QueryParams):
    """Federal Funds Rate Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class FederalFundsRateData(Data):
    """Federal Funds Rate Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: float = Field(
        description="Effective federal funds rate.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    target_range_upper: Optional[float] = Field(
        default=None,
        description="Upper bound of the target range.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    target_range_lower: Optional[float] = Field(
        default=None,
        description="Lower bound of the target range.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percentile_1: Optional[float] = Field(
        default=None,
        description="1st percentile of the distribution.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percentile_25: Optional[float] = Field(
        default=None,
        description="25th percentile of the distribution.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percentile_75: Optional[float] = Field(
        default=None,
        description="75th percentile of the distribution.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percentile_99: Optional[float] = Field(
        default=None,
        description="99th percentile of the distribution.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume: Optional[float] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("volume", "")
        + "The notional volume of transactions (Billions of $).",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-frontend_multiply": 1e9,
        },
    )
