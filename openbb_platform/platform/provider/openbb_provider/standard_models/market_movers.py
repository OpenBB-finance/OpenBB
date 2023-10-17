"""Market Movers data model.  Base model for market gainers/losers/most active."""

from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class MarketMoversQueryParams(QueryParams):
    """Market Movers Query."""


class MarketMoversData(Data):
    """Market Movers Data."""

    symbol: str = Field(description="The ticker symbol.")
    name: Optional[str] = Field(
        default=None, description="The name associated with the ticker."
    )
    price: float = Field(description="The last price of the ticker.")
    change: float = Field(description="The change in price from open.")
    change_percent: float = Field(description="The change in percent from open.")
