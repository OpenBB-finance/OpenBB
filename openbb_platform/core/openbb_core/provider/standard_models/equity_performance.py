"""股票表现标准模型。"""

from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field, field_validator


class EquityPerformanceQueryParams(QueryParams):
    """股票表现查询。"""

    sort: Literal["asc", "desc"] = Field(
        default="desc",
        description="排序顺序。可能的值：'asc'，'desc'。默认值：'desc'。",
    )

    @field_validator("sort", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: str | None) -> str | None:
        """将字段转换为小写。"""
        return v.lower() if v else v


class EquityPerformanceData(Data):
    """股票表现数据。"""

    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    name: str | None = Field(
        default=None,
        description="实体名称。",
    )
    price: float = Field(
        description="最新价格。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    change: float = Field(
        description="价格变化。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    percent_change: float = Field(
        description="百分比变化。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume: int | float | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("volume", ""),
    )
