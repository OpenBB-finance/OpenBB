"""利润表标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, NonNegativeInt, field_validator


class IncomeStatementQueryParams(QueryParams):
    """利润表查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    limit: NonNegativeInt | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """将字段转换为大写。"""
        return v.upper()


class IncomeStatementData(Data):
    """利润表数据。"""

    period_ending: dateType = Field(description="报告期截止日期。")
    fiscal_period: str | None = Field(
        description="报告的财政期间。", default=None
    )
    fiscal_year: int | None = Field(
        description="财政期间所属的财政年度。", default=None
    )
