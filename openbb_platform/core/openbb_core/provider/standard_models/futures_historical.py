"""Futures Historical Price Standard Model."""

from datetime import date, datetime
from typing import Optional

from dateutil import parser
from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class FuturesHistoricalQueryParams(QueryParams):
    """Futures Historical Price Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    start_date: Optional[date] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[date] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    expiration: Optional[str] = Field(
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

    date: datetime = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    open: float = Field(description=DATA_DESCRIPTIONS.get("open", ""))
    high: float = Field(description=DATA_DESCRIPTIONS.get("high", ""))
    low: float = Field(description=DATA_DESCRIPTIONS.get("low", ""))
    close: float = Field(description=DATA_DESCRIPTIONS.get("close", ""))
    volume: float = Field(description=DATA_DESCRIPTIONS.get("volume", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return formatted datetime."""
        return parser.isoparse(str(v))
