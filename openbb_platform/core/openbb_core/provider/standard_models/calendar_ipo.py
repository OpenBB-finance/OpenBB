"""IPO 日历标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class CalendarIpoQueryParams(QueryParams):
    """IPO 日历查询。"""

    symbol: str | None = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", ""), default=None
    )
    start_date: dateType | None = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: dateType | None = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )
    limit: int | None = Field(
        description=QUERY_DESCRIPTIONS.get("limit", ""), default=100
    )


class CalendarIpoData(Data):
    """IPO 日历数据。"""

    symbol: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    ipo_date: dateType | None = Field(
        description="IPO 日期，即股票首次在主要交易所交易的日期。",
        default=None,
    )
