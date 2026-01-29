"""期权链标准模型。"""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.options_chains_properties import OptionsChainsProperties
from pydantic import Field, field_validator, model_serializer


class OptionsChainsQueryParams(QueryParams):
    """期权链查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """以大写形式返回股票代码。"""
        return v.upper()


class OptionsChainsData(OptionsChainsProperties):
    """期权链数据。

    注意：所附带的属性和方法仅在使用该类的实例时可用，
    该实例已使用经过验证的提供商数据初始化。下面的项绑定到函数输出中的 `results` 对象。

    属性
    ----------
    dataframe: DataFrame
        返回所有数据作为 Pandas DataFrame，包含额外的计算列（Breakeven, GEX, DEX，如有）。
    expirations: List[str]
        以字符串列表形式返回唯一的到期日。
    strikes: List[float]
        返回唯一的执行价列表。
    has_iv: bool
        如果数据包含隐含波动率，则返回 True。
    has_greeks: bool
        如果数据包含希腊字母值，则返回 True。
    total_oi: Dict
        将持仓量统计信息作为嵌套字典返回，包含键：total、expiration、strike。
        "expiration" 和 "strike" 都包含一系列记录，字段包括：Calls、Puts、Total、Net Percent、PCR。
    total_volume: Dict
        将成交量统计信息作为嵌套字典返回，包含键：total、expiration、strike。
        "expiration" 和 "strike" 都包含一系列记录，字段包括：Calls、Puts、Total、Net Percent、PCR。
    total_dex: Dict
        如果可用，将 Delta Dollars (DEX) 作为嵌套字典返回，包含键：total、expiration、strike。
        "expiration" 和 "strike" 都包含一系列记录，字段包括：Calls、Puts、Total、Net Percent、PCR。
    total_gex: Dict
        如果可用，将 Gamma Exposure (GEX) 作为嵌套字典返回，包含键：total、expiration、strike。
        "expiration" 和 "strike" 都包含一系列记录，字段包括：Calls、Puts、Total、Net Percent、PCR。
    last_price: float
        通过为此属性分配浮点值来手动设置标的价格。
        某些提供商/股票代码组合可能不会返回标的价格，
        在初始化后设置它可能是必要或理想的。
        此属性可用于覆盖提供商返回的标的价格。
        它不会自动设置，如果未设置，此属性将返回 None。

    方法
    -------
    filter_data(
        date: Optional[Union[str, int]] = None,
        column: Optional[str] = None,
        option_type: Optional[Literal["call", "put"]] = None,
        moneyness: Optional[Literal["otm", "itm"]] = None,
        value_min: Optional[float] = None,
        value_max: Optional[float] = None,
        stat: Optional[Literal["open_interest", "volume", "dex", "gex"]] = None,
        by: Literal["expiration", "strike"] = "expiration",
    ) -> DataFrame:
        按执行价或到期日返回统计信息；或者，返回过滤后的期权链数据。
    skew(
        date: Optional[Union[int, str]] = None, underlying_price: Optional[float] = None)
    -> DataFrame:
        按最近的 DTE 返回期权的偏度，垂直或水平。
    straddle(
        days: Optional[int] = None, strike: Optional[float] = None, underlying_price: Optional[float] = None
    ) -> DataFrame:
        按最近的 DTE 计算跨式期权的成本。卖出期权请使用负的执行价。
    strangle(
        days: Optional[int] = None, moneyness: Optional[float] = None, underlying_price: Optional[float] = None
    ) -> DataFrame:
        按最近的 DTE 和虚值百分比计算勒式期权的成本。
        卖出期权的虚值百分比请使用负值。
    synthetic_long(
        days: Optional[int] = None, strike: Optional[float] = None, underlying_price: Optional[float] = None
    ) -> DataFrame:
        按最近的 DTE 和执行价计算合成做多头寸的成本。
    synthetic_short(
        days: Optional[int] = None, strike: Optional[float] = None, underlying_price: Optional[float] = None
    ) -> DataFrame:
        按最近的 DTE 和执行价计算合成做空头寸的成本。
    vertical_call(
        days: Optional[int] = None, sold: Optional[float] = None, bought: Optional[float] = None,
        underlying_price: Optional[float] = None
    ) -> DataFrame:
        按最近的 DTE 以及卖出和买入层级的执行价计算垂直看涨价差的成本。
    vertical_put(
        days: Optional[int] = None, sold: Optional[float] = None, bought: Optional[float] = None,
        underlying_price: Optional[float] = None
    ) -> DataFrame:
        按最近的 DTE 以及卖出和买入层级的执行价计算垂直看跌价差的成本。
    strategies(
        days: Optional[int] = None,
        straddle_strike: Optional[float] = None,
        strangle_moneyness: Optional[List[float]] = None,
        synthetic_longs: Optional[List[float]] = None,
        synthetic_shorts: Optional[List[float]] = None,
        vertical_calls: Optional[List[tuple]] = None,
        vertical_puts: Optional[List[tuple]] = None,
        underlying_price: Optional[float] = None,
    ) -> DataFrame:
        在单个 DataFrame 中组合多种策略和参数的方法。
        要获取所有到期日，请将 days 设置为 -1。

    异常
    ------
    OpenBBError
    如果未找到所需的特定数据，访问属性和方法时将引发 OpenBBError。
    """

    underlying_symbol: list[str | None] = Field(
        default_factory=list,
        description="期权的标的股票代码。",
    )
    underlying_price: list[float | None] = Field(
        default_factory=list,
        description="标的股票的价格。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    contract_symbol: list[str] = Field(description="期权合约代码。")
    eod_date: list[dateType | None] = Field(
        default_factory=list,
        description="返回期权链的日期。",
    )
    expiration: list[dateType] = Field(description="合约到期日。")
    dte: list[int | None] = Field(
        default_factory=list, description="合约距离到期天数。"
    )
    strike: list[float] = Field(
        description="合约执行价。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    option_type: list[str] = Field(description="看涨期权或看跌期权 (Call or Put)。")
    contract_size: list[int | float | None] = Field(
        default_factory=list, description="每张合约对应的标的单位数量。"
    )
    open_interest: list[int | float | None] = Field(
        default_factory=list, description="合约持仓量。"
    )
    volume: list[int | float | None] = Field(
        default_factory=list, description=DATA_DESCRIPTIONS.get("volume", "")
    )
    theoretical_price: list[float | None] = Field(
        default_factory=list,
        description="期权理论价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    last_trade_price: list[float | None] = Field(
        default_factory=list,
        description="期权最新成交价。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    last_trade_size: list[int | float | None] = Field(
        default_factory=list, description="期权最新成交规模。"
    )
    last_trade_time: list[datetime | None] = Field(
        default_factory=list,
        description="最新成交的时间戳。",
    )
    tick: list[str | None] = Field(
        default_factory=list,
        description="上一价格跳动是向上还是向下。",
    )
    bid: list[float | None] = Field(
        default_factory=list,
        description="期权当前买入价。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    bid_size: list[int | float | None] = Field(
        default_factory=list, description="期权买入规模。"
    )
    bid_time: list[datetime | None] = Field(
        default_factory=list,
        description="买入价的时间戳。",
    )
    bid_exchange: list[str | None] = Field(
        default_factory=list, description="买入价所属交易所。"
    )
    ask: list[float | None] = Field(
        default_factory=list,
        description="期权当前卖出价。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ask_size: list[int | float | None] = Field(
        default_factory=list, description="期权卖出规模。"
    )
    ask_time: list[datetime | None] = Field(
        default_factory=list,
        description="卖出价的时间戳。",
    )
    ask_exchange: list[str | None] = Field(
        default_factory=list, description="卖出价所属交易所。"
    )
    mark: list[float | None] = Field(
        default_factory=list,
        description="最新买卖报价的中点价。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    open: list[float | None] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("open", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    open_bid: list[float | None] = Field(
        default_factory=list,
        description="该期权当日开盘买入价。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    open_ask: list[float | None] = Field(
        default_factory=list,
        description="该期权当日开盘卖出价。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    high: list[float | None] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("high", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    bid_high: list[float | None] = Field(
        default_factory=list,
        description="该期权当日最高买入价。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ask_high: list[float | None] = Field(
        default_factory=list,
        description="该期权当日最高卖出价。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    low: list[float | None] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("low", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    bid_low: list[float | None] = Field(
        default_factory=list,
        description="该期权当日最低买入价。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ask_low: list[float | None] = Field(
        default_factory=list,
        description="该期权当日最低卖出价。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    close: list[float | None] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("close", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    close_size: list[int | float | None] = Field(
        default_factory=list,
        description="该期权当日收盘成交规模。",
    )
    close_time: list[datetime | None] = Field(
        default_factory=list,
        description="该期权当日收盘价的时间。",
    )
    close_bid: list[float | None] = Field(
        default_factory=list,
        description="该期权当日收盘买入价。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    close_bid_size: list[int | float | None] = Field(
        default_factory=list,
        description="该期权当日收盘买入规模。",
    )
    close_bid_time: list[datetime | None] = Field(
        default_factory=list,
        description="该期权当日收盘买入价的时间。",
    )
    close_ask: list[float | None] = Field(
        default_factory=list,
        description="该期权当日收盘卖出价。",
    )
    close_ask_size: list[int | float | None] = Field(
        default_factory=list,
        description="该期权当日收盘卖出规模。",
    )
    close_ask_time: list[datetime | None] = Field(
        default_factory=list,
        description="该期权当日收盘卖出价的时间。",
    )
    prev_close: list[float | None] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("prev_close", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    change: list[float | None] = Field(
        default_factory=list, description="期权价格的变化。"
    )
    change_percent: list[float | None] = Field(
        default_factory=list,
        description="期权的价格百分比变化。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    implied_volatility: list[float | None] = Field(
        default_factory=list,
        description="期权隐含波动率。",
        json_schema_extra={"x-unit_measurement": "decimal"},
    )
    delta: list[float | None] = Field(
        default_factory=list,
        description="期权 Delta 值。",
        json_schema_extra={"x-unit_measurement": "decimal"},
    )
    gamma: list[float | None] = Field(
        default_factory=list,
        description="期权 Gamma 值。",
        json_schema_extra={"x-unit_measurement": "decimal"},
    )
    theta: list[float | None] = Field(
        default_factory=list,
        description="期权 Theta 值。",
        json_schema_extra={"x-unit_measurement": "decimal"},
    )
    vega: list[float | None] = Field(
        default_factory=list,
        description="期权 Vega 值。",
        json_schema_extra={"x-unit_measurement": "decimal"},
    )
    rho: list[float | None] = Field(
        default_factory=list,
        description="期权 Rho 值。",
        json_schema_extra={"x-unit_measurement": "decimal"},
    )

    @field_validator("expiration", mode="before", check_fields=False)
    @classmethod
    def _date_validate(cls, v):
        """从日期字符串返回 datetime 对象。"""
        if isinstance(v[0], datetime):
            return [datetime.strftime(d, "%Y-%m-%d") if d else None for d in v]
        if isinstance(v[0], str):
            return [datetime.strptime(d, "%Y-%m-%d") if d else None for d in v]
        return v

    @model_serializer
    def model_serialize(self):
        """返回序列化后的数据。"""
        data: dict = {}
        for field in self.model_fields:
            value = getattr(self, field)
            if isinstance(value, list):
                if value:  # Check if the list is not empty
                    if isinstance(value[0], datetime):
                        data[field] = [str(v) if v else None for v in value]
                    else:
                        data[field] = value
            else:
                data[field] = value

        records = [dict(zip(data.keys(), values)) for values in zip(*data.values())]

        return records
