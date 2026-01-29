"""历史属性标准模型。"""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class HistoricalAttributesQueryParams(QueryParams):
    """历史属性查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol"))
    tag: str = Field(description="Intrinio 数据标签 ID 或代码。")
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )
    frequency: Literal["daily", "weekly", "monthly", "quarterly", "yearly"] | None = (
        Field(default="yearly", description=QUERY_DESCRIPTIONS.get("frequency"))
    )
    limit: int | None = Field(default=1000, description=QUERY_DESCRIPTIONS.get("limit"))
    tag_type: str | None = Field(
        default=None, description="过滤类型（如适用）。"
    )
    sort: Literal["asc", "desc"] | None = Field(
        default="desc", description="排序顺序。"
    )

    @field_validator("tag", mode="before", check_fields=False)
    @classmethod
    def multiple_tags(cls, v: str | list[str] | set[str]):
        """接受以逗号分隔的字符串或标签列表。"""
        if isinstance(v, str):
            return v.lower()
        return ",".join([tag.lower() for tag in list(v)])

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()

    @field_validator("frequency", "sort", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: str | None) -> str | None:
        """将字段转换为小写。"""
        return v.lower() if v else v


class HistoricalAttributesData(Data):
    """历史属性数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol"))
    tag: str | None = Field(default=None, description="获取数据的标签名称。")
    value: float | None = Field(default=None, description="数据值。")
