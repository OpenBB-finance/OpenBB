"""Market Movers Standard Model."""

from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS


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
    change_percent: Optional[float] = Field(
        default=None,
        description="The change in price, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
