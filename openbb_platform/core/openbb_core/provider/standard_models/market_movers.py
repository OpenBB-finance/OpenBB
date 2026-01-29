"""市场异动股标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class MarketMoversQueryParams(QueryParams):
    """市场异动股查询。"""


class MarketMoversData(Data):
    """市场异动股数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(
        default=None, description="与股票代码关联的名称。"
    )
    price: float = Field(description="股票代码的最新价格。")
    change: float = Field(description="较开盘价的价格变化。")
    change_percent: float = Field(description="较开盘价的百分比变化。")
