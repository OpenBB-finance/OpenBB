"""日历拆分标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class CalendarSplitsQueryParams(QueryParams):
    """日历拆分查询。"""

    start_date: dateType | None = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: dateType | None = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )


class CalendarSplitsData(Data):
    """日历拆分数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    numerator: float = Field(description="股票拆分的分子。")
    denominator: float = Field(description="股票拆分的分母。")
