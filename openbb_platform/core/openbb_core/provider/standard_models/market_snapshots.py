"""Market Snapshots Standard Model."""

from openbb_core.provider.abstract.data import Data, ForceInt
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class MarketSnapshotsQueryParams(QueryParams):
    """Market Snapshots Query."""


class MarketSnapshotsData(Data):
    """Market Snapshots Data."""

    exchange: str | None = Field(
        description="Exchange the security is listed on.", default=None
    )
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(
        description="Name of the company, fund, or security.", default=None
    )
    open: float | None = Field(
        description=DATA_DESCRIPTIONS.get("open", ""),
        default=None,
    )
    high: float | None = Field(
        description=DATA_DESCRIPTIONS.get("high", ""),
        default=None,
    )
    low: float | None = Field(
        description=DATA_DESCRIPTIONS.get("low", ""),
        default=None,
    )
    close: float | None = Field(
        description=DATA_DESCRIPTIONS.get("close", ""),
        default=None,
    )
    volume: ForceInt | None = Field(
        description=DATA_DESCRIPTIONS.get("volume", ""), default=None
    )
    prev_close: float | None = Field(
        description=DATA_DESCRIPTIONS.get("prev_close", ""),
        default=None,
    )
    change: float | None = Field(
        description="The change in price from the previous close.",
        default=None,
    )
    change_percent: float | None = Field(
        description="The change in price from the previous close, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
