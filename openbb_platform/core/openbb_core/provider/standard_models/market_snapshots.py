"""市场快照标准模型。"""

from openbb_core.provider.abstract.data import Data, ForceInt
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class MarketSnapshotsQueryParams(QueryParams):
    """市场快照查询。"""


class MarketSnapshotsData(Data):
    """市场快照数据。"""

    exchange: str | None = Field(
        description="证券上市的交易所。", default=None
    )
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(
        description="公司、基金或证券的名称。", default=None
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
        description="较前一收盘价的价格变化。",
        default=None,
    )
    change_percent: float | None = Field(
        description="较前一收盘价的价格百分比变化。",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
