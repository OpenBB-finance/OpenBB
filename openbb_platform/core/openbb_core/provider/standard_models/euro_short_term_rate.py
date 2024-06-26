"""Euro Short Term Rate Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class EuroShortTermRateQueryParams(QueryParams):
    """Euro Short Term Rate Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class EuroShortTermRateData(Data):
    """Euro Short Term Rate Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: float = Field(
        description="Volume-weighted trimmed mean rate.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percentile_25: Optional[float] = Field(
        default=None,
        description="Rate at 25th percentile of volume.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percentile_75: Optional[float] = Field(
        default=None,
        description="Rate at 75th percentile of volume.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume: Optional[float] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("volume", "") + " (Millions of €EUR).",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-frontend_multiply": 1e6,
        },
    )
    transactions: Optional[int] = Field(
        default=None,
        description="Number of transactions.",
    )
    number_of_banks: Optional[int] = Field(
        default=None,
        description="Number of active banks.",
    )
    large_bank_share_of_volume: Optional[float] = Field(
        default=None,
        description="The percent of volume attributable to the 5 largest active banks.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
