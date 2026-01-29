"""指数历史数据标准模型。"""

from datetime import (
    date as dateType,
    datetime,
)

from dateutil import parser
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class IndexHistoricalQueryParams(QueryParams):
    """指数历史数据查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    start_date: dateType | None = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: dateType | None = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class IndexHistoricalData(Data):
    """指数历史数据。"""

    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    date: dateType | datetime = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    open: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("open", "")
    )
    high: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("high", "")
    )
    low: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("low", "")
    )
    close: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("close", "")
    )
    volume: int | float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """返回格式化的日期时间。"""
        if ":" in str(v):
            return parser.isoparse(str(v))
        return parser.parse(str(v)).date()
