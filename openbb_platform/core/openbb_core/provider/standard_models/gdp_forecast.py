"""GDP 预测标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class GdpForecastQueryParams(QueryParams):
    """GDP 预测查询。"""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class GdpForecastData(Data):
    """GDP 预测数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    country: str = Field(description=DATA_DESCRIPTIONS.get("country"))
    value: int | float = Field(
        description="该国家和日期的 GDP 预测值。"
    )
