"""Futures Historical Price Standard Model."""

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


class FuturesHistoricalQueryParams(QueryParams):
    """Futures Historical Price Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    expiration: str | None = Field(
        default=None,
        description="Future expiry date with format YYYY-MM",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class FuturesHistoricalData(Data):
    """Futures Historical Price Data."""

    date: datetime | dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    open: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("open", "")
    )
    high: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("high", "")
    )
    low: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("low", "")
    )
    close: float = Field(description=DATA_DESCRIPTIONS.get("close", ""))
    volume: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
    )
