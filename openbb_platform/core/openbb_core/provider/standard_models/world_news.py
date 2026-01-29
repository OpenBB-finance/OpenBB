"""世界新闻标准模型。"""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, NonNegativeInt, field_validator


class WorldNewsQueryParams(QueryParams):
    """世界新闻查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " 默认为 2 周前。",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", "") + " 默认为今天。",
    )
    limit: NonNegativeInt | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("limit", "")
        + " 要返回的文章数量。",
    )

    @field_validator("start_date", mode="before")
    @classmethod
    def start_date_validate(cls, v) -> dateType:  # pylint: disable=E0213
        """如果起始日期为空，则进行填充。"""
        if not v:
            now = datetime.now().date()
            v = now - relativedelta(weeks=2)
        return v

    @field_validator("end_date", mode="before")
    @classmethod
    def end_date_validate(cls, v) -> dateType:  # pylint: disable=E0213
        """如果结束日期为空，则进行填充。"""
        if not v:
            v = datetime.now().date()
        return v


class WorldNewsData(Data):
    """世界新闻数据。"""

    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", "") + " 发布日期。"
    )
    title: str = Field(description="文章标题。")
    author: str | None = Field(default=None, description="文章作者。")
    excerpt: str | None = Field(
        default=None, description="文章正文摘录。"
    )
    body: str | None = Field(default=None, description="文章正文。")
    images: Any | None = Field(
        default=None, description="与文章相关的图片。"
    )
    url: str | None = Field(default=None, description="文章 URL。")
