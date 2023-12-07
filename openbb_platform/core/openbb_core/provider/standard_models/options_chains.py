"""Options Chains Standard Model."""

from datetime import date as dateType
from typing import List, Optional, Set, Union

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
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class OptionsChainsData(Data):
    """Options Chains Data."""

    contract_symbol: str = Field(description="Contract symbol for the option.")
    symbol: Optional[str] = Field(
        description=DATA_DESCRIPTIONS.get("symbol", "")
        + " Here its the underlying symbol for the option.",
        default=None,
    )
    expiration: dateType = Field(description="Expiration date of the contract.")
    strike: float = Field(description="Strike price of the contract.")
    option_type: str = Field(description="Call or Put.")
    eod_date: Optional[dateType] = Field(
        default=None, description="Date for which the options chains are returned."
    )
    close: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("close", "")
    )
    close_bid: Optional[float] = Field(
        default=None, description="The closing bid price for the option that day."
    )
    close_ask: Optional[float] = Field(
        default=None, description="The closing ask price for the option that day."
    )
    volume: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
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
    open_interest: Optional[float] = Field(
        default=None, description="Open interest on the contract."
    )
    high: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("high", "")
    )
    low: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("low", "")
    )
    mark: Optional[float] = Field(
        default=None, description="The mid-price between the latest bid-ask spread."
    )
    ask_high: Optional[float] = Field(
        default=None, description="The highest ask price for the option that day."
    )
    ask_low: Optional[float] = Field(
        default=None, description="The lowest ask price for the option that day."
    )
    bid_high: Optional[float] = Field(
        default=None, description="The highest bid price for the option that day."
    )
    bid_low: Optional[float] = Field(
        default=None, description="The lowest bid price for the option that day."
    )
    implied_volatility: Optional[float] = Field(
        default=None, description="Implied volatility of the option."
    )
    delta: Optional[float] = Field(default=None, description="Delta of the option.")
    gamma: Optional[float] = Field(default=None, description="Gamma of the option.")
    theta: Optional[float] = Field(default=None, description="Theta of the option.")
    vega: Optional[float] = Field(default=None, description="Vega of the option.")

    @field_validator("date", mode="before", check_fields=False)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
