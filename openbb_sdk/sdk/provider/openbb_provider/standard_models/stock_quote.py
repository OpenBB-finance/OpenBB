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

    symbol: Optional[str] = Field(
        default=None, description="Comma separated list of symbols."
    )


class StockQuoteData(Data):
    """Stock Quote data."""

    symbol: str = Field(description="Symbol of the company.")
    name: Optional[str] = Field(description="The name of the company.")
    price: Optional[float] = Field(
        description="The current trading price of the stock."
    )
    changes_percentage: Optional[float] = Field(
        description="The change percentage of the stock price."
    )
    change: Optional[float] = Field(description="The change of the stock price.")
    day_low: Optional[float] = Field(
        default=None,
        description="The lowest price of the stock in the current trading day.",
    )
    day_high: Optional[float] = Field(
        default=None,
        description="The highest price of the stock in the current trading day.",
    )
    year_high: Optional[float] = Field(
        description="The highest price of the stock in the last 52 weeks."
    )
    year_low: Optional[float] = Field(
        description="The lowest price of the stock in the last 52 weeks."
    )
    market_cap: Optional[float] = Field(description="The market cap of the company.")
    price_avg50: Optional[float] = Field(
        description="The 50 days average price of the stock."
    )
    price_avg200: Optional[float] = Field(
        description="The 200 days average price of the stock."
    )
    volume: Optional[int] = Field(
        description="The volume of the stock in the current trading day."
    )
    avg_volume: Optional[int] = Field(
        default=None,
        description="The average volume of the stock in the last 10 trading days.",
    )
    exchange: Optional[str] = Field(description="The exchange the stock is traded on.")
    open: Optional[float] = Field(
        default=None,
        description="The opening price of the stock in the current trading day.",
    )
    previous_close: Optional[float] = Field(
        description="The previous closing price of the stock."
    )
    eps: Optional[float] = Field(description="The earnings per share of the stock.")
    pe: Optional[float] = Field(description="The price earnings ratio of the stock.")
    earnings_announcement: Optional[str] = Field(
        description="The earnings announcement date of the stock."
    )
    shares_outstanding: Optional[int] = Field(
        description="The number of shares outstanding of the stock."
    )
    date: Optional[datetime] = Field(
        description="The timestamp of the stock quote.", alias="timestamp"
    )
