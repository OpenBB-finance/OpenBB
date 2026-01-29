"""指数搜索标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class IndexSearchQueryParams(QueryParams):
    """指数搜索查询。"""

    query: str = Field(description="搜索查询。", default="")
    is_symbol: bool = Field(
        description="是否按股票代码搜索。", default=False
    )


class IndexSearchData(Data):
    """指数搜索数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str = Field(description="指数名称。")
