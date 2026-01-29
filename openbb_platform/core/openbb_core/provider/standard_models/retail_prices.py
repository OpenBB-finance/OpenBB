"""零售价格标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class RetailPricesQueryParams(QueryParams):
    """零售价格查询。"""

    item: str | None = Field(
        default=None,
        description="待查询的项目或项目篮子。",
    )
    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country", ""),
        default="united_states",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class RetailPricesData(Data):
    """零售价格数据。"""

    date: dateType | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date")
    )
    symbol: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    country: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("country", ""),
    )
    description: str = Field(
        default=None,
        description="项目描述。",
    )
    value: float | None = Field(
        default=None,
        description="每单位的价格或价格变动。",
    )
