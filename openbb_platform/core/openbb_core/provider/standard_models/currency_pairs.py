"""货币对标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class CurrencyPairsQueryParams(QueryParams):
    """货币对查询。"""

    query: str | None = Field(
        default=None, description="货币对搜索查询。"
    )


class CurrencyPairsData(Data):
    """货币对数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(default=None, description="货币对名称。")
