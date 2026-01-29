"""可用指标标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class AvailableIndicesQueryParams(QueryParams):
    """可用指标查询。"""


class AvailableIndicatorsData(Data):
    """可用指标数据。
    
    返回提供者提供的可用经济指标列表。
    """

    symbol_root: str | None = Field(
        default=None, description="代表指标的根代码。"
    )
    symbol: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("symbol", "")
        + " The root symbol with additional codes.",
    )
    country: str | None = Field(
        default=None,
        description="由代码代表的国家、地区或实体的名称。",
    )
    iso: str | None = Field(
        default=None,
        description="由代码代表的国家、地区或实体的 ISO 代码。",
    )
    description: str | None = Field(
        default=None, description="指标的描述。"
    )
    frequency: str | None = Field(
        default=None, description="指标数据的频率。"
    )
