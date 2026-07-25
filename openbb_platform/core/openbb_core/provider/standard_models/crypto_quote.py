"""Crypto Quote Standard Model."""

from datetime import datetime

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class CryptoQuoteQueryParams(QueryParams):
    """Crypto Quote Query.

    Source: https://www.cryptocompare.com/api/
    """

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " Can be a comma-separated list of crypto symbols (e.g., BTC,ETH,SOL)."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _to_upper(cls, v):
        """Convert field to uppercase."""
        return str(v).upper()


class CryptoQuoteData(Data):
    """Crypto Quote Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(default=None, description="Name of the cryptocurrency.")
    price: float = Field(
        description="The last price of the cryptocurrency in the given currency."
    )
    currency: str = Field(
        default="USD",
        description="The currency in which the price is denominated.",
    )
    bid: float | None = Field(
        default=None, description="The current highest bid price."
    )
    ask: float | None = Field(
        default=None, description="The current lowest ask price."
    )
    change: float | None = Field(
        default=None, description="Change in price from the previous close."
    )
    change_percent: float | None = Field(
        default=None,
        description="Change in price from the previous close, as a normalized percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume_24h: float | None = Field(
        default=None, description="Trading volume over the last 24 hours."
    )
    high_24h: float | None = Field(
        default=None, description="Highest price over the last 24 hours."
    )
    low_24h: float | None = Field(
        default=None, description="Lowest price over the last 24 hours."
    )
    market_cap: float | None = Field(
        default=None, description="Market capitalization of the cryptocurrency."
    )
    supply_circulating: float | None = Field(
        default=None, description="Circulating supply of the cryptocurrency."
    )
    supply_total: float | None = Field(
        default=None, description="Total supply of the cryptocurrency."
    )
    last_timestamp: datetime | None = Field(
        default=None, description="Timestamp of the last recorded price."
    )
    open: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("open", "")
    )
    high: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("high", "")
    )
    low: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("low", "")
    )
    close: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("close", "")
    )
    volume: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
    )

    @field_validator("change_percent", mode="before", check_fields=False)
    @classmethod
    def _normalize_percent(cls, v):
        """Normalize percent to decimal."""
        if v is not None and abs(v) > 1:
            return v / 100
        return v

    @field_validator("last_timestamp", mode="before", check_fields=False)
    @classmethod
    def _validate_timestamp(cls, v):
        """Convert Unix timestamp to datetime."""
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v)
        return v
