"""Crypto Price Data Model."""


from datetime import date, datetime
from typing import Optional

from pydantic import Field, PositiveFloat

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.metadata import QUERY_DESCRIPTIONS
from openbb_provider.models.base import BaseSymbol


class CryptoPriceQueryParams(QueryParams, BaseSymbol):
    """Crypto price query.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    start_date : date
        The start date of the query.
    end_date : Optional[date]
        The end date of the query.
    """

    # These fields only work with Polygon
    start_date: date = Field(description=QUERY_DESCRIPTIONS.get("start_date", ""))
    end_date: Optional[date] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=date.today()
    )


class CryptoPriceData(Data):
    """Crypto price data.

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
