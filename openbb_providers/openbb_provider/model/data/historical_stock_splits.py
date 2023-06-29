"""Historical stock splits data model."""

# IMPORT STANDARD
from datetime import date as dateType

# IMPORT THIRD-PARTY
# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol


class HistoricalStockSplitsQueryParams(QueryParams, BaseSymbol):
    """Historical Stock Splits query model.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """

    __name__ = "HistoricalStockSplitsQueryParams"


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
