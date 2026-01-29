"""石油状况报告标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class PetroleumStatusReportQueryParams(QueryParams):
    """石油状况报告查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class PetroleumStatusReportData(Data):
    """石油状况报告数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    table: str | None = Field(description="数据表名称。")
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    order: int | None = Field(
        default=None, description="数据在表中的呈现顺序。"
    )
    title: str | None = Field(default=None, description="数据标题。")
    value: int | float = Field(description="数据值。")
    unit: str | None = Field(default=None, description="数据的单位或比例。")
