"""加密货币历史价格标准模型。"""

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


class CryptoHistoricalQueryParams(QueryParams):
    """加密货币历史价格查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _to_upper(cls, v):
        """将字段转换为大写并删除 '-'。"""
        return str(v).upper()


class CryptoHistoricalData(Data):
    """加密货币历史价格数据。"""

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
    close: float = Field(description=DATA_DESCRIPTIONS.get("close", ""))
    volume: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
    )
    vwap: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("vwap", "")
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """返回格式化的日期时间。"""
        if ":" in str(v):
            return parser.isoparse(str(v))
        return parser.parse(str(v)).date()
