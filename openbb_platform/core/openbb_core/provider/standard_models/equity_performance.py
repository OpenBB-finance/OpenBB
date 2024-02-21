"""Equity Performance Standard Model."""

from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS


class EquityPerformanceQueryParams(QueryParams):
    """Equity Performance Query."""

    sort: str = Field(
        default="desc",
        description="Sort order. Possible values: 'asc', 'desc'. Default: 'desc'.",
    )


class EquityPerformanceData(Data):
    """Equity Performance Data."""

    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    name: Optional[str] = Field(
        default=None,
        description="Name of the entity.",
    )
    price: float = Field(
        description="Last price.",
    )
    change: Optional[float] = Field(
        description="Change in price value.",
    )
    change_percent: Optional[float] = Field(
        default=None,
        description="Change in price as a normalized percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume: Optional[float] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("volume", ""),
    )
