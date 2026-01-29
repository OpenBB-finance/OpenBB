"""BLS 系列标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class SeriesQueryParams(QueryParams):
    """BLS 系列查询。"""

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", ""),
    )
    start_date: dateType | None = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: dateType | None = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class SeriesData(Data):
    """BLS 系列数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    title: str | None = Field(default=None, description="系列标题。")
    value: float | None = Field(
        default=None, description="代码和日期的观测值。"
    )
