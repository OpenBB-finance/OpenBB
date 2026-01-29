"""欧元短期利率标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class EuroShortTermRateQueryParams(QueryParams):
    """欧元短期利率查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class EuroShortTermRateData(Data):
    """欧元短期利率数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: float = Field(
        description="成交量加权修正平均利率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percentile_25: float | None = Field(
        default=None,
        description="成交量第 25 百分位数的利率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percentile_75: float | None = Field(
        default=None,
        description="成交量第 75 百分位数的利率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume: float | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("volume", "") + "（百万欧元）。",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-frontend_multiply": 1e6,
        },
    )
    transactions: int | None = Field(
        default=None,
        description="交易数量。",
    )
    number_of_banks: int | None = Field(
        default=None,
        description="活跃银行数量。",
    )
    large_bank_share_of_volume: float | None = Field(
        default=None,
        description="成交量中归属于 5 家最大活跃银行的百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
