"""异常期权标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class OptionsUnusualQueryParams(QueryParams):
    """异常期权查询。"""

    symbol: str | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("symbol", "") + "（标的股票代码）",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """将字段转换为大写。"""
        return v.upper() if v else None


class OptionsUnusualData(Data):
    """异常期权数据。"""

    underlying_symbol: str | None = Field(
        description=DATA_DESCRIPTIONS.get("symbol", "") + "（标的股票代码）",
        default=None,
    )
    contract_symbol: str = Field(description="期权合约代码。")
