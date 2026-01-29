"""高质量市场企业债标准模型。"""

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


class HighQualityMarketCorporateBondQueryParams(QueryParams):
    """高质量市场企业债查询。"""

    date: dateType | str | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", ""),
    )


class HighQualityMarketCorporateBondData(Data):
    """高质量市场企业债数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: float = Field(
        description="利率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    maturity: str = Field(description="到期期限。")
