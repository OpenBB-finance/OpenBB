"""管理层讨论与分析 (MD&A) 标准模型。"""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class ManagementDiscussionAnalysisQueryParams(QueryParams):
    """管理层讨论与分析 (MD&A) 查询属性。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    calendar_year: int | None = Field(
        default=None,
        description="报告的日历年度。默认是当前年份。"
        + " 如果未提供日历期间，但提供了日历年度，它将返回年度报告。",
    )
    calendar_period: Literal["Q1", "Q2", "Q3", "Q4"] | None = Field(
        default=None,
        description="报告的日历期间。默认是该股票代码可用的最新报告。"
        + " 如果未提供日历年度和日历期间，则会返回最新报告。",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """将字段转换为大写。"""
        return v.upper()


class ManagementDiscussionAnalysisData(Data):
    """管理层讨论与分析 (MD&A) 数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    calendar_year: int = Field(description="报告的日历年度。")
    calendar_period: int = Field(description="报告的日历期间。")
    period_ending: dateType | None = Field(
        description="报告期截止日期。", default=None
    )
    content: str = Field(
        description="管理层讨论与分析的内容。"
    )
