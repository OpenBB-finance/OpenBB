"""Share Statistics Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class ShareStatisticsQueryParams(QueryParams):
    """Share Statistics Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class ShareStatisticsData(Data):
    """Share Statistics Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    date: dateType | datetime | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    free_float: float | None = Field(
        default=None,
        description="Percentage of unrestricted shares of a publicly-traded company.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    float_shares: int | float | None = Field(
        default=None,
        description="Number of shares available for trading by the general public.",
    )
    outstanding_shares: int | float | None = Field(
        default=None, description="Total number of shares of a publicly-traded company."
    )
