"""Stock Quote data model."""

from datetime import datetime
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class StockQuoteQueryParams(QueryParams, BaseSymbol):
    """Stock Quote query model.

    Parameter
    ---------
    symbol: str
        The symbol of the company.
    symbols: str
        Comma separated list of symbols.
    """

    symbol: str = Field(default=None, description="Comma separated list of symbols.")


class StockQuoteData(Data):
    """Stock Quote data."""

    day_low: Optional[float] = Field(
        default=None,
        description="Lowest price of the stock in the current trading day.",
    )
    day_high: Optional[float] = Field(
        default=None,
        description="Highest price of the stock in the current trading day.",
    )
    date: Optional[datetime] = Field(
        description="Timestamp of the stock quote.", default=None
    )
