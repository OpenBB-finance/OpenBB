"""远期销售额预测标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data, ForceInt
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class ForwardSalesEstimatesQueryParams(QueryParams):
    """远期销售额预测查询参数。"""

    symbol: str | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["symbol"],
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v):
        """将字段转换为大写。"""
        return v.upper() if v else None


class ForwardSalesEstimatesData(Data):
    """远期销售额预测数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(default=None, description="实体名称。")
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    fiscal_year: int | None = Field(
        default=None, description="预测的财政年度。"
    )
    fiscal_period: str | None = Field(
        default=None, description="预测的财政季度。"
    )
    calendar_year: int | None = Field(
        default=None, description="预测的日历年度。"
    )
    calendar_period: str | None = Field(
        default=None, description="预测的日历季度。"
    )
    low_estimate: ForceInt | None = Field(
        default=None, description="该期间的销售额最低预测值。"
    )
    high_estimate: ForceInt | None = Field(
        default=None, description="该期间的销售额最高预测值。"
    )
    mean: ForceInt | None = Field(
        default=None, description="该期间的销售额平均预测值。"
    )
    median: ForceInt | None = Field(
        default=None, description="该期间的销售额中位数预测值。"
    )
    standard_deviation: ForceInt | None = Field(
        default=None,
        description="该期间的销售额预测值标准偏差。",
    )
    number_of_analysts: int | None = Field(
        default=None,
        description="提供该期间预测的分析师数量。",
    )
