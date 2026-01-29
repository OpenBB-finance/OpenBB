"""历史 EPS 标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class HistoricalEpsQueryParams(QueryParams):
    """历史 EPS 查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class HistoricalEpsData(Data):
    """历史 EPS 数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    eps_actual: int | float | None = Field(
        default=None, description="业绩公告日的实际 EPS。"
    )
    eps_estimated: int | float | None = Field(
        default=None, description="业绩公告日的预测 EPS。"
    )
