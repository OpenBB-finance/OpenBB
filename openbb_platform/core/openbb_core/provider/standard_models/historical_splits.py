"""历史拆股标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class HistoricalSplitsQueryParams(QueryParams):
    """历史拆股查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class HistoricalSplitsData(Data):
    """历史拆股数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    numerator: float | None = Field(
        default=None,
        description="拆股分子。",
    )
    denominator: float | None = Field(
        default=None,
        description="拆股分母。",
    )
    split_ratio: str | None = Field(
        default=None,
        description="拆分比例。",
    )
