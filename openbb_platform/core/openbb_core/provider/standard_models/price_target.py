"""目标价标准模型。"""

from datetime import (
    date as dateType,
    datetime,
    time,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class PriceTargetQueryParams(QueryParams):
    """目标价查询。"""

    symbol: str | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("symbol", "")
    )
    limit: int | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """将字段转换为大写。"""
        return v.upper() if v else None


class PriceTargetData(Data):
    """目标价数据。"""

    published_date: dateType | datetime = Field(
        description="目标价的发布日期。"
    )
    published_time: time | None = Field(
        default=None, description="原始评级的时间，UTC。"
    )
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    exchange: str | None = Field(
        default=None, description="公司交易所在的交易所。"
    )
    company_name: str | None = Field(
        default=None, description="评级对象公司的名称。"
    )
    analyst_name: str | None = Field(default=None, description="分析师姓名。")
    analyst_firm: str | None = Field(
        default=None,
        description="发布目标价的分析师公司名称。",
    )
    currency: str | None = Field(
        default=None, description="数据计价货币。"
    )
    price_target: float | None = Field(
        default=None, description="当前目标价。"
    )
    adj_price_target: float | None = Field(
        default=None,
        description="针对拆股和股票股利调整后的目标价。",
    )
    price_target_previous: float | None = Field(
        default=None, description="之前的目标价。"
    )
    previous_adj_price_target: float | None = Field(
        default=None, description="之前调整后的目标价。"
    )
    price_when_posted: float | None = Field(
        default=None, description="发布时的价格。"
    )
    rating_current: str | None = Field(
        default=None, description="分析师对该公司的评级。"
    )
    rating_previous: str | None = Field(
        default=None, description="之前分析师对该公司的评级。"
    )
    action: str | None = Field(
        default=None,
        description="与该公司上次评级相比的评级变动说明。",
    )
