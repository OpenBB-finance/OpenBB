"""Treasury Rates Standard Model."""

from datetime import date as dateType
from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class TreasuryRatesQueryParams(QueryParams):
    """Treasury Rates Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class TreasuryRatesData(Data):
    """Treasury Rates Data. All fields are expressed as a normalized percent - 1% = 0.01."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    week_4: Optional[float] = Field(
        default=None,
        description="4 week Treasury bills rate (secondary market).",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    month_1: Optional[float] = Field(
        description="1 month Treasury rate.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    month_2: Optional[float] = Field(
        description="2 month Treasury rate.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    month_3: Optional[float] = Field(
        description="3 month Treasury rate.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    month_6: Optional[float] = Field(
        description="6 month Treasury rate.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_1: Optional[float] = Field(
        description="1 year Treasury rate.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_2: Optional[float] = Field(
        description="2 year Treasury rate.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_3: Optional[float] = Field(
        description="3 year Treasury rate.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_5: Optional[float] = Field(
        description="5 year Treasury rate.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_7: Optional[float] = Field(
        description="7 year Treasury rate.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_10: Optional[float] = Field(
        description="10 year Treasury rate.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_20: Optional[float] = Field(
        description="20 year Treasury rate.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_30: Optional[float] = Field(
        description="30 year Treasury rate.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
