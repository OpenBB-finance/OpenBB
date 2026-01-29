"""板块表现标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class SectorPerformanceQueryParams(QueryParams):
    """板块表现查询。"""


class SectorPerformanceData(Data):
    """板块表现数据。"""

    sector: str = Field(description="板块名称。")
    change_percent: float = Field(description="较开盘价的百分比变化。")
