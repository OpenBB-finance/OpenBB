"""最新属性标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class LatestAttributesQueryParams(QueryParams):
    """最新属性查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol"))
    tag: str = Field(description="Intrinio 数据标签 ID 或代码。")

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


class LatestAttributesData(Data):
    """最新属性数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol"))
    tag: str | None = Field(default=None, description="获取数据的标签名称。")
    value: str | float | None = Field(
        default=None, description="数据值。"
    )
