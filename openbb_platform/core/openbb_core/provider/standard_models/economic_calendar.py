"""经济日历标准模型。"""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class EconomicCalendarQueryParams(QueryParams):
    """经济日历查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class EconomicCalendarData(Data):
    """经济日历数据。"""

    date: datetime | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    country: str | None = Field(default=None, description="事件所在国家。")
    category: str | None = Field(default=None, description="事件类别。")
    event: str | None = Field(default=None, description="事件名称。")
    importance: str | None = Field(
        default=None, description="事件的重要性级别。"
    )
    source: str | None = Field(default=None, description="数据来源。")
    currency: str | None = Field(default=None, description="数据货币。")
    unit: str | None = Field(default=None, description="数据单位。")
    consensus: str | float | None = Field(
        default=None,
        description="代表性经济学家小组的平均预测。",
    )
    previous: str | float | None = Field(
        default=None,
        description="修订后的上一期数值（如果适用）。",
    )
    revised: str | float | None = Field(
        default=None,
        description="修订后的前值（如果适用）。",
    )
    actual: str | float | None = Field(
        default=None, description="最新发布值。"
    )
