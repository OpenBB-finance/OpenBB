"""行业市盈率标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class IndustryPEQueryParams(QueryParams):
    """行业市盈率查询。"""


class IndustryPEData(Data):
    """行业市盈率数据。"""

    date: dateType | None = Field(
        description=DATA_DESCRIPTIONS.get("date", ""), default=None
    )
    exchange: str | None = Field(
        default=None, description="数据来源的交易所。"
    )
    industry: str = Field(description="行业名称。")
    pe: float = Field(description="该行业的市盈率。")
