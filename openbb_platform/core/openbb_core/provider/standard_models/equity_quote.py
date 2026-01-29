"""股票报价标准模型。"""

from datetime import datetime

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EquityQuoteQueryParams(QueryParams):
    """股票报价查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class EquityQuoteData(Data):
    """股票报价数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    asset_type: str | None = Field(
        default=None, description="资产类型 - 例如股票，ETF 等。"
    )
    name: str | None = Field(default=None, description="公司或资产的名称。")
    exchange: str | None = Field(
        default=None,
        description="数据来源的场所名称或符号。",
    )
    bid: float | None = Field(default=None, description="最高买入价。")
    bid_size: int | None = Field(
        default=None,
        description="这代表给定价格下的整手订单数量。"
        + " 正常的整手大小为 100 股。"
        + " 大小为 2 意味着在给定价格下有 200 股可用。",
    )
    bid_exchange: str | None = Field(
        default=None,
        description="下达买入订单的特定交易场所。",
    )
    ask: float | None = Field(default=None, description="最低卖出价。")
    ask_size: int | None = Field(
        default=None,
        description="这代表给定价格下的整手订单数量。"
        + " 正常的整手大小为 100 股。"
        + " 大小为 2 意味着在给定价格下有 200 股可用。",
    )
    ask_exchange: str | None = Field(
        default=None,
        description="下达卖出订单的特定交易场所。",
    )
    quote_conditions: str | int | list[str] | list[int] | None = Field(
        default=None,
        description="适用于报价的条件或条件代码。",
    )
    quote_indicators: str | int | list[str] | list[int] | None = Field(
        default=None,
        description="适用于参与者报价的指标或指标代码，与发行价格区间有关，或者报价对 NBBO 的影响有关。",
    )
    sales_conditions: str | int | list[str] | list[int] | None = Field(
        default=None,
        description="适用于销售的条件或条件代码。",
    )
    sequence_number: int | None = Field(
        default=None,
        description="序列号表示消息事件发生的顺序。"
        + " 这对于每个股票代码是递增且唯一的，"
        + " 但并不总是连续的（例如，1, 2, 6, 9, 10, 11）。",
    )
    market_center: str | None = Field(
        default=None,
        description="发起消息的 UTP 参与者的 ID。",
    )
    participant_timestamp: datetime | None = Field(
        default=None,
        description="交易所生成报价的时间戳。",
    )
    trf_timestamp: datetime | None = Field(
        default=None,
        description="TRF（贸易报告设施）接收到消息的时间戳。",
    )
    sip_timestamp: datetime | None = Field(
        default=None,
        description="SIP（证券信息处理器）从交易所接收到消息的时间戳。",
    )
    last_price: float | None = Field(
        default=None, description="最新交易价格。"
    )
    last_tick: str | None = Field(
        default=None, description="上一次销售是上涨还是下跌。"
    )
    last_size: int | None = Field(default=None, description="最新交易的规模。")
    last_timestamp: datetime | None = Field(
        default=None, description="记录最后价格的日期和时间。"
    )
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
    exchange_volume: int | float | None = Field(
        default=None,
        description="特定交易所在交易日内交换的股票数量。",
    )
    prev_close: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("prev_close", "")
    )
    change: float | None = Field(
        default=None, description="与前一收盘价相比的价格变化。"
    )
    change_percent: float | None = Field(
        default=None,
        description="作为归一化百分比的价格变化。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_high: float | None = Field(
        default=None, description="一年高点（52 周高点）。"
    )
    year_low: float | None = Field(
        default=None, description="一年低点（52 周低点）。"
    )
