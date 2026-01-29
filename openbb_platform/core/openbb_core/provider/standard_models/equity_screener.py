"""股票筛选器标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class EquityScreenerQueryParams(QueryParams):
    """股票筛选器查询。"""


class EquityScreenerData(Data):
    """股票筛选器数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(default=None, description="公司名称。")
