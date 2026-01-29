"""FRED 搜索模型。"""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class SearchQueryParams(QueryParams):
    """FRED 搜索查询参数。"""

    query: str | None = Field(default=None, description="搜索词。")


class SearchData(Data):
    """FRED 搜索数据。"""

    release_id: str | None = Field(
        default=None,
        description="用于查询的发布 ID。",
    )
    series_id: str | None = Field(
        default=None,
        description="发布项目中条目的系列 ID。",
    )
    series_group: str | None = Field(
        default=None,
        description="系列的系列组 ID。此值用于查询区域数据。",
    )
    region_type: str | None = Field(
        default=None,
        description="系列的区域类型。",
    )
    name: str | None = Field(
        default=None,
        description="发布项目的名称。",
    )
    title: str | None = Field(
        default=None,
        description="系列的标题。",
    )
    observation_start: dateType | None = Field(
        default=None, description="系列中第一次观测的日期。"
    )
    observation_end: dateType | None = Field(
        default=None, description="系列中最后一次观测的日期。"
    )
    frequency: str | None = Field(
        default=None,
        description="数据的频率。",
    )
    frequency_short: str | None = Field(
        default=None,
        description="数据频率的简写。",
    )
    units: str | None = Field(
        default=None,
        description="数据的单位。",
    )
    units_short: str | None = Field(
        default=None,
        description="数据单位的简写。",
    )
    seasonal_adjustment: str | None = Field(
        default=None,
        description="数据的季节性调整。",
    )
    seasonal_adjustment_short: str | None = Field(
        default=None,
        description="数据季节性调整的简写。",
    )
    last_updated: datetime | None = Field(
        default=None,
        description="数据最后更新的日期时间。",
    )
    popularity: int | None = Field(
        default=None,
        description="系列的受欢迎程度",
    )
    group_popularity: int | None = Field(
        default=None,
        description="发布项目的组受欢迎程度项",
    )
    realtime_start: dateType | None = Field(
        default=None,
        description="系列的实时开始日期。",
    )
    realtime_end: dateType | None = Field(
        default=None,
        description="系列的实时结束日期。",
    )
    notes: str | None = Field(default=None, description="发布项目的描述。")
    press_release: bool | None = Field(
        description="发布项目是否为新闻发布。",
        default=None,
    )
    url: str | None = Field(default=None, description="发布项目的 URL。")
