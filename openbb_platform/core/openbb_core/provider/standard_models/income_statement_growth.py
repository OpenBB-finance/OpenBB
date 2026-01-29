"""利润表增长标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class IncomeStatementGrowthQueryParams(QueryParams):
    """利润表增长查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    limit: int | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class IncomeStatementGrowthData(Data):
    """利润表增长数据。"""

    period_ending: dateType = Field(description="报告期截止日期。")
    fiscal_period: str | None = Field(
        description="报告的财政期间。", default=None
    )
    fiscal_year: int | None = Field(
        description="财政期间所属的财政年度。", default=None
    )
