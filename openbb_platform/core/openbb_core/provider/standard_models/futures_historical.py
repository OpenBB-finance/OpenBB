"""期货历史价格标准模型。"""

from datetime import date, datetime

from dateutil import parser
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class FuturesHistoricalQueryParams(QueryParams):
    """期货历史价格查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    start_date: date | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: date | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    expiration: str | None = Field(
        default=None,
        description="YYYY-MM 格式的期货到期日期。",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class FuturesHistoricalData(Data):
    """期货历史价格数据。"""

    date: datetime = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    open: float = Field(description=DATA_DESCRIPTIONS.get("open", ""))
    high: float = Field(description=DATA_DESCRIPTIONS.get("high", ""))
    low: float = Field(description=DATA_DESCRIPTIONS.get("low", ""))
    close: float = Field(description=DATA_DESCRIPTIONS.get("close", ""))
    volume: float = Field(description=DATA_DESCRIPTIONS.get("volume", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """返回格式化的日期时间。"""
        return parser.isoparse(str(v))
