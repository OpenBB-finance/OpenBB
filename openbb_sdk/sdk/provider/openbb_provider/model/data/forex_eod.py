"""Forex aggregate end of day price data model."""


from datetime import datetime
from typing import Optional

from pydantic import NonNegativeFloat, PositiveFloat

from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol


class ForexEODQueryParams(QueryParams, BaseSymbol):
    """Forex end of day query.

    Parameter
    ---------
    symbol : str
        The symbol of the forex currency pair.
    """


class ForexEODData(Data):
    """Forex end of day price data.

    Returns
    -------
    date : datetime
        The date of the forex currency pair.
    open : PositiveFloat
        The open price of the forex currency pair.
    high : PositiveFloat
        The high price of the forex currency pair.
    low : PositiveFloat
        The low price of the forex currency pair.
    close : PositiveFloat
        The close price of the forex currency pair.
    adj_close : Optional[PositiveFloat]
        The adjusted close price of the forex currency pair.
    """

    date: datetime
    open: PositiveFloat
    high: PositiveFloat
    low: PositiveFloat
    close: PositiveFloat
    adj_close: Optional[PositiveFloat]
    volume: NonNegativeFloat
