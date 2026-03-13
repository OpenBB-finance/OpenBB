"""Recent Performance Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class RecentPerformanceQueryParams(QueryParams):
    """Recent Performance Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class RecentPerformanceData(Data):
    """Recent Performance Data. All returns are normalized percents."""

    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    one_day: float | None = Field(
        default=None,
        description="One-day return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    wtd: float | None = Field(
        default=None,
        description="Week to date return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    one_week: float | None = Field(
        default=None,
        description="One-week return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    mtd: float | None = Field(
        default=None,
        description="Month to date return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    one_month: float | None = Field(
        default=None,
        description="One-month return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    qtd: float | None = Field(
        default=None,
        description="Quarter to date return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    three_month: float | None = Field(
        default=None,
        description="Three-month return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    six_month: float | None = Field(
        default=None,
        description="Six-month return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ytd: float | None = Field(
        default=None,
        description="Year to date return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    one_year: float | None = Field(
        default=None,
        description="One-year return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    two_year: float | None = Field(
        default=None,
        description="Two-year return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    three_year: float | None = Field(
        default=None,
        description="Three-year return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    four_year: float | None = Field(
        default=None,
        description="Four-year",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    five_year: float | None = Field(
        default=None,
        description="Five-year return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ten_year: float | None = Field(
        default=None,
        description="Ten-year return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    max: float | None = Field(
        default=None,
        description="Return from the beginning of the time series.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
