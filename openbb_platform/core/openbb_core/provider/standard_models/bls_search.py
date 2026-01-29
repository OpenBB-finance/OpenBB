"""BLS 搜索模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class SearchQueryParams(QueryParams):
    """BLS 搜索查询参数。"""

    query: str = Field(
        default="",
        description="搜索词。使用分号分隔多个查询作为 & 运算符。",
    )


class SearchData(Data):
    """BLS 搜索数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    title: str | None = Field(default=None, description="系列标题。")
    survey_name: str | None = Field(default=None, description="调查名称。")
