"""政府交易标准模型。"""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class GovernmentTradesQueryParams(QueryParams):
    """政府交易查询。"""

    symbol: str | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("symbol", "")
    )
    chamber: Literal["house", "senate", "all"] = Field(
        default="all", description="政府议院。"
    )
    limit: int | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """将字段转换为大写。"""
        return v.upper() if v else None


class GovernmentTradesData(Data):
    """政府交易数据。"""

    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    transaction_date: dateType | None = Field(
        default=None, description="交易日期。"
    )
    representative: str | None = Field(
        default=None, description="代表姓名。"
    )
