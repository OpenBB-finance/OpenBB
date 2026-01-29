"""制造业展望 - 德克萨斯州 - 标准模型。"""

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


class ManufacturingOutlookTexasQueryParams(QueryParams):
    """制造业展望 - 德克萨斯州 - 查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class ManufacturingOutlookTexasData(Data):
    """制造业展望 - 德克萨斯州 - 数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    topic: str | None = Field(default=None, description="调查响应的主题。")
    diffusion_index: float | None = Field(default=None, description="扩散指数。")
    percent_reporting_increase: float | None = Field(
        default=None,
        description="报告上个月有所增加的受访者百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percent_reporting_decrease: float | None = Field(
        default=None,
        description="报告上个月有所减少的受访者百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percent_reporting_no_change: float | None = Field(
        default=None,
        description="报告上个月没有变化的受访者百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
