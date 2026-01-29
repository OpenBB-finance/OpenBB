"""港口信息与元数据。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class PortInfoQueryParams(QueryParams):
    """港口信息查询。"""


class PortInfoData(Data):
    """港口信息数据。"""

    port_code: str = Field(description="由来源方分配给该港口的唯一 ID。")
