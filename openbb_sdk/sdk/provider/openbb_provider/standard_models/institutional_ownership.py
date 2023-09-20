"""Institutional Ownership Data Model."""


from datetime import date as dateType
from typing import List, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class InstitutionalOwnershipQueryParams(QueryParams):
    """Institutional Ownership Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    include_current_quarter: bool = Field(
        default=False, description="Include current quarter data."
    )
    date: Optional[dateType] = Field(description=QUERY_DESCRIPTIONS.get("date", ""))

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class InstitutionalOwnershipData(Data):
    """Institutional Ownership Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    cik: Optional[str] = Field(description="CIK of the company.")
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    investors_holding: int = Field(description="Number of investors holding the stock.")
    last_investors_holding: int = Field(
        description="Number of investors holding the stock in the last quarter."
    )
    investors_holding_change: int = Field(
        description="Change in the number of investors holding the stock."
    )
    number_of_13f_shares: Optional[int] = Field(description="Number of 13F shares.")
    last_number_of_13f_shares: Optional[int] = Field(
        description="Number of 13F shares in the last quarter."
    )
    number_of_13f_shares_change: Optional[int] = Field(
        description="Change in the number of 13F shares."
    )
    total_invested: float = Field(description="Total amount invested.")
    last_total_invested: float = Field(
        description="Total amount invested in the last quarter."
    )
    total_invested_change: float = Field(
        description="Change in the total amount invested."
    )
    ownership_percent: float = Field(description="Ownership percent.")
    last_ownership_percent: float = Field(
        description="Ownership percent in the last quarter."
    )
    ownership_percent_change: float = Field(
        description="Change in the ownership percent."
    )
    new_positions: int = Field(description="Number of new positions.")
    last_new_positions: int = Field(
        description="Number of new positions in the last quarter."
    )
    new_positions_change: int = Field(
        description="Change in the number of new positions."
    )
    increased_positions: int = Field(description="Number of increased positions.")
    last_increased_positions: int = Field(
        description="Number of increased positions in the last quarter."
    )
    increased_positions_change: int = Field(
        description="Change in the number of increased positions."
    )
    closed_positions: int = Field(description="Number of closed positions.")
    last_closed_positions: int = Field(
        description="Number of closed positions in the last quarter."
    )
    closed_positions_change: int = Field(
        description="Change in the number of closed positions."
    )
    reduced_positions: int = Field(description="Number of reduced positions.")
    last_reduced_positions: int = Field(
        description="Number of reduced positions in the last quarter."
    )
    reduced_positions_change: int = Field(
        description="Change in the number of reduced positions."
    )
    total_calls: int = Field(
        description="Total number of call options contracts traded for Apple Inc. on the specified date."
    )
    last_total_calls: int = Field(
        description="Total number of call options contracts traded for Apple Inc. on the previous reporting date."
    )
    total_calls_change: int = Field(
        description="Change in the total number of call options contracts traded between "
        "the current and previous reporting dates."
    )
    total_puts: int = Field(
        description="Total number of put options contracts traded for Apple Inc. on the specified date."
    )
    last_total_puts: int = Field(
        description="Total number of put options contracts traded for Apple Inc. on the previous reporting date."
    )
    total_puts_change: int = Field(
        description="Change in the total number of put "
        "options contracts traded between the current and previous reporting dates."
    )
    put_call_ratio: float = Field(
        description="Put-call ratio, which is the ratio of the total number of "
        "put options to call options traded on the specified date."
    )
    last_put_call_ratio: float = Field(
        description="Put-call ratio on the previous reporting date."
    )
    put_call_ratio_change: float = Field(
        description="Change in the put-call ratio between the current and previous reporting dates."
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
