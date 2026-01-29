"""指数信息标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class IndexInfoQueryParams(QueryParams):
    """指数信息查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class IndexInfoData(Data):
    """指数信息数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str = Field(description="指数名称。")
    description: str | None = Field(
        description="指数的简短描述。", default=None
    )
    methodology: str | None = Field(
        description="编制方案文档的 URL。", default=None
    )
    factsheet: str | None = Field(
        description="概览文档 (Factsheet) 的 URL。", default=None
    )
    num_constituents: int | None = Field(
        description="指数中的成份股数量。", default=None
    )
