"""加密货币搜索标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class CryptoSearchQueryParams(QueryParams):
    """加密货币搜索查询。"""

    query: str | None = Field(description="搜索查询。", default=None)


class CryptoSearchData(Data):
    """加密货币搜索数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", "") + " (Crypto)")
    name: str | None = Field(description="加密货币名称。", default=None)
