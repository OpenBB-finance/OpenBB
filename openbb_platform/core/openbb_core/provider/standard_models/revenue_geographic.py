"""按地理区域划分的收入标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class RevenueGeographicQueryParams(QueryParams):
    """按地理区域划分的收入查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """将字段转换为大写。"""
        return v.upper()


class RevenueGeographicData(Data):
    """按地理区域划分的收入数据。"""

    period_ending: dateType = Field(description="报告期的截止日期。")
    fiscal_period: str | None = Field(
        default=None, description="财务报告的分期。"
    )
    fiscal_year: int | None = Field(
        default=None, description="财务报告的年度。"
    )
    filing_date: dateType | None = Field(
        default=None, description="报告的申报日期。"
    )
    region: str | None = Field(
        default=None,
        description="收入数据代表的区域。",
    )
    revenue: int | float = Field(
        description="归属于该区域的总收入。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
