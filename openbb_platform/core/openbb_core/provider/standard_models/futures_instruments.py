"""期货工具标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams


class FuturesInstrumentsQueryParams(QueryParams):
    """期货工具查询。"""


class FuturesInstrumentsData(Data):
    """期货工具数据。"""
