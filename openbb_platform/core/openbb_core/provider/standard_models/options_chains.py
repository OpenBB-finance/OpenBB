"""Options Chains Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class OptionsChainsQueryParams(QueryParams):
    """Options Chains Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Return the symbol in uppercase."""
        return v.upper()


class OptionsChainsData(Data):
    """Options Chains Data."""

    underlying_symbol: Optional[str] = Field(
        default=None,
        description="Underlying symbol for the option.",
    )
    underlying_price: Optional[float] = Field(
        default=None,
        description="Price of the underlying stock.",
    )
    contract_symbol: str = Field(description="Contract symbol for the option.")
    eod_date: Optional[dateType] = Field(
        default=None, description="Date for which the options chains are returned."
    )
    expiration: dateType = Field(description="Expiration date of the contract.")
    dte: Optional[int] = Field(
        default=None, description="Days to expiration of the contract."
    )
    strike: float = Field(description="Strike price of the contract.")
    option_type: str = Field(description="Call or Put.")
    open_interest: Optional[int] = Field(
        default=0, description="Open interest on the contract."
    )
    volume: Optional[int] = Field(
        default=0, description=DATA_DESCRIPTIONS.get("volume", "")
    )
    theoretical_price: Optional[float] = Field(
        default=None, description="Theoretical value of the option."
    )
    last_trade_price: Optional[float] = Field(
        default=None, description="Last trade price of the option."
    )
    last_trade_size: Optional[int] = Field(
        default=None, description="Last trade size of the option."
    )
    last_trade_time: Optional[datetime] = Field(
        default=None,
        description="The timestamp of the last trade.",
    )
    tick: Optional[str] = Field(
        default=None, description="Whether the last tick was up or down in price."
    )
    bid: Optional[float] = Field(
        default=None, description="Current bid price for the option."
    )
    bid_size: Optional[int] = Field(
        default=None, description="Bid size for the option."
    )
    bid_time: Optional[datetime] = Field(
        default=None,
        description="The timestamp of the bid price.",
    )
    bid_exchange: Optional[str] = Field(
        default=None, description="The exchange of the bid price."
    )
    ask: Optional[float] = Field(
        default=None, description="Current ask price for the option."
    )
    ask_size: Optional[int] = Field(
        default=None, description="Ask size for the option."
    )
    ask_time: Optional[datetime] = Field(
        default=None,
        description="The timestamp of the ask price.",
    )
    ask_exchange: Optional[str] = Field(
        default=None, description="The exchange of the ask price."
    )
    mark: Optional[float] = Field(
        default=None, description="The mid-price between the latest bid and ask."
    )
    open: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("open", "")
    )
    open_bid: Optional[float] = Field(
        default=None, description="The opening bid price for the option that day."
    )
    open_ask: Optional[float] = Field(
        default=None, description="The opening ask price for the option that day."
    )
    high: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("high", "")
    )
    bid_high: Optional[float] = Field(
        default=None, description="The highest bid price for the option that day."
    )
    ask_high: Optional[float] = Field(
        default=None, description="The highest ask price for the option that day."
    )
    low: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("low", "")
    )
    bid_low: Optional[float] = Field(
        default=None, description="The lowest bid price for the option that day."
    )
    ask_low: Optional[float] = Field(
        default=None, description="The lowest ask price for the option that day."
    )
    close: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("close", "")
    )
    close_size: Optional[int] = Field(
        default=None, description="The closing trade size for the option that day."
    )
    close_time: Optional[datetime] = Field(
        default=None,
        description="The time of the closing price for the option that day.",
    )
    close_bid: Optional[float] = Field(
        default=None, description="The closing bid price for the option that day."
    )
    close_bid_size: Optional[int] = Field(
        default=None, description="The closing bid size for the option that day."
    )
    close_bid_time: Optional[datetime] = Field(
        default=None,
        description="The time of the bid closing price for the option that day.",
    )
    close_ask: Optional[float] = Field(
        default=None, description="The closing ask price for the option that day."
    )
    close_ask_size: Optional[int] = Field(
        default=None, description="The closing ask size for the option that day."
    )
    close_ask_time: Optional[datetime] = Field(
        default=None,
        description="The time of the ask closing price for the option that day.",
    )
    prev_close: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("prev_close", "")
    )
    change: Optional[float] = Field(
        default=None, description="The change in the price of the option."
    )
    change_percent: Optional[float] = Field(
        default=None,
        description="Change, in normalized percentage points, of the option.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    implied_volatility: Optional[float] = Field(
        default=None, description="Implied volatility of the option."
    )
    delta: Optional[float] = Field(default=None, description="Delta of the option.")
    gamma: Optional[float] = Field(default=None, description="Gamma of the option.")
    theta: Optional[float] = Field(default=None, description="Theta of the option.")
    vega: Optional[float] = Field(default=None, description="Vega of the option.")
    rho: Optional[float] = Field(default=None, description="Rho of the option.")

    @field_validator("expiration", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return the datetime object from the date string."""
        if isinstance(v, datetime):
            return datetime.strftime(v, "%Y-%m-%d")
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d")
        return v
