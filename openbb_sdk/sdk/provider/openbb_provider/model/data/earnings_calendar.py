"""Earnings calendar data model."""


from datetime import date as dateType
from typing import Optional

from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol


class EarningsCalendarQueryParams(QueryParams, BaseSymbol):
    """Earnings calendar rating query model.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    limit : int
    """

    limit: Optional[int]


class EarningsCalendarData(Data, BaseSymbol):
    """Earnings calendar data.

    Returns
    -------
    symbol : str
        The symbol of the asset.
    date : date
        The date of the earnings calendar.
    eps : float
        The EPS of the earnings calendar.
    eps_estimated : float
        The estimated EPS of the earnings calendar.
    time : str
        The time of the earnings calendar.
    revenue : int
        The revenue of the earnings calendar.
    revenue_estimated : int
        The estimated revenue of the earnings calendar.
    updated_from_date : date
        The updated from date of the earnings calendar.
    fiscal_date_ending : date
        The fiscal date ending of the earnings calendar.
    """

    date: dateType
    symbol: str
    eps: Optional[float]
    eps_estimated: Optional[float]
    time: str
    revenue: Optional[int]
    revenue_estimated: Optional[int]
    updated_from_date: Optional[dateType]
    fiscal_date_ending: dateType
