"""精选短期国债标准模型。"""

from datetime import (
    date as dateType,
)
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class SelectedTreasuryBillQueryParams(QueryParams):
    """精选短期国债查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    maturity: Literal["3m", "6m"] | None = Field(
        default="3m",
        description="到期期限。",
    )

    @field_validator("maturity", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: str | None) -> str | None:
        """将字段转换为小写。"""
        return v.lower() if v else v


class SelectedTreasuryBillData(Data):
    """精选短期国债数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: float | None = Field(description="精选短期国债利率。")
