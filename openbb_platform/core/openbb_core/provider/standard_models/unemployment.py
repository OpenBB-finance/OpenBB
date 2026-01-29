"""失业率标准模型。"""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class UnemploymentQueryParams(QueryParams):
    """失业率查询。"""

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country", ""),
        default="united_states",
    )
    frequency: Literal["monthly", "quarter", "annual"] = Field(
        description=QUERY_DESCRIPTIONS.get("frequency", ""),
        default="monthly",
        json_schema_extra={"choices": ["monthly", "quarter", "annual"]},
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class UnemploymentData(Data):
    """失业率数据。"""

    date: dateType | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date")
    )
    country: str | None = Field(
        default=None,
        description="提供失业率的国家",
    )
    value: float | None = Field(
        default=None,
        description="失业率，以归一化的百分比表示。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
