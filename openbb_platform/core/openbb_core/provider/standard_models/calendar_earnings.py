"""财报日历标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class CalendarEarningsQueryParams(QueryParams):
    """财报日历查询。"""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class CalendarEarningsData(Data):
    """财报日历数据。"""

    report_date: dateType = Field(description="财报发布日期。")
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(description="实体名称。", default=None)
    eps_previous: float | None = Field(
        default=None,
        description="上一个报告期的每股收益。",
    )
    eps_consensus: float | None = Field(
        default=None,
        description="分析师一致预期的每股收益。",
    )
