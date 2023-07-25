"""Stock aggregate end of day price data model."""


from datetime import date, datetime
from typing import Optional

from pydantic import Field, PositiveFloat

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.metadata import QUERY_DESCRIPTIONS
from openbb_provider.models.base import BaseSymbol


class StockEODQueryParams(QueryParams, BaseSymbol):
    """Stock end of day query.
    Parameter
    ---------
    symbol : str
        The symbol of the company.
    start_date : Optional[date]
        The start date of the stock data from which to retrieve the data.
    end_date : Optional[date]
        The end date of the stock data up to which to retrieve the data.
    """

    start_date: Optional[date] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
        default=None,
    )
    end_date: Optional[date] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )


class StockEODData(Data):
    """Stock end of day price data.

    Returns
    -------
    date : datetime
        The date of the stock.
    open : PositiveFloat
        The open price of the stock.
    high : PositiveFloat
        The high price of the stock.
    low : PositiveFloat
        The low price of the stock.
    close : PositiveFloat
        The close price of the stock.
    adj_close : Optional[PositiveFloat]
        The adjusted close price of the stock.
    volume : PositiveFloat
        The volume of the stock.
    """

    date: datetime
    open: PositiveFloat
    high: PositiveFloat
    low: PositiveFloat
    close: PositiveFloat
    volume: PositiveFloat
