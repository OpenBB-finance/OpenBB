"""Market Snapshots Standard Model."""

from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS


class MarketSnapshotsQueryParams(QueryParams):
    """Market Snapshots Query."""


class MarketSnapshotsData(Data):
    """Market Snapshots Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))

    open: Optional[float] = Field(
        description=DATA_DESCRIPTIONS.get("open", ""),
        default=None,
    )
    high: Optional[float] = Field(
        description=DATA_DESCRIPTIONS.get("high", ""),
        default=None,
    )
    low: Optional[float] = Field(
        description=DATA_DESCRIPTIONS.get("low", ""),
        default=None,
    )
    close: Optional[float] = Field(
        description=DATA_DESCRIPTIONS.get("close", ""),
        default=None,
    )
    prev_close: Optional[float] = Field(
        description=DATA_DESCRIPTIONS.get("prev_close", ""),
        default=None,
    )
    change: Optional[float] = Field(description="The change in price.", default=None)
    change_percent: Optional[float] = Field(
        description="The change, as a percent.", default=None
    )
    volume: Optional[int] = Field(
        description=DATA_DESCRIPTIONS.get("volume", ""), default=None
    )
