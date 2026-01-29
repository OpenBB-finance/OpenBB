"""关键指标标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class KeyMetricsQueryParams(QueryParams):
    """关键指标查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class KeyMetricsData(Data):
    """关键指标数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    period_ending: dateType | None = Field(
        default=None, description="报告期截止日期。"
    )
    fiscal_year: int | None = Field(
        default=None, description="财政期间所属的财政年度（如有）。"
    )
    fiscal_period: str | None = Field(
        default=None, description="数据的财政期间（如有）。"
    )
    currency: str | None = Field(
        default=None,
        description="报告数据所用的货币。",
    )
    market_cap: int | float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("market_cap", "")
    )
