"""关键高管标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class KeyExecutivesQueryParams(QueryParams):
    """关键高管查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class KeyExecutivesData(Data):
    """关键高管数据。"""

    title: str = Field(description="关键高管的职务。")
    name: str = Field(description="关键高管的姓名。")
    pay: int | None = Field(default=None, description="关键高管的薪酬。")
    currency_pay: str | None = Field(default=None, description="薪酬货币。")
    gender: str | None = Field(default=None, description="关键高管的性别。")
    year_born: int | None = Field(
        default=None, description="关键高管的出生年份。"
    )
