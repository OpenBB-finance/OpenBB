"""高管薪酬标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class ExecutiveCompensationQueryParams(QueryParams):
    """高管薪酬查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class ExecutiveCompensationData(Data):
    """高管薪酬数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    cik: str | None = Field(default=None, description=DATA_DESCRIPTIONS.get("cik", ""))
    report_date: dateType | None = Field(
        default=None, description="报告的薪酬日期。"
    )
    company_name: str | None = Field(
        default=None, description="公司名称。"
    )
    executive: str | None = Field(default=None, description="姓名和职位。")
    year: int | None = Field(default=None, description="薪酬年份。")
    salary: int | float | None = Field(default=None, description="基本薪水。")
    bonus: int | float | None = Field(default=None, description="奖金。")
    stock_award: int | float | None = Field(default=None, description="股票奖励。")
    option_award: int | float | None = Field(default=None, description="期权奖励。")
    incentive_plan_compensation: int | float | None = Field(
        default=None, description="激励计划薪酬。"
    )
    all_other_compensation: int | float | None = Field(
        default=None, description="所有其他薪酬。"
    )
    total: int | float | None = Field(default=None, description="总薪酬。")
