"""股票所有权标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EquityOwnershipQueryParams(QueryParams):
    """股票所有权查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class EquityOwnershipData(Data):
    """股票所有权数据。"""

    investor_name: str = Field(description="投资实体名称。")
    cik: str | None = Field(default=None, description=DATA_DESCRIPTIONS.get("cik", ""))
    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", "") + " 截至该期间。"
    )
    filing_date: dateType | None = Field(description="报告日期。")
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
