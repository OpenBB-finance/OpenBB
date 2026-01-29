"""可用指数标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
)
from pydantic import Field


class AvailableIndicesQueryParams(QueryParams):
    """可用指数查询。"""


class AvailableIndicesData(Data):
    """可用指数数据。
    
    返回提供者提供的可用指数列表。
    """

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("name", "")
    )
    exchange: str | None = Field(
        default=None, description="指数上市的证券交易所。"
    )
    currency: str | None = Field(
        default=None, description="指数交易的货币。"
    )
