"""Executive Compensation Data Model."""


from datetime import date as dateType
from typing import Optional

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.models.base import BaseSymbol


class ExecutiveCompensationQueryParams(QueryParams, BaseSymbol):
    """Executive Compensation query model.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class ExecutiveCompensationData(Data):
    """Return Executive Compensation Data.

    Returns
    -------
    cik : Optional[str]
        The Central Index Key (CIK) of the company.
    symbol : str
        The symbol of the company.
    filing_date : dateType
        The date of the filing.
    accepted_date : dateType
        The date the filing was accepted.
    name_and_position : str
        The name and position of the executive.
    year : int
        The year of the compensation.
    salary : float
        The salary of the executive.
    bonus : float
        The bonus of the executive.
    stock_award : float
        The stock award of the executive.
    incentive_plan_compensation : float
        The incentive plan compensation of the executive.
    all_other_compensation : float
        The all other compensation of the executive.
    total : float
        The total compensation of the executive.
    url : str
        The URL of the filing.
    """

    cik: Optional[str]
    symbol: str
    filing_date: dateType
    accepted_date: dateType
    name_and_position: str
    year: int
    salary: float
    bonus: float
    stock_award: float
    incentive_plan_compensation: float
    all_other_compensation: float
    total: float
    url: str
