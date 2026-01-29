"""联邦基金利率标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class FederalFundsRateQueryParams(QueryParams):
    """联邦基金利率查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class FederalFundsRateData(Data):
    """联邦基金利率数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: float = Field(
        description="有效联邦基金利率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    target_range_upper: float | None = Field(
        default=None,
        description="目标范围的上限。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    target_range_lower: float | None = Field(
        default=None,
        description="目标范围的下限。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percentile_1: float | None = Field(
        default=None,
        description="分布的第 1 百分位数。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percentile_25: float | None = Field(
        default=None,
        description="分布的第 25 百分位数。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percentile_75: float | None = Field(
        default=None,
        description="分布的第 75 百分位数。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percentile_99: float | None = Field(
        default=None,
        description="分布的第 99 百分位数。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume: float | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("volume", "")
        + "名义交易量（十亿美元）。",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-frontend_multiply": 1e9,
        },
    )
