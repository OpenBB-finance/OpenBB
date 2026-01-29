"""ETF 搜索标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class EtfSearchQueryParams(QueryParams):
    """ETF 搜索查询。"""

    query: str | None = Field(description="搜索查询。", default="")


class EtfSearchData(Data):
    """ETF 搜索数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", "") + "(ETF)")
    name: str | None = Field(description="ETF 名称。", default=None)
