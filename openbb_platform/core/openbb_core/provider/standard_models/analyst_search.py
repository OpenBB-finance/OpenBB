"""分析师搜索标准模型。"""

from datetime import (
    datetime,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class AnalystSearchQueryParams(QueryParams):
    """分析师搜索查询。"""

    analyst_name: str | None = Field(
        default=None,
        description="要返回的分析师姓名。"
        + " 省略将返回所有可用分析师。",
    )
    firm_name: str | None = Field(
        default=None,
        description="要返回的公司名称。"
        + " 省略将返回所有可用公司。",
    )


class AnalystSearchData(Data):
    """分析师搜索数据。"""

    last_updated: datetime | None = Field(
        default=None,
        description="最后更新日期。",
    )
    firm_name: str | None = Field(
        default=None,
        description="分析师所在公司名称。",
    )
    name_first: str | None = Field(
        default=None,
        description="分析师名字。",
    )
    name_last: str | None = Field(
        default=None,
        description="分析师姓氏。",
    )
    name_full: str = Field(
        description="分析师全名。",
    )
