"""公司新闻标准模型。"""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, NonNegativeInt, field_validator


class CompanyNewsQueryParams(QueryParams):
    """公司新闻查询。"""

    symbol: str | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("symbol", ""),
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    limit: NonNegativeInt | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before")
    @classmethod
    def symbols_validate(cls, v):
        """验证代码。"""
        return v.upper() if v else None


class CompanyNewsData(Data):
    """公司新闻数据。"""

    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", "") + " 发布日期。"
    )
    title: str = Field(description="文章标题。")
    author: str | None = Field(default=None, description="文章作者。")
    excerpt: str | None = Field(
        default=None, description="文章文本摘录。"
    )
    body: str | None = Field(default=None, description="文章正文。")
    images: Any | None = Field(
        default=None, description="与文章相关的图片。"
    )
    url: str = Field(description="文章的 URL。")
    symbols: str | None = Field(
        default=None, description="与文章相关的代码。"
    )
