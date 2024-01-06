"""Equity Quote Standard Model."""

from datetime import datetime
from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class EquityQuoteQueryParams(QueryParams):
    """Equity Quote Query."""

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " In this case, the comma separated list of symbols."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class EquityQuoteData(Data):
    """Equity Quote Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    asset_type: Optional[str] = Field(
        default=None, description="Type of asset - i.e, stock, EFF, etc."
    )
    name: Optional[str] = Field(
        default=None, description="Name of the company or asset."
    )
    exchange: Optional[str] = Field(
        default=None, description="The name or symbol of the primary trading venue."
    )
    bid: Optional[float] = Field(
        default=None, description="Price of the top bid order."
    )
    bid_size: Optional[int] = Field(
        default=None, description="Size of the top bid order."
    )
    bid_exchange: Optional[str] = Field(
        default=None, description="Exchange where the bid order was placed."
    )
    ask: Optional[float] = Field(
        default=None, description="Price of the top ask order."
    )
    ask_size: Optional[int] = Field(
        default=None, description="Size of the top ask order."
    )
    ask_exchange: Optional[str] = Field(
        default=None, description="Exchange where the ask order was placed."
    )
    last_price: Optional[float] = Field(
        default=None, description="Price of the last trade."
    )
    last_tick: Optional[str] = Field(
        default=None, description="Whether the last sale was an up or down tick."
    )
    last_size: Optional[int] = Field(
        default=None, description="Size of the last trade."
    )
    last_time: Optional[datetime] = Field(
        default=None, description="Date and Time when the last price was recorded."
    )
    open: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("open", "")
    )
    high: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("high", "")
    )
    low: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("low", "")
    )
    close: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("close", "")
    )
    volume: Optional[Union[int, float]] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
    )
    prev_close: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("prev_close", "")
    )
    change: Optional[float] = Field(
        default=None, description="Change in price from previous close."
    )
    change_percent: Optional[float] = Field(
        default=None, description="Change in price as a normalized percentage."
    )
    year_high: Optional[float] = Field(
        default=None, description="The one year high (52W High)."
    )
    year_low: Optional[float] = Field(
        default=None, description="The one year low (52W Low)."
    )
