"""Market Snapshots  data model."""

from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class MarketSnapshotsQueryParams(QueryParams):
    """Market Snapshots Query Params"""


class MarketSnapshotsData(Data):
    """Market Snapshots Data"""

    symbol: str = Field(description="The stock symbol.")

    open: Optional[float] = Field(
        description="The opening price of the stock on the current trading day.",
        default=None,
    )
    high: Optional[float] = Field(
        description="The highest price of the stock on the current trading day.",
        default=None,
    )
    low: Optional[float] = Field(
        description="The lowest price of the stock on the current trading day.",
        default=None,
    )
    close: Optional[float] = Field(
        description="The closing price of the stock on the current trading day.",
        default=None,
    )
    prev_close: Optional[float] = Field(
        description="The previous closing price of the stock.", default=None
    )
    change: Optional[float] = Field(description="The change in price.", default=None)
    change_percent: Optional[float] = Field(
        description="The change, as a percent.", default=None
    )
    volume: Optional[int] = Field(
        description="The volume of the stock on the current trading day.", default=None
    )
