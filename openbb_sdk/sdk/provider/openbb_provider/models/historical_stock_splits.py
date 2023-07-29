"""Historical stock splits data model."""


from datetime import date as dateType

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.models.base import BaseSymbol


class HistoricalStockSplitsQueryParams(QueryParams, BaseSymbol):
    """Historical Stock Splits query model.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class HistoricalStockSplitsData(Data):
    """Historical stock splits data.

    Returns
    -------
    date : date
        The date of the historical stock splits.
    label : str
        The label of the historical stock splits.
    numerator : float
        The numerator of the historical stock splits.
    denominator : float
        The denominator of the historical stock splits.
    """

    date: dateType
    label: str
    numerator: float
    denominator: float
