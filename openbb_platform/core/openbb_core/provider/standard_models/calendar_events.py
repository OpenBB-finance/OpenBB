"""公司事件日历标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class CalendarEventsQueryParams(QueryParams):
    """公司事件日历查询。"""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class CalendarEventsData(Data):
    """公司事件日历数据。"""

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", "") + " 事件日期。"
    )
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
