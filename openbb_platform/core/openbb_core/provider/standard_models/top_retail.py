"""热门零售交易标的标准模型。"""

from datetime import date as DateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class TopRetailQueryParams(QueryParams):
    """热门零售交易标的搜索查询。"""

    limit: int = Field(description=QUERY_DESCRIPTIONS.get("limit", ""), default=5)


class TopRetailData(Data):
    """热门零售交易标的搜索数据。"""

    date: DateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    activity: float = Field(description="代码的活跃度。")
    sentiment: float = Field(
        description="代码的情绪。1 为看涨，-1 为看跌。"
    )
