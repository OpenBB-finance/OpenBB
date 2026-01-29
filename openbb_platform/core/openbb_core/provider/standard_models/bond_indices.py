"""债券指数标准模型。"""

from datetime import (
    date as dateType,
)
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class BondIndicesQueryParams(QueryParams):
    """债券指数查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    index_type: Literal["yield", "yield_to_worst", "total_return", "oas"] = Field(
        default="yield",
        description="系列类型。OAS 是期权调整利差。默认为收益率 (yield)。",
        json_schema_extra={
            "choices": ["yield", "yield_to_worst", "total_return", "oas"]
        },
    )

    @field_validator("index_type", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: str | None) -> str | None:
        """将字段转换为小写。"""
        return v.lower() if v else v


class BondIndicesData(Data):
    """债券指数数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    value: float = Field(description="指数值。")
