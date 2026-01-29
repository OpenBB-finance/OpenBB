"""ETF 表现标准模型。"""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class ETFPerformanceQueryParams(QueryParams):
    """ETF 表现查询。"""

    sort: Literal["asc", "desc"] = Field(
        default="desc",
        description="排序顺序。可能的值：'asc'，'desc'。默认值：'desc'。",
    )
    limit: int = Field(
        default=10,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )

    @field_validator("sort", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: str | None) -> str | None:
        """将字段转换为小写。"""
        return v.lower() if v else v


class ETFPerformanceData(Data):
    """ETF 表现数据。"""

    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    name: str = Field(
        description="实体名称。",
    )
    last_price: float = Field(
        description="最新价格。",
    )
    percent_change: float = Field(
        description="百分比变化。",
    )
    net_change: float = Field(
        description="净变化。",
    )
    volume: float = Field(
        description=DATA_DESCRIPTIONS.get("volume", ""),
    )
    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
