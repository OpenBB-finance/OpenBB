"""指数快照标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class IndexSnapshotsQueryParams(QueryParams):
    """指数快照查询。"""

    region: str = Field(
        default="us", description="数据的关注区域——例如：us（美国）、eu（欧洲）。"
    )


class IndexSnapshotsData(Data):
    """指数快照数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(default=None, description="指数名称。")
    currency: str | None = Field(default=None, description="指数的计价货币。")
    price: float | None = Field(default=None, description="指数的当前价格。")
    open: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("open", "")
    )
    high: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("high", "")
    )
    low: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("low", "")
    )
    close: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("close", "")
    )
    volume: int | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
    )
    prev_close: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("prev_close", "")
    )
    change: float | None = Field(
        default=None, description="指数值的变化。"
    )
    change_percent: float | None = Field(
        default=None,
        description="指数的变化百分比。",
    )
