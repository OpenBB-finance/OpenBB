"""Market Movers Standard Model."""

from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class MarketMoversQueryParams(QueryParams):
    """Market Movers Query."""


class MarketMoversData(Data):
    """Market Movers Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: Optional[str] = Field(
        default=None, description="The name associated with the ticker."
    )
    price: float = Field(description="The last price of the ticker.")
    change: float = Field(description="The change in price from open.")
    change_percent: float = Field(description="The change in percent from open.")
