"""比较公司事实模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class CompareCompanyFactsQueryParams(QueryParams):
    """比较公司事实查询。"""

    symbol: str | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("symbol", "")
    )
    fact: str = Field(
        default="",
        description="要查找的事实，通常是 GAAP 报告度量。选择因提供商而异。",
    )


class CompareCompanyFactsData(Data):
    """比较公司事实数据。"""

    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    name: str | None = Field(default=None, description="实体名称。")
    value: float = Field(
        description="事实或概念的报告值。",
    )
    reported_date: dateType | None = Field(
        default=None, description="报告的备案日期。"
    )
    period_beginning: dateType | None = Field(
        default=None,
        description="报告期的开始日期。",
    )
    period_ending: dateType | None = Field(
        default=None,
        description="报告期的结束日期。",
    )
    fiscal_year: int | None = Field(
        default=None,
        description="会计年度。",
    )
    fiscal_period: str | None = Field(
        default=None,
        description="会计年度的会计期间。",
    )
