"""财报电话会议成绩单标准模型。"""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EarningsCallTranscriptQueryParams(QueryParams):
    """财报电话会议成绩单查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    year: int | None = Field(
        default=None, description="财报电话会议成绩单的年份。"
    )
    quarter: Literal[1, 2, 3, 4] | None = Field(
        default=None, description="财报电话会议成绩单的季度周期。"
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class EarningsCallTranscriptData(Data):
    """财报电话会议成绩单数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    year: int = Field(description="财报电话会议成绩单的年份。")
    quarter: str = Field(description="财报电话会议成绩单的季度。")
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    content: str = Field(description="财报电话会议成绩单的内容。")
