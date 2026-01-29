"""ETF 历史 NAV 模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EtfHistoricalNavQueryParams(QueryParams):
    """ETF 历史 NAV 查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class EtfHistoricalNavData(Data):
    """ETF 历史 NAV 数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    nav: float = Field(description="该日期的资产净值。")
