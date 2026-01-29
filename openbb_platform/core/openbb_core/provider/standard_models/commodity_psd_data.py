"""商品供需平衡数据标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class CommodityPsdDataQueryParams(QueryParams):
    """商品供需平衡数据查询。"""


class CommodityPsdData(Data):
    """商品供需平衡数据。"""

    region: str | None = Field(default=None, description="区域组类别。")
    country: str | None = Field(
        default=None,
        description="国家或地区名称。",
    )
    commodity: str | None = Field(
        default=None,
        description="商品名称。",
    )
    attribute: str | None = Field(
        default=None,
        description="行值名称。",
    )
    marketing_year: str | None = Field(
        default=None,
        description="商品的市场年度。",
    )
    value: float | int | None = Field(
        default=None,
        description="给定市场年度中商品属性的值。",
    )
    unit: str | None = Field(
        default=None,
        description="值的计量单位。",
    )
