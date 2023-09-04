"""Stock Info data model."""

from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class StockInfoQueryParams(QueryParams, BaseSymbol):
    """Stock Info Query Params"""


class StockInfoData(Data, BaseSymbol):
    """Stock Info Data."""

    name: str = Field(description="Name associated with the ticker symbol.")
    price: float = Field(description="Last transaction price.")
    open: float = Field(description="Opening price of the stock.")
    high: float = Field(description="High price of the current trading day.")
    low: float = Field(description="Low price of the current trading day.")
    close: float = Field(description="Closing price of the most recent trading day.")
    change: Optional[float] = Field(
        description="Change in price over the current trading period."
    )
    change_percent: Optional[float] = Field(
        description="Percent change in price over the current trading period."
    )
    prev_close: Optional[float] = Field(description="Previous closing price.")
