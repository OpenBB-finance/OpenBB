"""Stock Info data model."""

from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.models.base import BaseSymbol


class StockInfoQueryParams(QueryParams, BaseSymbol):
    """Stock Info Query Params"""


class StockInfoData(Data):
    """Stock Info Data."""

    symbol: str = Field(description="The ticker symbol.")
    name: str = Field(description="The name associated with the ticker symbol.")
    price: float = Field(description="The last price of the stock.")
    open: Optional[float] = Field(description="The opening price of the stock.")
    high: Optional[float] = Field(description="The high price of the current trading day.")
    low: Optional[float] = Field(description="The low price of the current trading day.")
    close: Optional[float] = Field(description="The closing price of the stock.")
    change: Optional[float] = Field(description="The change in price over the current trading period.")
    change_percent: Optional[float] = Field(description="The % change in price over the current trading period.")
    previous_close: Optional[float] = Field(description="The previous closing price of the stock.")

