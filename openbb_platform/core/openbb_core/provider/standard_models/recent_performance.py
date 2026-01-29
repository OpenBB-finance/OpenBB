"""近期表现标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class RecentPerformanceQueryParams(QueryParams):
    """近期表现查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class RecentPerformanceData(Data):
    """近期表现数据。所有回报率均为归一化的百分比。"""

    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    one_day: float | None = Field(
        default=None,
        description="单日回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    wtd: float | None = Field(
        default=None,
        description="本周至今 (WTD) 回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    one_week: float | None = Field(
        default=None,
        description="一周回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    mtd: float | None = Field(
        default=None,
        description="本月至今 (MTD) 回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    one_month: float | None = Field(
        default=None,
        description="一月回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    qtd: float | None = Field(
        default=None,
        description="本季度至今 (QTD) 回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    three_month: float | None = Field(
        default=None,
        description="三月回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    six_month: float | None = Field(
        default=None,
        description="六月回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ytd: float | None = Field(
        default=None,
        description="今年至今 (YTD) 回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    one_year: float | None = Field(
        default=None,
        description="一年回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    two_year: float | None = Field(
        default=None,
        description="两年回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    three_year: float | None = Field(
        default=None,
        description="三年回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    four_year: float | None = Field(
        default=None,
        description="四年回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    five_year: float | None = Field(
        default=None,
        description="五年回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ten_year: float | None = Field(
        default=None,
        description="十年回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    max: float | None = Field(
        default=None,
        description="自有时间序列数据以来的回报率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
