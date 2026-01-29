"""房价指数标准模型。"""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class HousePriceIndexQueryParams(QueryParams):
    """房价指数查询。"""

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country", ""),
        default="united_states",
    )
    frequency: Literal["monthly", "quarter", "annual"] = Field(
        description=QUERY_DESCRIPTIONS.get("frequency", ""),
        default="quarter",
        json_schema_extra={"choices": ["monthly", "quarter", "annual"]},
    )
    transform: Literal["index", "yoy", "period"] = Field(
        description="CPI 数据的转换。Period 代表与上一期相比的变化。"
        + " 默认从一年前开始变化 (yoy)。",
        default="index",
        json_schema_extra={"choices": ["index", "yoy", "period"]},
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class HousePriceIndexData(Data):
    """房价指数数据。"""

    date: dateType | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date")
    )
    country: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("country", ""),
    )
    value: float | None = Field(
        default=None,
        description="房价指数值。",
    )
