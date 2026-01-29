"""债券交易标准模型。"""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class BondTradesQueryParams(QueryParams):
    """债券交易查询。"""

    country: str | None = Field(
        default=None,
        description="获取数据的国家。匹配部分名称。",
    )
    isin: str | None = Field(
        default=None,
        description="债券的 ISIN。",
    )
    issuer_type: Literal["government", "corporate", "municipal"] | None = Field(
        default=None,
        description="债券发行人类型。",
    )
    notional_currency: str | None = Field(
        default=None,
        description="""
            债券货币，可能与交易货币不同。
            格式为 3 字母 ISO 4217 代码（例如 GBP、EUR、USD）。
        """,
    )
    start_date: dateType | str | None = Field(
        default=None,
        description=(
            QUERY_DESCRIPTIONS.get("start_date", "")
            + " YYYY-MM-DD or  ISO-8601 format. E.g. 2023-01-14T10:55:00Z"
        ),
    )
    end_date: dateType | str | None = Field(
        default=None,
        description=(
            QUERY_DESCRIPTIONS.get("end_date", "")
            + " YYYY-MM-DD or  ISO-8601 format. E.g. 2023-01-14T10:55:00Z"
        ),
    )

    @field_validator("isin", "notional_currency", mode="before", check_fields=False)
    @classmethod
    def validate_upper_case(cls, v):
        """强制字段为大写。"""
        return v.upper() if v else None


class BondTradesData(Data):
    """债券交易数据。"""

    trade_date: dateType | datetime | None = Field(
        default=None,
        description="交易日期。",
    )
    isin: str | None = Field(
        default=None,
        description="债券的 ISIN。",
    )
    figi: str | None = Field(default=None, description="债券的 FIGI。")
    cusip: str | None = Field(
        default=None,
        description="债券的 CUSIP。",
    )
    price: float | None = Field(
        default=None,
        description="债券价格。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    current_yield: float | None = Field(
        default=None,
        description="债券的当前收益率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    coupon_rate: float | None = Field(
        default=None,
        description="债券的票面利率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume: int | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("volume", ""),
    )
