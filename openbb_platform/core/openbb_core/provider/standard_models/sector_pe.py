"""板块市盈率标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class SectorPEQueryParams(QueryParams):
    """板块市盈率查询。"""


class SectorPEData(Data):
    """板块市盈率数据。"""

    date: dateType | None = Field(
        description=DATA_DESCRIPTIONS.get("date", ""), default=None
    )
    exchange: str | None = Field(
        default=None, description="数据的来源交易所。"
    )
    sector: str = Field(description="板块名称。")
    pe: float = Field(description="板块市盈率。")
