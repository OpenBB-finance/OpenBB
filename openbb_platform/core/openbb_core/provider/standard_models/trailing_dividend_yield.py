"""滚动股息率标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class TrailingDivYieldQueryParams(QueryParams):
    """滚动股息率查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    limit: int | None = Field(
        default=252,
        description=f"{QUERY_DESCRIPTIONS.get('limit', '')} 默认为 252，即一年的交易天数。",
    )


class TrailingDivYieldData(Data):
    """滚动股息率数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    trailing_dividend_yield: float = Field(description="滚动股息率。")
