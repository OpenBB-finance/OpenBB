"""Share Statistics Data Model."""


from datetime import date as dateType

from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol


class ShareStatisticsQueryParams(QueryParams, BaseSymbol):
    """Share Statistics query.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """

    __name__ = "ShareStatisticsQueryParams"


class ShareStatisticsData(Data):
    """Return Share Statistics Data.

    Returns
    -------
    symbol : str
        The symbol of the company.
    date : dateType
        The date of the share statistics.
    free_float : float
        The free float of the company.
    float_shares : float
        The float shares of the company.
    outstanding_shares : float
        The outstanding shares of the company.
    source : str
        The source of the data.
    """

    symbol: str
    date: dateType
    free_float: float
    float_shares: float
    outstanding_shares: float
    source: str
