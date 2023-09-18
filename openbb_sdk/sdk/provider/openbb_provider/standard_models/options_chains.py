"""Options Chains data model."""

from datetime import date as dateType
from typing import List, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class OptionsChainsQueryParams(QueryParams):
    """Options Chains Query Params"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class OptionsChainsData(Data):
    """Options Chains Data."""

    contract_symbol: str = Field(description="Contract symbol for the option.")
    symbol: str = Field(description="Underlying symbol for the option.")
    expiration: dateType = Field(description="Expiration date of the contract.")
    strike: float = Field(description="Strike price of the contract.")
    type: str = Field(description="Call or Put.")
    date: dateType = Field(
        description="Date for which the options chains are returned."
    )

    close: Optional[float] = Field(description="Close price for the option that day.")
    close_bid: Optional[float] = Field(
        description="The closing bid price for the option that day."
    )
    close_ask: Optional[float] = Field(
        description="The closing ask price for the option that day."
    )
    volume: Optional[float] = Field(
        description="Current trading volume on the contract."
    )
    open: Optional[float] = Field(description="Opening price of the option.")
    open_bid: Optional[float] = Field(
        description="The opening bid price for the option that day."
    )
    open_ask: Optional[float] = Field(
        description="The opening ask price for the option that day."
    )
    open_interest: Optional[float] = Field(description="Open interest on the contract.")
    high: Optional[float] = Field(description="High price of the option.")
    low: Optional[float] = Field(description="Low price of the option.")
    mark: Optional[float] = Field(
        description="The mid-price between the latest bid-ask spread."
    )
    ask_high: Optional[float] = Field(
        description="The highest ask price for the option that day."
    )
    ask_low: Optional[float] = Field(
        description="The lowest ask price for the option that day."
    )
    bid_high: Optional[float] = Field(
        description="The highest bid price for the option that day."
    )
    bid_low: Optional[float] = Field(
        description="The lowest bid price for the option that day."
    )
    implied_volatility: Optional[float] = Field(
        description="Implied volatility of the option."
    )
    delta: Optional[float] = Field(description="Delta of the option.")
    gamma: Optional[float] = Field(description="Gamma of the option.")
    theta: Optional[float] = Field(description="Theta of the option.")
    vega: Optional[float] = Field(description="Vega of the option.")

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
