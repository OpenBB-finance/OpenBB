"""非农就业人数标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class NonFarmPayrollsQueryParams(QueryParams):
    """非农就业人数查询。"""

    date: dateType | str | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " 默认是最新报告。",
    )


class NonFarmPayrollsData(Data):
    """非农就业人数数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    value: float = Field(description=DATA_DESCRIPTIONS.get("value", ""))
