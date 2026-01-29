"""绘图扩展查询参数。"""

# pylint: disable=unused-variable,unused-argument

from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, model_validator

from openbb_charting.core.plotly_ta.data_classes import ChartIndicators

MAMODES = Literal["ema", "sma", "wma", "hna", "zlma", "rma"]


def _get_type_name(t):
    """获取类型提示的类型名称。"""
    if hasattr(t, "__origin__"):
        if hasattr(t.__origin__, "__name__"):
            return f"{t.__origin__.__name__}[{', '.join([_get_type_name(arg) for arg in t.__args__])}]"
        if hasattr(t.__origin__, "_name"):
            return f"{t.__origin__._name}[{', '.join([_get_type_name(arg) for arg in t.__args__])}]"  # pylint: disable=W0212
    if isinstance(t, str):
        return t
    if hasattr(t, "__name__"):
        return t.__name__
    if hasattr(t, "_name"):
        return t._name  # pylint: disable=W0212
    return str(t)


class BaseQueryParams(QueryParams):
    """基本查询参数基本模型。"""

    def __init__(self, **data):
        """初始化基本查询参数。"""
        super().__init__(**data)
        self.__doc__ = self.__repr__()

    def __repr__(self):
        """返回模型的字符串表示形式。"""
        fields = self.__class__.model_fields
        repr_str = (
            "\n"
            + self.__class__.__name__
            + "\n\n"
            + "    Parameters\n"
            + "    ----------\n"
            + "\n".join(
                [
                    f"\n    {k} : {_get_type_name(v.annotation)}\n        {v.description}".replace(
                        ". ", ".\n        "
                    )
                    for k, v in fields.items()
                ]
            )
        )
        return repr_str


class ChartQueryParams(BaseQueryParams):
    """ChartParams."""

    data: Data | list[Data] | None = Field(
        default=None,
        description="Filtered versions of the data contained in the original `self.results`."
        + " Columns should be the same as the original data."
        + " Example use is to reduce the number of columns, or the length of data, to plot.",
    )


class EquityPricePerformanceChartQueryParams(ChartQueryParams):
    """股票价格表现图表查询参数。"""

    title: str | None = Field(
        default=None,
        description="Title of the chart.",
    )
    orientation: Literal["v", "h"] = Field(
        default="v",
        description="Orientation of the bars.",
    )
    limit: int | None = Field(
        default=None,
        description="Limit the number of bars to plot, from the most recent."
        + " If None, the periods from one-day to five-years will be plotted, if available.",
    )
    layout_kwargs: dict[str, Any] | None = Field(
        default=None,
        description="Additional keyword arguments to pass to the Plotly `update_layout` method.",
    )


class EtfPricePerformanceChartQueryParams(EquityPricePerformanceChartQueryParams):
    """ETF 价格表现图表查询参数。"""


class EtfHoldingsChartQueryParams(ChartQueryParams):
    """ETF 持仓图表查询参数。"""

    title: str | None = Field(
        default=None,
        description="Title of the chart.",
    )
    orientation: Literal["v", "h"] = Field(
        default="v",
        description="Orientation of the bars.",
    )
    limit: int | None = Field(
        default=20,
        description="Limit the number of bars to plot, ranked by top weighting.",
    )
    layout_kwargs: dict[str, Any] | None = Field(
        default=None,
        description="Additional keyword arguments to pass to the Plotly `update_layout` method.",
    )


class EquityPriceHistoricalChartQueryParams(ChartQueryParams):
    """股票历史价格图表查询参数。"""

    title: str | None = Field(
        default=None,
        description="Title of the chart.",
    )
    target: str | None = Field(
        default=None,
        description="The specific column to target. If supplied, this will override the candles and volume parameters.",
    )
    multi_symbol: bool = Field(
        default=False,
        description="Flag to indicate whether the data contains multiple symbols."
        + " This is mostly handled automatically, but if the chart fails to generate try setting this to True.",
    )
    same_axis: bool = Field(
        default=False,
        description="If True, forces all data to be plotted on the same axis.",
    )
    normalize: bool = Field(
        default=False,
        description="If True, the data will be normalized and placed on the same axis.",
    )
    returns: bool = Field(
        default=False,
        description="If True, the cumulative returns for the length of the time series will be calculated and plotted.",
    )
    candles: bool = Field(
        default=True,
        description="If True, and OHLC exists, and there is only one symbol in the data, candles will be plotted.",
    )
    heikin_ashi: bool = Field(
        default=False,
        description="If True, and `candles=True`, Heikin Ashi candles will be plotted.",
    )
    volume: bool = Field(
        default=True,
        description="If True, and volume exists, and `candles=True`, volume will be plotted.",
    )
    indicators: ChartIndicators | dict[str, dict[str, Any]] | None = Field(
        default=None,
        description="Indicators to be plotted, formatted as a dictionary."
        + " Data containing multiple symbols will ignore indicators."
        + """
        Example:
            indicators = dict(
                sma=dict(length=[20,30,50]),
                adx=dict(length=14),
                rsi=dict(length=14),
            )""",
    )


class EconomyFredSeriesChartQueryParams(ChartQueryParams):
    """FRED 系列图表查询参数。"""

    title: str | None = Field(
        default=None,
        description="Title of the chart.",
    )
    y1title: str | None = Field(
        default=None,
        description="Right Y-axis title.",
    )
    y2title: str | None = Field(
        default=None,
        description="Left Y-axis title.",
    )
    xtitle: str | None = Field(
        default=None,
        description="X-axis title.",
    )
    dropnan: bool = Field(
        default=True,
        description="If True, rows containing NaN will be dropped.",
    )
    normalize: bool = Field(
        default=False,
        description="If True, the data will be normalized and placed on the same axis.",
    )
    allow_unsafe: bool = Field(
        default=False,
        description="If True, the method will attempt to pass all supplied data to the chart constructor."
        + " This can result in unexpected behavior.",
    )
    plot_bar: bool = Field(
        default=False,
        description="If True, a bar chart will be plotted instead of a line."
        + " If multiple units of measure are present, they will be normalized and plotted on the same axis.",
    )
    barmode: Literal["stack", "group", "relative"] = Field(
        default="group",
        description="The mode to use for the bar chart, by default is 'group'."
        + " Has no effect if `bar=False`.",
    )
    layout_kwargs: dict[str, Any] | None = Field(
        default=None,
        description="Additional keyword arguments to pass to the Plotly `update_layout` method.",
    )


class TechnicalConesChartQueryParams(ChartQueryParams):
    """技术锥体图表查询参数。"""

    title: str | None = Field(
        default=None,
        description="Title of the chart.",
    )
    symbol: str | None = Field(
        default=None,
        description="Symbol represented by the data. Used to label the chart.",
    )


class MAQueryParams(ChartQueryParams):
    """移动平均查询参数。"""

    target: str = Field(
        default="close",
        description="The column to calculate the moving average on.",
    )
    index: str = Field(
        default="date",
        description="The index column.",
    )
    length: int | list[int] | None = Field(
        default=50,
        description="Window length for the moving average."
        "+ The number is relative to the interval of the time series data.",
    )
    offset: int | None = Field(
        default=0,
        description="Number of periods to offset for the moving average.",
    )
    dropnan: bool = Field(
        default=False,
        description="If True, rows containing NaN will be dropped."
        + " This will reduce the length of the charted data by the longest window.",
    )
    symbol: str | None = Field(
        default=None,
        description="Symbol represented by the data. Used to label the chart.",
    )


class FixedincomeGovernmentYieldCurve(ChartQueryParams):
    """固定收益政府收益率曲线图表查询参数。"""

    title: str | None = Field(
        default=None,
        description="Title of the chart.",
    )
    colors: list[str] | None = Field(
        default=None,
        description="List of colors to use for the lines.",
    )
    layout_kwargs: dict[str, Any] | None = Field(
        default=None,
        description="Additional keyword arguments to pass to the Plotly `update_layout` method.",
    )


class TechnicalSMAChartQueryParams(MAQueryParams):
    """技术 SMA 图表查询参数。"""


class TechnicalEMAChartQueryParams(MAQueryParams):
    """技术 EMA 图表查询参数。"""


class TechnicalHMAChartQueryParams(MAQueryParams):
    """技术 HMA 图表查询参数。"""


class TechnicalWMAChartQueryParams(MAQueryParams):
    """技术 WMA 图表查询参数。"""


class TechnicalZLMAChartQueryParams(MAQueryParams):
    """技术 ZLMA 图表查询参数。"""


class TechnicalADXChartQueryParams(ChartQueryParams):
    """技术 ADX 图表查询参数。"""

    length: int | None = Field(
        default=50,
        description="Window length for the ADX, by default is 50.",
    )
    scalar: float | None = Field(
        default=100,
        description="Scalar to multiply the ADX by, default is 100.",
    )
    drift: int | None = Field(
        default=1,
        description="Drift value for the ADX, by default is 1.",
    )


class TechnicalArooonChartQueryParams(ChartQueryParams):
    """技术 Aroon 图表查询参数。"""

    length: int | None = Field(
        default=25,
        description="Window length for the Aroon, by default is 50.",
    )
    scalar: float | None = Field(
        default=100,
        description="Scalar to multiply the Aroon by, default is 100.",
    )


class TechnicalMACDChartQueryParams(ChartQueryParams):
    """技术 MACD 图表查询参数。"""

    fast: int | None = Field(
        default=12,
        description="Window length for the fast EMA, by default is 12.",
    )
    slow: int | None = Field(
        default=26,
        description="Window length for the slow EMA, by default is 26.",
    )
    signal: int | None = Field(
        default=9,
        description="Window length for the signal line, by default is 9.",
    )
    scalar: float | None = Field(
        default=100,
        description="Scalar to multiply the MACD by, default is 100.",
    )


class TechnicalRSIChartQueryParams(ChartQueryParams):
    """技术 RSI 图表查询参数。"""

    length: int | None = Field(
        default=14,
        description="Window length for the RSI, by default is 14.",
    )
    scalar: float | None = Field(
        default=100,
        description="Scalar to multiply the RSI by, default is 100.",
    )
    drift: int | None = Field(
        default=1,
        description="Drift value for the RSI, by default is 1.",
    )


class TechnicalRelativeRotationChartQueryParams(ChartQueryParams):
    """技术相对旋转图表查询参数。"""

    date: str | None = Field(
        default=None,
        description="A target end date within the data to use for the chart, by default is the last date in the data.",
    )
    show_tails: bool = Field(
        default=True,
        description="Show the tails on the chart, by default True.",
    )
    tail_periods: int | None = Field(
        default=16,
        description="Number of periods to show in the tails, by default 16.",
    )
    tail_interval: Literal["day", "week", "month"] = Field(
        default="week",
        description="The interval to show the tails, by default 'week'.",
    )
    title: str | None = Field(
        default=None,
        description="Title of the chart.",
    )


class ChartParams:
    """图表查询参数。"""

    crypto_price_historical = EquityPriceHistoricalChartQueryParams
    derivatives_futures_historical = EquityPriceHistoricalChartQueryParams
    equity_price_historical = EquityPriceHistoricalChartQueryParams
    economy_fred_series = EconomyFredSeriesChartQueryParams
    equity_price_historical = EquityPriceHistoricalChartQueryParams
    equity_price_performance = EquityPricePerformanceChartQueryParams
    etf_historical = EtfPricePerformanceChartQueryParams
    etf_holdings = EtfHoldingsChartQueryParams
    etf_price_performance = EquityPricePerformanceChartQueryParams
    index_price_historical = EquityPriceHistoricalChartQueryParams
    technical_adx = TechnicalADXChartQueryParams
    technical_aroon = TechnicalArooonChartQueryParams
    technical_cones = TechnicalConesChartQueryParams
    technical_ema = TechnicalEMAChartQueryParams
    technical_hma = TechnicalHMAChartQueryParams
    technical_macd = TechnicalMACDChartQueryParams
    technical_relative_rotation = TechnicalRelativeRotationChartQueryParams
    technical_rsi = TechnicalRSIChartQueryParams
    technical_sma = TechnicalSMAChartQueryParams
    technical_wma = TechnicalWMAChartQueryParams
    technical_zlma = TechnicalZLMAChartQueryParams


class IndicatorsQueryParams(BaseQueryParams):
    """指标查询参数。"""


class MAIndicatorsQueryParams(IndicatorsQueryParams):
    """移动平均指标查询参数。"""

    length: int | list[int] = Field(
        default=50,
        description="Window length for the moving average, by default is 50."
        + " The number is relative to the interval of the time series data.",
    )
    offset: int = Field(
        default=0,
        description="Number of periods to offset for the moving average, by default is 0.",
    )


class SMAIndicatorsQueryParams(MAIndicatorsQueryParams):
    """简单移动平均指标查询参数。"""


class EMAIndicatorsQueryParams(MAIndicatorsQueryParams):
    """指数移动平均指标查询参数。"""


class HMAIndicatorsQueryParams(MAIndicatorsQueryParams):
    """赫尔移动平均指标查询参数。"""


class WMAIndicatorsQueryParams(MAIndicatorsQueryParams):
    """加权移动平均指标查询参数。"""


class ZLMAIndicatorsQueryParams(MAIndicatorsQueryParams):
    """零滞后移动平均指标查询参数。"""


class ADIndicatorsQueryParams(IndicatorsQueryParams):
    """累积/派发指标查询参数。"""

    offset: int = Field(
        default=0,
        description="Offset value for the AD, by default is 0.",
    )


class ADOscillatorIndicatorsQueryParams(IndicatorsQueryParams):
    """累积/派发震荡指标查询参数。"""

    fast: int = Field(
        default=3,
        description="Number of periods to use for the fast calculation, by default 3.",
    )
    slow: int = Field(
        default=10,
        description="Number of periods to use for the slow calculation, by default 10.",
    )
    offset: int = Field(
        default=0,
        description="Offset to be used for the calculation, by default is 0.",
    )


class ADXIndicatorsQueryParams(IndicatorsQueryParams):
    """平均趋向指数指标查询参数。"""

    length: int = Field(
        default=50,
        description="Window length for the ADX, by default is 50.",
    )
    scalar: float = Field(
        default=100,
        description="Scalar to multiply the ADX by, default is 100.",
    )
    drift: int = Field(
        default=1,
        description="Drift value for the ADX, by default is 1.",
    )


class AroonIndicatorsQueryParams(IndicatorsQueryParams):
    """Aroon 指标查询参数。"""

    length: int = Field(
        default=25,
        description="Window length for the Aroon, by default is 50.",
    )
    scalar: float = Field(
        default=100,
        description="Scalar to multiply the Aroon by, default is 100.",
    )


class ATRIndicatorsQueryParams(IndicatorsQueryParams):
    """平均真实范围指标查询参数。"""

    length: int = Field(
        default=14,
        description="Window length for the ATR, by default is 14.",
    )
    mamode: Literal["rma", "ema", "sma", "wma"] = Field(
        default="rma",
        description="The mode to use for the moving average calculation.",
    )
    drift: int = Field(
        default=1,
        description="The difference period.",
    )
    offset: int = Field(
        default=0,
        description="Number of periods to offset the result, by default is 0.",
    )


class CCIIndicatorsQueryParams(IndicatorsQueryParams):
    """商品通道指数指标查询参数。"""

    length: int = Field(
        default=14,
        description="Window length for the CCI, by default is 14.",
    )
    scalar: float = Field(
        default=0.015,
        description="Scalar to multiply the CCI by, default is 0.015.",
    )


class DonchianIndicatorsQueryParams(IndicatorsQueryParams):
    """唐奇安通道指标查询参数。"""

    lower: int | None = Field(
        default=20,
        description="Window length for the lower band, by default is 20.",
    )
    upper: int | None = Field(
        default=20,
        description="Window length for the upper band, by default is 20.",
    )
    offset: int | None = Field(
        default=0,
        description="Number of periods to offset the result, by default is 0.",
    )


class FisherIndicatorsQueryParams(IndicatorsQueryParams):
    """费舍尔变换指标查询参数。"""

    length: int = Field(
        default=14,
        description="Window length for the Fisher Transform, by default is 14.",
    )
    signal: int = Field(
        default=1,
        description="Fisher Signal Period",
    )


class KCIndicatorsQueryParams(IndicatorsQueryParams):
    """凯尔特纳通道指标查询参数。"""

    length: int = Field(
        default=20,
        description="Window length for the Keltner Channel, by default is 20.",
    )
    scalar: float = Field(
        default=2,
        description="Scalar to multiply the ATR, by default is 2.",
    )
    mamode: MAMODES = Field(
        default="rma",
        description="The mode to use for the moving average calculation, by default is ema.",
    )
    offset: int = Field(
        default=0,
        description="Number of periods to offset the result, by default is 0.",
    )


class MACDIndicatorsQueryParams(IndicatorsQueryParams):
    """MACD 指标查询参数。"""

    fast: int | None = Field(
        default=12,
        description="Window length for the fast EMA, by default is 12.",
    )
    slow: int | None = Field(
        default=26,
        description="Window length for the slow EMA, by default is 26.",
    )
    signal: int | None = Field(
        default=9,
        description="Window length for the signal line, by default is 9.",
    )
    scalar: float | None = Field(
        default=100,
        description="Scalar to multiply the MACD by, default is 100.",
    )


class OBVIndicatorsQueryParams(IndicatorsQueryParams):
    """能量潮指标查询参数。"""

    offset: int = Field(
        default=0,
        description="Number of periods to offset the result, by default is 0.",
    )


class RSIIndicatorsQueryParams(IndicatorsQueryParams):
    """RSI 指标查询参数。"""

    length: int = Field(
        default=14,
        description="Window length for the RSI, by default is 14.",
    )
    scalar: float = Field(
        default=100,
        description="Scalar to multiply the RSI by, default is 100.",
    )
    drift: int = Field(
        default=1,
        description="Drift value for the RSI, by default is 1.",
    )


class StochIndicatorsQueryParams(IndicatorsQueryParams):
    """随机震荡指标查询参数。"""

    fast_k: int = Field(
        default=14,
        description="The fast K period, by default 14.",
    )
    slow_d: int = Field(
        default=3,
        description="The slow D period, by default 3.",
    )
    slow_k: int = Field(
        default=3,
        description="The slow K period, by default 3.",
    )


class FibIndicatorsQueryParams(IndicatorsQueryParams):
    """斐波那契回撤指标查询参数。"""

    period: int = Field(
        default=120,
        description="The period to calculate the Fibonacci Retracement, by default 120.",
    )
    start_date: str | None = Field(
        default=None,
        description="The start date for the Fibonacci Retracement.",
    )
    end_date: str | None = Field(
        default=None,
        description="The end date for the Fibonacci Retracement.",
    )


class ClenowIndicatorsQueryParams(IndicatorsQueryParams):
    """Clenow 波动率调整动量指标查询参数。"""

    period: int = Field(
        default=90,
        description="The number of periods for the momentum, by default 90.",
    )


class DemarkIndicatorsQueryParams(IndicatorsQueryParams):
    """Demark 指标查询参数。"""

    show_all: bool = Field(
        default=False,
        description="Show 1 - 13. If set to False, show 6 - 9.",
    )
    offset: int = Field(
        default=0,
        description="Number of periods to offset the result, by default is 0.",
    )


class IchimokuIndicatorsQueryParams(IndicatorsQueryParams):
    """一目均衡表指标查询参数。"""

    conversion: int = Field(
        default=9,
        description="The conversion line period, by default 9.",
    )
    base: int = Field(
        default=26,
        description="The base line period, by default 26.",
    )
    lagging: int = Field(
        default=52,
        description="The lagging line period, by default 52.",
    )
    offset: int = Field(
        default=26,
        description="The offset period, by default 26.",
    )
    lookahead: bool = Field(
        default=False,
        description="Drops the Chikou Span Column to prevent potential data leak",
    )


class SRLinesIndicatorsQueryParams(IndicatorsQueryParams):
    """支撑线和阻力线指标查询参数。"""

    show: bool = Field(
        default=True,
        description="Show the support and resistance lines.",
    )


class IndicatorsParams(QueryParams):
    """指标查询参数。"""

    sma: SMAIndicatorsQueryParams = Field(
        default=SMAIndicatorsQueryParams(),
        description=repr(SMAIndicatorsQueryParams()),
    )
    ema: EMAIndicatorsQueryParams = Field(
        default=EMAIndicatorsQueryParams(),
        description=repr(EMAIndicatorsQueryParams()),
    )
    hma: HMAIndicatorsQueryParams = Field(
        default=HMAIndicatorsQueryParams(),
        description=repr(HMAIndicatorsQueryParams()),
    )
    wma: WMAIndicatorsQueryParams = Field(
        default=WMAIndicatorsQueryParams(),
        description=repr(WMAIndicatorsQueryParams()),
    )
    zlma: ZLMAIndicatorsQueryParams = Field(
        default=ZLMAIndicatorsQueryParams(),
        description=repr(ZLMAIndicatorsQueryParams()),
    )
    ad: ADIndicatorsQueryParams = Field(
        default=ADIndicatorsQueryParams(),
        description=repr(ADIndicatorsQueryParams()),
    )
    adoscillator: ADOscillatorIndicatorsQueryParams = Field(
        default=ADOscillatorIndicatorsQueryParams(),
        description=repr(ADOscillatorIndicatorsQueryParams()),
    )
    adx: ADXIndicatorsQueryParams = Field(
        default=ADXIndicatorsQueryParams(),
        description=repr(ADXIndicatorsQueryParams()),
    )
    aroon: AroonIndicatorsQueryParams = Field(
        default=AroonIndicatorsQueryParams(),
        description=repr(AroonIndicatorsQueryParams()),
    )
    atr: ATRIndicatorsQueryParams = Field(
        default=ATRIndicatorsQueryParams(),
        description=repr(ATRIndicatorsQueryParams()),
    )
    cci: CCIIndicatorsQueryParams = Field(
        default=CCIIndicatorsQueryParams(),
        description=repr(CCIIndicatorsQueryParams()),
    )
    clenow: ClenowIndicatorsQueryParams = Field(
        default=ClenowIndicatorsQueryParams(),
        description=repr(ClenowIndicatorsQueryParams()),
    )
    demark: DemarkIndicatorsQueryParams = Field(
        default=DemarkIndicatorsQueryParams(),
        description=repr(DemarkIndicatorsQueryParams()),
    )
    donchian: DonchianIndicatorsQueryParams = Field(
        default=DonchianIndicatorsQueryParams(),
        description=repr(DonchianIndicatorsQueryParams()),
    )
    fib: FibIndicatorsQueryParams = Field(
        default=FibIndicatorsQueryParams(),
        description=repr(FibIndicatorsQueryParams()),
    )
    fisher: FisherIndicatorsQueryParams = Field(
        default=FisherIndicatorsQueryParams(),
        description=repr(FisherIndicatorsQueryParams()),
    )
    ichimoku: IchimokuIndicatorsQueryParams = Field(
        default=IchimokuIndicatorsQueryParams(),
        description=repr(IchimokuIndicatorsQueryParams()),
    )
    kc: KCIndicatorsQueryParams = Field(
        default=KCIndicatorsQueryParams(),
        description=repr(KCIndicatorsQueryParams()),
    )
    macd: MACDIndicatorsQueryParams = Field(
        default=MACDIndicatorsQueryParams(),
        description=repr(MACDIndicatorsQueryParams()),
    )
    obv: OBVIndicatorsQueryParams = Field(
        default=OBVIndicatorsQueryParams(),
        description=repr(OBVIndicatorsQueryParams()),
    )
    rsi: RSIIndicatorsQueryParams = Field(
        default=RSIIndicatorsQueryParams(),
        description=repr(RSIIndicatorsQueryParams()),
    )
    srlines: SRLinesIndicatorsQueryParams = Field(
        default=SRLinesIndicatorsQueryParams(),
        description=repr(SRLinesIndicatorsQueryParams()),
    )
    stoch: StochIndicatorsQueryParams = Field(
        default=StochIndicatorsQueryParams(),
        description=repr(StochIndicatorsQueryParams()),
    )

    def __repr__(self):
        """返回模型的字符串表示形式。"""
        fields = self.__class__.model_fields
        repr_str = "\n" + "\n".join(
            [
                f"{str(v.description).replace('IndicatorsQueryParams', ':').replace('ADOs', 'AD Os')}"
                for k, v in fields.items()
            ]
        )
        return repr_str

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, values):
        """验证模型。"""
        indicators = list(ChartIndicators.get_available_indicators())
        for k, v in values.items():
            if k not in indicators:
                raise ValueError(f"{k} is not a valid indicator.")
        return values
