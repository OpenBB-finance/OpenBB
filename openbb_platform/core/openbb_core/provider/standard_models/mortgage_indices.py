"""抵押贷款指数标准模型。"""

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


class MortgageIndicesQueryParams(QueryParams):
    """抵押贷款指数查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class MortgageIndicesData(Data):
    """抵押贷款指数数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    name: str | None = Field(
        default=None,
        description="指数名称。",
    )
    rate: float = Field(
        description="抵押贷款利率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
