"""股票统计标准模型。"""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class ShareStatisticsQueryParams(QueryParams):
    """股票统计查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class ShareStatisticsData(Data):
    """股票统计数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    date: dateType | datetime | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    free_float: float | None = Field(
        default=None,
        description="上市公司的自由流通股百分率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    float_shares: int | float | None = Field(
        default=None,
        description="公众可交易的股票数量（流通股数）。",
    )
    outstanding_shares: int | float | None = Field(
        default=None, description="上市公司的股票总数（总股本）。"
    )
