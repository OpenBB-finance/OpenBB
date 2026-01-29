"""国债价格标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field


class TreasuryPricesQueryParams(QueryParams):
    """國債價格查詢。"""

    date: dateType | None = Field(
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " 默認為最後一個營業日。",
        default=None,
    )


class TreasuryPricesData(Data):
    """國債價格數據。"""

    issuer_name: str | None = Field(
        default=None,
        description="發行實體名稱。",
    )
    cusip: str | None = Field(
        default=None,
        description="證券的 CUSIP。",
    )
    isin: str | None = Field(
        default=None,
        description="證券的 ISIN。",
    )
    security_type: str | None = Field(
        default=None,
        description="國債證券類型 - 即短期國債 (Bill)、中期國債 (Note)、長期國債 (Bond)、抗通膨債券 (TIPS)、浮動利率債券 (FRN)。",
    )
    issue_date: dateType | None = Field(
        default=None,
        description="證券的原始發行日期。",
    )
    maturity_date: dateType | None = Field(
        default=None,
        description="證券的到期日期。",
    )
    call_date: dateType | None = Field(
        description="證券的贖回日期。", default=None
    )
    bid: float | None = Field(
        default=None,
        description="證券的買入價。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    offer: float | None = Field(
        default=None,
        description="證券的賣出價。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    eod_price: float | None = Field(
        default=None,
        description="證券的收盤價格。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    last_traded_date: dateType | None = Field(
        description="證券的最後交易日期。", default=None
    )
    total_trades: int | None = Field(
        default=None,
        description="最後交易日的交易總數。",
    )
    last_price: float | None = Field(
        default=None,
        description="證券的最後成交價。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    highest_price: float | None = Field(
        default=None,
        description="最後交易日該債券的最高價格。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    lowest_price: float | None = Field(
        default=None,
        description="最後交易日該債券的最低價格。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    rate: float | None = Field(
        description="證券的年化利率或票息。",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ytm: float | None = Field(
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
