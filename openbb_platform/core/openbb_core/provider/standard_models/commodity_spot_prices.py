"""商品现货价格标准模型。"""

from datetime import (
    date as dateType,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class CommoditySpotPricesQueryParams(QueryParams):
    """商品现货价格查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class CommoditySpotPricesData(Data):
    """商品现货价格数据。"""

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    symbol: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    commodity: str | None = Field(
        default=None,
        description="商品名称。",
    )
    price: float = Field(
        description="商品价格。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    unit: str | None = Field(
        default=None,
        description="商品价格单位。",
    )
