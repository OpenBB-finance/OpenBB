"""指数成份股标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class IndexConstituentsQueryParams(QueryParams):
    """指数成份股查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @classmethod
    @field_validator("symbol")
    def _to_upper(cls, v):
        """将股票代码转换为大写。"""
        return v.upper()


class IndexConstituentsData(Data):
    """指数成份股数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(
        default=None, description="指数成份股公司的名称。"
    )
