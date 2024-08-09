"""Historical Market Cap Model."""

from datetime import date as dateType
from typing import Optional, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class HistoricalMarketCapQueryParams(QueryParams):
    """Historical Market Cap Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class HistoricalMarketCapData(Data):
    """Historical Market Cap Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    market_cap: Union[int, float] = Field(
        description="Market capitalization of the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
