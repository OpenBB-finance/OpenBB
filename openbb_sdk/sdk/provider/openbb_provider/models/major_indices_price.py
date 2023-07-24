"""Major Indices Price Data Model."""


from datetime import datetime

from pydantic import PositiveFloat

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.models.base import BaseSymbol


class MajorIndicesPriceQueryParams(QueryParams, BaseSymbol):
    """Major indices price query.

    Parameter
    ---------
    symbol : str
        The symbol of the index.
    """


class MajorIndicesPriceData(Data):
    """Major Indices price data.

    Returns
    -------
    open : PositiveFloat
        The open price of the stock.
    high : PositiveFloat
        The high price of the stock.
    low : PositiveFloat
        The low price of the stock.
    close : PositiveFloat
        The close price of the stock.
    date : datetime
        The date of the stock.
    """

    open: PositiveFloat
    high: PositiveFloat
    low: PositiveFloat
    close: PositiveFloat
    date: datetime
