"""CPI 标准模型。"""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class ConsumerPriceIndexQueryParams(QueryParams):
    """CPI 查询。"""

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country"),
        default="united_states",
    )
    transform: str = Field(
        description="CPI 数据的转换。",
        default="yoy",
    )
    frequency: Literal["annual", "quarter", "monthly"] = Field(
        default="monthly",
        description=QUERY_DESCRIPTIONS.get("frequency"),
    )
    harmonized: bool = Field(
        default=False, description="如果为 true，则返回协调数据。"
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class ConsumerPriceIndexData(Data):
    """CPI 数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    country: str = Field(description=DATA_DESCRIPTIONS.get("country"))
    value: float = Field(description="CPI 指数值或期间变化。")
