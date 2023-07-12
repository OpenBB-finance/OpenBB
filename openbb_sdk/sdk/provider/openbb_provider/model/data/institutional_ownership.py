"""Institutional Ownership Data Model."""


from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_provider.metadata import DESCRIPTIONS
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol


class InstitutionalOwnershipQueryParams(QueryParams, BaseSymbol):
    """Institutional Ownership QueryParams.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    include_current_quarter : bool
        Whether to include the current quarter. Default is False.
    date : Optional[dateType]
        A specific date to get data for.
    """

    include_current_quarter: bool = Field(
        default=False, description="Include current quarter data."
    )
    date: Optional[dateType] = Field(description=DESCRIPTIONS.get("date", ""))


class InstitutionalOwnershipData(Data):
    """Institutional Ownership data.

    Returns
    -------
    symbol : str
        The symbol of the company.
    cik : str
        The CIK of the company.
    date : dateType
        The date of the institutional ownership.
    investors_holding : int
        The number of investors holding the stock.
    last_investors_holding : int
        The number of investors holding the stock in the last quarter.
    investors_holding_change : int
        The change in the number of investors holding the stock.
    number_of_13f_shares : int
        The number of 13F shares.
    last_number_of_13f_shares : int
        The number of 13F shares in the last quarter.
    number_of_13f_shares_change : int
        The change in the number of 13F shares.
    total_invested : float
        The total amount invested.
    last_total_invested : float
        The total amount invested in the last quarter.
    total_invested_change : float
        The change in the total amount invested.
    ownership_percent : float
        The ownership percent.
    last_ownership_percent : float
        The ownership percent in the last quarter.
    ownership_percent_change : float
        The change in the ownership percent.
    new_positions : int
        The number of new positions.
    last_new_positions : int
        The number of new positions in the last quarter.
    new_positions_change : int
        The change in the number of new positions.
    increased_positions : int
        The number of increased positions.
    last_increased_positions : int
        The number of increased positions in the last quarter.
    increased_positions_change : int
        The change in the number of increased positions.
    closed_positions : int
        The number of closed positions.
    last_closed_positions : int
        The number of closed positions in the last quarter.
    closed_positions_change : int
        The change in the number of closed positions.
    reduced_positions : int
        The number of reduced positions.
    last_reduced_positions : int
        The number of reduced positions in the last quarter.
    """

    symbol: str = Field(min_lenght=1)
    cik: Optional[str] = Field(min_lenght=1)
    date: dateType
    investors_holding: int
    last_investors_holding: int
    investors_holding_change: int
    number_of_13f_shares: Optional[int]
    last_number_of_13f_shares: Optional[int]
    number_of_13f_shares_change: Optional[int]
    total_invested: float
    last_total_invested: float
    total_invested_change: float
    ownership_percent: float
    last_ownership_percent: float
    ownership_percent_change: float
    new_positions: int
    last_new_positions: int
    new_positions_change: int
    increased_positions: int
    last_increased_positions: int
    increased_positions_change: int
    closed_positions: int
    last_closed_positions: int
    closed_positions_change: int
    reduced_positions: int
    last_reduced_positions: int
    reduced_positions_change: int
    total_calls: int
    last_total_calls: int
    total_calls_change: int
    total_puts: int
    last_total_puts: int
    total_puts_change: int
    put_call_ratio: float
    last_put_call_ratio: float
    put_call_ratio_change: float
