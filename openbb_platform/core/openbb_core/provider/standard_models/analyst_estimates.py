"""分析师预估标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data, ForceInt
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class AnalystEstimatesQueryParams(QueryParams):
    """分析师预估查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class AnalystEstimatesData(Data):
    """分析师预估数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    estimated_revenue_low: ForceInt | None = Field(
        default=None, description="预估收入下限。"
    )
    estimated_revenue_high: ForceInt | None = Field(
        default=None, description="预估收入上限。"
    )
    estimated_revenue_avg: ForceInt | None = Field(
        default=None, description="预估收入平均值。"
    )
    estimated_sga_expense_low: ForceInt | None = Field(
        default=None, description="预估 SGA 费用下限。"
    )
    estimated_sga_expense_high: ForceInt | None = Field(
        default=None, description="预估 SGA 费用上限。"
    )
    estimated_sga_expense_avg: ForceInt | None = Field(
        default=None, description="预估 SGA 费用平均值。"
    )
    estimated_ebitda_low: ForceInt | None = Field(
        default=None, description="预估 EBITDA 下限。"
    )
    estimated_ebitda_high: ForceInt | None = Field(
        default=None, description="预估 EBITDA 上限。"
    )
    estimated_ebitda_avg: ForceInt | None = Field(
        default=None, description="预估 EBITDA 平均值。"
    )
    estimated_ebit_low: ForceInt | None = Field(
        default=None, description="预估 EBIT 下限。"
    )
    estimated_ebit_high: ForceInt | None = Field(
        default=None, description="预估 EBIT 上限。"
    )
    estimated_ebit_avg: ForceInt | None = Field(
        default=None, description="预估 EBIT 平均值。"
    )
    estimated_net_income_low: ForceInt | None = Field(
        default=None, description="预估净收入下限。"
    )
    estimated_net_income_high: ForceInt | None = Field(
        default=None, description="预估净收入上限。"
    )
    estimated_net_income_avg: ForceInt | None = Field(
        default=None, description="预估净收入平均值。"
    )
    estimated_eps_avg: float | None = Field(
        default=None, description="预估 EPS 平均值。"
    )
    estimated_eps_high: float | None = Field(
        default=None, description="预估 EPS 上限。"
    )
    estimated_eps_low: float | None = Field(
        default=None, description="预估 EPS 下限。"
    )
    number_analyst_estimated_revenue: ForceInt | None = Field(
        default=None, description="预估收入的分析师人数。"
    )
    number_analysts_estimated_eps: ForceInt | None = Field(
        default=None, description="预估 EPS 的分析师人数。"
    )
