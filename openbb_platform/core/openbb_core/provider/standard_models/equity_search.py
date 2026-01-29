"""股票搜索标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class EquitySearchQueryParams(QueryParams):
    """股票搜索查询。"""

    query: str = Field(description="搜索查询。", default="")
    is_symbol: bool = Field(
        description="是否按股票代码搜索。", default=False
    )


class EquitySearchData(Data):
    """股票搜索数据。"""

    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    name: str | None = Field(default=None, description="公司名称。")
