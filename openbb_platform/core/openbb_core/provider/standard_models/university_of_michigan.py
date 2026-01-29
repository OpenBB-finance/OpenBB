"""密歇根大学调查标准模型。"""

from datetime import (
    date as dateType,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class UofMichiganQueryParams(QueryParams):
    """密歇根大学调查查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class UofMichiganData(Data):
    """密歇根大学调查数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    consumer_sentiment: float | None = Field(
        default=None,
        description="密歇根大学每月消费者调查结果指数，用于评估未来的支出和储蓄。（1966:Q1=100）。",
    )
    inflation_expectation: float | None = Field(
        default=None,
        description="消费者调查中对未来 12 个月价格变化的预期中位数。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
