"""TIPS (通胀保值国债) 收益率标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class TipsYieldsQueryParams(QueryParams):
    """TIPS 收益率查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class TipsYieldsData(Data):
    """TIPS 收益率数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    due: dateType | None = Field(
        default=None,
        description="证券的到期日（成熟日期）。",
    )
    name: str | None = Field(
        default=None,
        description="证券名称。",
    )
    value: float = Field(
        default=None,
        description="收益率数值。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
