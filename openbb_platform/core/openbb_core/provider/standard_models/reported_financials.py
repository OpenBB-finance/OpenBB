"""申报财务数据。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator, model_validator


class ReportedFinancialsQueryParams(QueryParams):
    """申报财务数据查询参数。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: str = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    statement_type: str = Field(
        default="balance",
        description="财务报表类型 - 即资产负债表 (balance)、利润表 (income)、现金流量表 (cash)。",
    )
    limit: int | None = Field(
        default=100,
        description=(
            QUERY_DESCRIPTIONS.get("limit", "")
            + " 虽然响应对象包含多个结果，"
            + " 但由于字段、年度和季度之间存在差异，"
            + " 建议分块查看结果。"
        ),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """将字段转换为大写。"""
        return v.upper()

    @field_validator("period", "statement_type", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: str | None) -> str | None:
        """将字段转换为小写。"""
        return v.lower() if v else v


class ReportedFinancialsData(Data):
    """申报财务数据。"""

    period_ending: dateType = Field(
        description="报告期的截止日期。"
    )
    fiscal_period: str = Field(
        description="报告的财政期间（例如 FY、Q1 等）。"
    )
    fiscal_year: int | None = Field(
        description="财政期间所属的财政年度。", default=None
    )

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """检查零值并将其替换为 None。"""
        return (
            {k: None if v == 0 else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )
