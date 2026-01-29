"""期货曲线标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class FuturesCurveQueryParams(QueryParams):
    """期货曲线查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    date: dateType | str | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", ""),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v):
        """将字段转换为大写。"""
        return v.upper()

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """验证日期。"""
        # pylint: disable=import-outside-toplevel
        from pandas import to_datetime

        if v is None:
            return None
        if isinstance(v, dateType):
            return v.strftime("%Y-%m-%d")
        new_dates: list = []
        if isinstance(v, str):
            dates = v.split(",")
        if isinstance(v, list):
            dates = v
        for date in dates:
            new_dates.append(to_datetime(date).date().strftime("%Y-%m-%d"))

        return ",".join(new_dates) if new_dates else None


class FuturesCurveData(Data):
    """期货曲线数据。"""

    date: dateType | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    expiration: str = Field(description="期货到期月份。")
    price: float = Field(
        default=None,
        description="期货合约的价格。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
