"""海上咽喉点信息和元数据。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class MaritimeChokePointInfoQueryParams(QueryParams):
    """海上咽喉点信息查询。"""


class MaritimeChokePointInfoData(Data):
    """海上咽喉点信息数据。"""

    chokepoint_code: str = Field(
        description="由来源方分配给该咽喉点的唯一 ID。"
    )
