"""财务属性标准模型。"""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class FinancialAttributesQueryParams(QueryParams):
    """财务属性查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol"))
    tag: str = Field(description=QUERY_DESCRIPTIONS.get("tag"))
    period: Literal["annual", "quarter"] | None = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period")
    )
    limit: int | None = Field(default=1000, description=QUERY_DESCRIPTIONS.get("limit"))
    type: str | None = Field(
        default=None, description="过滤类型（如适用）。"
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )
    sort: Literal["asc", "desc"] | None = Field(
        default="desc", description="排序顺序。"
    )

    @field_validator("period", "sort", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: str | None) -> str | None:
        """将字段转换为小写。"""
        return v.lower() if v else v


class FinancialAttributesData(Data):
    """财务属性数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    value: float | None = Field(default=None, description="数据值。")
