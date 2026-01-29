"""国债收益率标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class TreasuryRatesQueryParams(QueryParams):
    """國債收益率查詢。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class TreasuryRatesData(Data):
    """國債收益率數據。所有字段均以歸一化的百分比表示 - 1% = 0.01。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    week_4: float | None = Field(
        default=None,
        description="4 週國庫券利率（次級市場）。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    month_1: float | None = Field(
        description="1 個月國債收益率。",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    month_2: float | None = Field(
        description="2 個月國債收益率。",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    month_3: float | None = Field(
        description="3 個月國債收益率。",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    month_6: float | None = Field(
        description="6 個月國債收益率。",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_1: float | None = Field(
        description="1 年期國債收益率。",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_2: float | None = Field(
        description="2 年期國債收益率。",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_3: float | None = Field(
        description="3 年期國債收益率。",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_5: float | None = Field(
        description="5 年期國債收益率。",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_7: float | None = Field(
        description="7 年期國債收益率。",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_10: float | None = Field(
        description="10 年期國債收益率。",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_20: float | None = Field(
        description="20 年期國債收益率。",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_30: float | None = Field(
        description="30 年期國債收益率。",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
