"""资产负债表标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, NonNegativeInt, field_validator


class BalanceSheetQueryParams(QueryParams):
    """资产负债表查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    limit: NonNegativeInt | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """将字段转换为大写。"""
        return v.upper()


class BalanceSheetData(Data):
    """资产负债表数据。"""

    period_ending: dateType = Field(description="报告期的结束日期。")
    fiscal_period: str | None = Field(
        description="报告的会计期间。", default=None
    )
    fiscal_year: int | None = Field(
        description="会计期间的会计年度。", default=None
    )
