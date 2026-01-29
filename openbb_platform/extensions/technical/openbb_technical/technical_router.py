"""技术分析路由器。"""

# pylint: disable=too-many-lines,unused-import,too-many-arguments,too-many-positional-arguments

from typing import Any, Literal

from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.utils import (
    basemodel_to_df,
    df_to_basemodel,
    get_target_column,
    get_target_columns,
)
from openbb_core.provider.abstract.data import Data
from pydantic import NonNegativeFloat, NonNegativeInt, PositiveFloat, PositiveInt

from openbb_technical.helpers import (
    calculate_cones,
    calculate_fib_levels,
    clenow_momentum,
    validate_data,
)
from openbb_technical.relative_rotation import (
    RelativeRotationData,
    RelativeRotationFetcher,
    RelativeRotationQueryParams,
)

# TODO: Split this into multiple files
router = Router(prefix="", description="技术分析工具。")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="计算一组代码相对于基准的相对强度比率和相对强度动量。",
            code=[
                "stock_data = obb.equity.price.historical("
                + "symbol='AAPL,MSFT,GOOGL,META,AMZN,TSLA,SPY', start_date='2022-01-01', provider='yfinance')",
                "rr_data = obb.technical.relative_rotation(data=stock_data.results, benchmark='SPY')",
                "rs_ratios = rr_data.results.rs_ratios",
                "rs_momentum = rr_data.results.rs_momentum",
            ],
        ),
        PythonEx(
            description="当资产不是每年 252 天交易时，相应地调整势头和波动率周期。",
            code=[
                "crypto_data = obb.crypto.price.historical("
                + " symbol='BTCUSD,ETHUSD,SOLUSD', start_date='2021-01-01', provider='yfinance')",
                "rr_data = obb.technical.relative_rotation(data=crypto_data.results, benchmark='BTC-USD',"
                + " long_period=365, short_period=30, window=30, trading_periods=365)",
            ],
        ),
    ],
)
async def relative_rotation(
    data: list[Data],
    benchmark: str,
    study: Literal["price", "volume", "volatility"] = "price",
    long_period: int | None = 252,
    short_period: int | None = 21,
    window: int | None = 21,
    trading_periods: int | None = 252,
    chart_params: dict[str, Any] | None = None,
) -> OBBject[RelativeRotationData]:
    """计算一组代码相对于基准的相对强度比率和相对强度动量。

    Parameters
    ----------
    data : list[Data]
        用于相对旋转计算的数据。
        这应该是 'equity.price.historical' 端点的多代码输出，或类似输出。
        或者是透视表，其中 'date' 列为索引，代码为列，'study' 为值。
        建议使用 'equity.price.historical' 端点获取数据，并将结果按原样输入。
    benchmark : str
        用作基准的代码。
    study : Literal[price, volume, volatility]
        用于计算的数据点。如果为 'price'，将使用收盘价。
        如果为 'volatility'，将使用收盘价的标准差。
        如果 'data' 以透视表形式提供，
        'study' 将假定值为收盘价，'volume' 将被忽略。
    long_period : int, optional
        用于动量计算的长周期长度，默认为 252。
        当提供非每日间隔的时间序列时，请调整此值。
        例如，如果数据是月度的，则长周期应为 12。
    short_period : int, optional
        用于动量计算的短周期长度，默认为 21。
        当提供非每日间隔的时间序列时，请调整此值。
    window : int, optional
        用于标准差计算的窗口长度，默认为 21。
        当提供非每日间隔的时间序列时，请调整此值。
    trading_periods : int, optional
        每年交易周期数，用于标准差计算，默认为 252。
        当提供非每日间隔的时间序列时，请调整此值。
    chart_params : dict[str, Any], optional
        当 `chart=True` 且安装了 `openbb-charting` 扩展时传递的其他参数。
        可以再次传递参数以使用响应的 charting.to_chart() 方法重绘图表。

        ChartParams
        -----------
        date : str, optional
            数据中用于图表的目标结束日期，默认为数据中的最后日期。
        show_tails : bool
            在图表上显示尾部，默认为 True。
        tail_periods : int
            尾部显示的周期数，默认为 16。
        tail_interval : Literal[day, week, month]
            显示尾部的间隔，默认为 'week'。
        title : str, optional
            图表的标题。

    Returns
    -------
    OBBject[RelativeRotationData]
        results : RelativeRotationData
            symbols : list[str]:
                正在与基准进行比较的代码。
            benchmark : str
                基准代码。
            study : Literal[price, volume, volatility]
                所选的数据点。
            long_period : int
                用户输入的用于动量计算的长周期长度。
            short_period : int
                用户输入的用于动量计算的短周期长度。
            window : int
                用于标准差计算的窗口长度。
            trading_periods : int
                每年交易周期数，用于标准差计算。
            start_date : str
                调整计算数据长度后的数据开始日期。
            end_date : str
                数据结束日期。
            symbols_data : list[Data]
                代表每个代码所选 'study' 的数据。
            benchmark_data : list[Data]
                代表基准所选 'study' 的数据。
            rs_ratios : list[Data]
                归一化相对强度比率数据。
            rs_momentum : list[Data]
                归一化相对强度动量数据。
    """
    params = RelativeRotationQueryParams(
        data=data,
        benchmark=benchmark,
        study=study,
        long_period=long_period,
        short_period=short_period,
        window=window,
        trading_periods=trading_periods,
        chart_params=chart_params,
    )

    return OBBject(
        results=RelativeRotationFetcher.transform_data(
            params, RelativeRotationFetcher.extract_data(params, {})
        )
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="获取平均真实波幅。",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "atr_data = obb.technical.atr(data=stock_data.results)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def atr(
    data: list[Data],
    index: str = "date",
    length: PositiveInt = 14,
    mamode: Literal["rma", "ema", "sma", "wma"] = "rma",
    drift: NonNegativeInt = 1,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """计算平均真实波幅。

    用于衡量波动性，尤其是由缺口或限价移动引起的波动性。
    ATR 指标有助于了解您的数据中的值平均变化多少，
    从而深入了解特定时期的稳定性或不可预测性。
    它对于发现变动幅度增加或减少的趋势特别有用，
    而无需通过技术交易细节。
    该方法不仅考虑日常变化，还考虑任何
    突然跳升或下降，确保您获得全面的运动视图。

    Parameters
    ----------
    data : list[Data]
        应用指标的数据列表。
    index : str, optional
        索引列名，默认为 "date"
    length : PositiveInt, optional
        周期，默认为 14
    mamode : Literal["rma", "ema", "sma", "wma"], optional
        移动平均模式，默认为 "rma"
    drift : NonNegativeInt, optional
        差分周期，默认为 1
    offset : int, optional
        结果偏移多少个周期，默认为 0

    Returns
    -------
    OBBject[list[Data]]
        应用了指标的数据列表。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, length)
    df = basemodel_to_df(data, index=index)
    df_target = get_target_columns(df, ["high", "low", "close"])
    df_atr = pd.DataFrame(
        df_target.ta.atr(length=length, mamode=mamode, drift=drift, offset=offset)
    )

    output = pd.concat([df, df_atr], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="获取布林带带宽。",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "fib_data = obb.technical.fib(data=stock_data.results, period=120)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def fib(
    data: list[Data],
    index: str = "date",
    close_column: Literal["close", "adj_close"] = "close",
    period: PositiveInt = 120,
    start_date: str | None = None,
    end_date: str | None = None,
) -> OBBject[list[Data]]:
    """创建斐波那契回撤水平。

    这种方法利用经典技术来确定重要的价格水平，
    这通常表明市场可能会在哪里找到支撑或阻力。
    它是一种工具，通过应用植根于自然模式的数学方法
    来衡量数据中的潜在转折点。用于深入了解
    根据历史变动，价格接下来可能会走向何方。

    Parameters
    ----------
    data : list[Data]
        应用指标的数据列表。
    index : str, optional
        索引列名，默认为 "date"
    period : PositiveInt, optional
        计算指标的周期，默认为 120

    Returns
    -------
    OBBject[list[Data]]
        应用了指标的数据列表。
    """
    df = basemodel_to_df(data, index=index)

    (
        df_fib,
        min_date,
        max_date,
        min_pr,
        max_pr,
        lvl_text,
    ) = calculate_fib_levels(
        data=df,
        close_col=close_column,
        limit=period,
        start_date=start_date,
        end_date=end_date,
    )

    df_fib["min_date"] = min_date
    df_fib["max_date"] = max_date
    df_fib["min_pr"] = min_pr
    df_fib["max_pr"] = max_pr
    df_fib["lvl_text"] = lvl_text

    results = df_to_basemodel(df_fib)

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="获取能量潮指标 (OBV)。",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "obv_data = obb.technical.obv(data=stock_data.results, offset=0)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def obv(
    data: list[Data],
    index: str = "date",
    offset: int = 0,
) -> OBBject[list[Data]]:
    """计算能量潮指标 (OBV)。

    它是上涨和下跌成交量的累计总和。当收盘价高于
    前一收盘价时，成交量被加到累计总和中；当收盘价
    低于前一收盘价时，成交量从累计总和中减去。

    要解释 OBV，请观察 OBV 是否随价格移动或先于价格移动。
    如果价格先于 OBV 移动，则这是一个未确认的移动。一系列上升的峰值，
    或下降的谷底，在 OBV 中表明这一强劲趋势。如果 OBV 持平，则市场
    没有趋势。

    Parameters
    ----------
    data : list[Data]
        应用指标的数据列表。
    index : str, optional
        索引列名，默认为 "date"
    offset : int, optional
        结果偏移多少个周期，默认为 0。

    Returns
    -------
    OBBject[list[Data]]
        应用了指标的数据列表。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    df = basemodel_to_df(data, index=index)
    df_target = get_target_columns(df, ["close", "volume"])
    df_obv = pd.DataFrame(df_target.ta.obv(offset=offset))

    output = pd.concat([df, df_obv], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="执行费舍尔变换。",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "fisher_data = obb.technical.fisher(data=stock_data.results, length=14, signal=1)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def fisher(
    data: list[Data],
    index: str = "date",
    length: PositiveInt = 14,
    signal: PositiveInt = 1,
) -> OBBject[list[Data]]:
    """执行费舍尔变换。

    由 John F. Ehlers 创建的技术指标，将价格转换为高斯
    正态分布。该指标突出显示价格何时变动到极端，
    基于近期价格。
    这可能有助于发现资产价格的转折点。它也有助于
    显示趋势并在趋势中隔离价格波浪。

    Parameters
    ----------
    data : list[Data]
        list of data to apply the indicator to.
    index : str, optional
        Index column name, by default "date"
    length : PositiveInt, optional
        Fisher period, by default 14
    signal : PositiveInt, optional
        Fisher Signal period, by default 1

    Returns
    -------
    OBBject[list[Data]]
        list of data with the indicator applied.
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, [length, signal])
    df = basemodel_to_df(data, index=index)
    df_target = get_target_columns(df, ["high", "low"])
    df_fisher = pd.DataFrame(df_target.ta.fisher(length=length, signal=signal))

    output = pd.concat([df, df_fisher], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="获取累积/派发震荡指标。",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "adosc_data = obb.technical.adosc(data=stock_data.results, fast=3, slow=10, offset=0)",
            ],
        ),
        APIEx(parameters={"fast": 2, "slow": 4, "data": APIEx.mock_data("timeseries")}),
    ],
)
def adosc(
    data: list[Data],
    index: str = "date",
    fast: PositiveInt = 3,
    slow: PositiveInt = 10,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """计算累积/派发震荡指标。

    也称为 Chaikin 震荡指标。

    本质上是一种动量指标，但针对积累-分布线
    而不仅仅是价格。它既观察价格变动的强度，也观察
    给定时间段内的基本买入和卖出压力。震荡指标
    读数高于零表示净买入压力，而低于零则表示
    净卖出压力。指标与纯价格变动之间的背离是
    该指标最常见的信号，通常标志着市场转折点。

    Parameters
    ----------
    data : list[Data]
        要用于计算的数据列表。
    fast : PositiveInt, optional
        用于快速计算的周期数，默认为 3。
    slow : PositiveInt, optional
        用于慢速计算的周期数，默认为 10。
    offset : int, optional
        用于计算的偏移量，默认为 0。

    Returns
    -------
    OBBject[list[Data]]
        计算后的数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, [fast, slow])
    df = basemodel_to_df(data, index=index)
    df_target = get_target_columns(df, ["open", "high", "low", "close", "volume"])
    df_adosc = pd.DataFrame(df_target.ta.adosc(fast=fast, slow=slow, offset=offset))

    output = pd.concat([df, df_adosc], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="获取钱德动量摆动指标。",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "bbands_data = obb.technical.bbands(data=stock_data.results, target='close', length=50, std=2, mamode='sma')",  # noqa: E501
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def bbands(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    std: NonNegativeFloat = 2,
    mamode: Literal["sma", "ema", "wma", "rma"] = "sma",
    offset: int = 0,
) -> OBBject[list[Data]]:
    """计算布林带。

    由三条线组成。中间带是典型价格 (TP) 的简单移动平均线（通常为 20
    个周期）。上下带是中间带上下 F 个标准
    差（通常为 2）。
    当价格波动率较高或较低时，波段分别变宽和变窄。

    布林带本身并不产生买入或卖出信号；
    它们是指示超买或超卖情况的指标。当价格接近
    上带或下带时，表明可能即将发生反转。中间带
    成为支撑或阻力水平。上带和下带也可以
    解释为价格目标。当价格从下带反弹并穿过
    中间带时，上带成为价格目标。

    Parameters
    ----------
    data : list[Data]
        要用于计算的数据列表。
    target : str
        目标列名。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"。
    length : int, optional
        用于计算的周期数，默认为 50。
    std : NonNegativeFloat, optional
        用于计算的标准差，默认为 2。
    mamode : Literal["sma", "ema", "wma", "rma"], optional
        用于计算的移动平均模式，默认为 "sma"。
    offset : int, optional
        用于计算的偏移量，默认为 0。

    Returns
    -------
    OBBject[list[Data]]
        计算后的数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, length)
    df = basemodel_to_df(data, index=index)
    df_target = get_target_column(df, target).to_frame()
    bbands_df = pd.DataFrame(
        df_target.ta.bbands(
            length=length,
            std=std,
            mamode=mamode,
            offset=offset,
            close=target,
            prefix=target,
        )
    )

    output = pd.concat([df, bbands_df], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Chande Momentum Oscillator.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "zlma_data = obb.technical.zlma(data=stock_data.results, target='close', length=50, offset=0)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def zlma(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """计算零滞后指数移动平均线 (ZLEMA)。

    由 John Ehlers 和 Ric Way 创建。其想法是进行
    常规指数移动平均 (EMA) 计算，但在
    去滞后数据上进行，而不是在常规数据上进行。
    数据通过移除“滞后”天前的数据进行去滞后，
    从而消除（或试图消除）移动平均线的累积效应。

    Parameters
    ----------
    data : list[Data]
        要用于计算的数据列表。
    target : str
        目标列名。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"。
    length : int, optional
        用于计算的周期数，默认为 50。
    offset : int, optional
        用于计算的偏移量，默认为 0。

    Returns
    -------
    OBBject[list[Data]]
        计算后的数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, length)
    df = basemodel_to_df(data, index=index)
    df_target = get_target_column(df, target).to_frame()
    zlma_df = pd.DataFrame(
        df_target.ta.zlma(
            length=length,
            offset=offset,
            close=target,
            prefix=target,
        )
    ).dropna()

    output = pd.concat([df, zlma_df], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Chande Momentum Oscillator.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "aaron_data = obb.technical.aroon(data=stock_data.results, length=25, scalar=100)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def aroon(
    data: list[Data],
    index: str = "date",
    length: int = 25,
    scalar: float = 100,
) -> OBBject[list[Data]]:
    """计算阿隆指标。

    词语 aroon 在梵语中意为“黎明的曙光”。阿隆
    指标试图显示新趋势何时出现。该指标由
    两条线（上升和下降）组成，衡量自 n 周期范围内出现最高高点/最低低点以来
    经过了多长时间。

    当阿隆上升线保持在 70 和 100 之间时，表明呈上升趋势。
    当阿隆下降线保持在 70 和 100 之间时，表明呈下降趋势。
    当阿隆上升线高于 70 而阿隆下降线低于 30 时，表明呈强劲上升趋势。
    同样，当阿隆下降线高于 70 而阿隆上升线低于 30 时，表明呈强劲下降趋势。
    还要寻找交叉点。当阿隆下降线向上穿过
    阿隆上升线时，表明上升趋势减弱（反之亦然）。

    Parameters
    ----------
    data : list[Data]
        要用于计算的数据列表。
    index: str, optional
        用于 `data` 的索引列名，默认为 "date"。
    length : int, optional
        用于计算的周期数，默认为 25。
    scalar : float, optional
        用于计算的标量，默认为 100。

    Returns
    -------
    OBBject[list[Data]]
        计算后的数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, length)
    df = basemodel_to_df(data, index=index)
    df_target = get_target_columns(df, ["high", "low", "close"])
    df_aroon = pd.DataFrame(df_target.ta.aroon(length=length, scalar=scalar)).dropna()

    output = pd.concat([df, df_aroon], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Chande Momentum Oscillator.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "sma_data = obb.technical.sma(data=stock_data.results, target='close', length=50, offset=0)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def sma(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """计算简单移动平均线 (SMA)。

    移动平均线用于平滑数组中的数据，以
    帮助消除噪音并识别趋势。简单移动平均线实际上是
    移动平均线的最简单形式。每个输出值是
    前 n 个值的平均值。在简单移动平均线中，时间段内的每个值具有
    相等的权重，时间段之外的值不包括在平均值中。
    这使其对数据的近期变化反应较慢，这对于
    过滤掉这些变化很有用。

    Parameters
    ----------
    data : list[Data]
        要用于计算的数据列表。
    target : str
        目标列名。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"。
    length : int, optional
        用于计算的周期数，默认为 50。
    offset : int, optional
        距当前周期的偏移量，默认为 0。

    Returns
    -------
    OBBject[list[Data]]
        计算后的数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, length)
    df = basemodel_to_df(data, index=index)
    df_target = get_target_column(df, target).to_frame()
    sma_df = pd.DataFrame(
        df_target.ta.sma(
            length=length,
            offset=offset,
            close=target,
            prefix=target,
        ).dropna()
    )

    output = pd.concat([df, sma_df], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Demark Sequential Indicator.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "demark_data = obb.technical.demark(data=stock_data.results, offset=0)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def demark(
    data: list[Data],
    index: str = "date",
    target: str = "close",
    show_all: bool = True,
    asint: bool = True,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """计算 Demark 顺序指标。

    该指标提供了一种识别市场趋势潜在逆转的战略方法。
    如同该指标旨在突出当前趋势可能耗尽动力的时刻，
    表明方向可能发生转变。通过关注价格变动中的特定模式，它提供了
    对未来变化做出明智决策的宝贵见解，并识别趋势衰竭点
    具有精确性。

    Parameters
    ----------
    data : list[Data]
        要用于计算的数据列表。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"。
    target : str, optional
        目标列名，默认为 "close"。
    show_all : bool, optional
        显示 1 - 13。如果设置为 False，显示 6 - 9。
    asint : bool, optional
        如果为 True，用 0 填充 NA 并将类型更改为 int，默认为 True。
    offset : int, optional
        结果偏移多少个周期

    Returns
    -------
    OBBject[list[Data]]
        计算后的数据，字段为：[{index}, {target}, "up", "down"]
    """
    # pylint: disable=import-outside-toplevel
    import pandas_ta as ta  # noqa
    from pandas import concat

    df = basemodel_to_df(data, index=index)
    df_target = get_target_column(df, target).to_frame()
    _demark = ta.exhc(df_target[target], asint=asint, show_all=show_all, offset=offset)
    demark_df = concat([df[[target]], _demark], axis=1).reset_index()
    demark_df = demark_df.rename(columns={"EXHC_DNa": "down", "EXHC_UPa": "up"})
    results = df_to_basemodel(demark_df)

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Volume Weighted Average Price (VWAP).",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "vwap_data = obb.technical.vwap(data=stock_data.results, anchor='D', offset=0)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def vwap(
    data: list[Data],
    index: str = "date",
    anchor: str = "D",
    offset: int = 0,
) -> OBBject[list[Data]]:
    """计算成交量加权平均价格 (VWAP)。

    衡量按成交量加权的平均典型价格。
    它通常用于日内图表以识别总体方向。
    它有助于了解考虑交易量的真实平均价格，
    并作为评估市场在短期内（如单个交易日）方向的基准。

    Parameters
    ----------
    data : list[Data]
        要用于计算的数据列表。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"。
    anchor : str, optional
        用于计算的锚定周期，默认为 "D"。
        有关其他选项，请参见下面的时间序列偏移别名：
        https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases
    offset : int, optional
        距当前周期的偏移量，默认为 0。

    Returns
    -------
    OBBject[list[Data]]
        计算后的数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    df = basemodel_to_df(data, index=index)
    if index == "date":
        df.index = pd.to_datetime(df.index)
    df_target = get_target_columns(df, ["high", "low", "close", "volume"])
    df_vwap = pd.DataFrame(df_target.ta.vwap(anchor=anchor, offset=offset).dropna())

    output = pd.concat([df, df_vwap], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Moving Average Convergence Divergence (MACD).",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "macd_data = obb.technical.macd(data=stock_data.results, target='close', fast=12, slow=26, signal=9)",
            ],
        ),
        APIEx(
            description="Example with mock data.",
            parameters={
                "fast": 2,
                "slow": 3,
                "signal": 1,
                "data": APIEx.mock_data("timeseries"),
            },
        ),
    ],
)
def macd(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> OBBject[list[Data]]:
    """计算移动平均收敛散度 (MACD)。

    两条指数移动平均线之间的差异。信号线是
    MACD 的指数移动平均线。

    MACD 发出趋势变化信号并指示新趋势方向的开始。
    高值表示超买情况，低值表示超卖情况。
    与价格的背离表明当前趋势结束，特别是如果
    MACD 处于极高或极低值。当 MACD 线上穿
    信号线时，产生买入信号。当 MACD 下穿信号线时，产生
    卖出信号。为了确认信号，MACD 应高于零为买入，
    低于零为卖出。

    Parameters
    ----------
    data : list[Data]
        要用于计算的数据列表。
    target : str
        目标列名。
    fast : int, optional
        快速 EMA 的周期数，默认为 12。
    slow : int, optional
        慢速 EMA 的周期数，默认为 26。
    signal : int, optional
        信号 EMA 的周期数，默认为 9。

    Returns
    -------
    OBBject[list[Data]]
        计算后的数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, [fast, slow, signal])
    df = basemodel_to_df(data, index=index)
    df_target = get_target_column(df, target).to_frame()
    macd_df = pd.DataFrame(
        df_target.ta.macd(
            fast=fast,
            slow=slow,
            signal=signal,
            close=target,
            prefix=target,
        ).dropna()
    )
    output = pd.concat([df, macd_df], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Calculate HMA with historical stock data.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "hma_data = obb.technical.hma(data=stock_data.results, target='close', length=50, offset=0)",
            ],
        ),
    ],
)
def hma(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """计算赫尔移动平均线 (HMA)。

    解决了使移动平均线对当前
    价格活动更敏感同时保持曲线平滑的古老困境。
    事实上，HMA 几乎完全消除了滞后，并设法同时改善平滑度
    。

    Parameters
    ----------
    data : list[Data]
        要用于计算的数据列表。
    target : str
        目标列名。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"。
    length : int, optional
        HMA 的周期数，默认为 50。
    offset : int, optional
        HMA 的偏移量，默认为 0。

    Returns
    -------
    OBBject[list[Data]]
        计算后的数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, length)
    df = basemodel_to_df(data, index=index)
    df_target = get_target_column(df, target).to_frame()
    hma_df = pd.DataFrame(
        df_target.ta.hma(
            length=length,
            offset=offset,
            close=target,
            prefix=target,
        ).dropna()
    )

    output = pd.concat([df, hma_df], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Donchian Channels.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "donchian_data = obb.technical.donchian(data=stock_data.results, lower_length=20, upper_length=20, offset=0)",  # noqa: E501
            ],
        ),
        APIEx(
            parameters={
                "lower_length": 1,
                "upper_length": 3,
                "data": APIEx.mock_data("timeseries"),
            }
        ),
    ],
)
def donchian(
    data: list[Data],
    index: str = "date",
    lower_length: PositiveInt = 20,
    upper_length: PositiveInt = 20,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """计算唐奇安通道。

    由移动平均线计算生成的三条线组成的指标，
    由围绕中程或中位带的上下带形成。上带
    标记证券在 N 个周期内的最高价格，而下带
    标记证券在 N 个周期内的最低价格。
    上下带之间的区域代表唐奇安通道。

    Parameters
    ----------
    data : list[Data]
        要用于计算的数据列表。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"。
    lower_length : PositiveInt, optional
        下带的周期数，默认为 20。
    upper_length : PositiveInt, optional
        上带的周期数，默认为 20。
    offset : int, optional
        唐奇安通道的偏移量，默认为 0。

    Returns
    -------
    OBBject[list[Data]]
        计算后的数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, [lower_length, upper_length])
    df = basemodel_to_df(data, index=index)
    df_target = get_target_columns(df, ["high", "low"])
    donchian_df = pd.DataFrame(
        df_target.ta.donchian(
            lower_length=lower_length, upper_length=upper_length, offset=offset
        ).dropna()
    )

    output = pd.concat([df, donchian_df], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Ichimoku Cloud.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "ichimoku_data = obb.technical.ichimoku(data=stock_data.results, conversion=9, base=26, lookahead=False)",
            ],
        ),
    ],
)
def ichimoku(
    data: list[Data],
    index: str = "date",
    conversion: PositiveInt = 9,
    base: PositiveInt = 26,
    lagging: PositiveInt = 52,
    offset: PositiveInt = 26,
    lookahead: bool = False,
) -> OBBject[list[Data]]:
    """计算一目均衡图 (Ichimoku Cloud)。

    也被称为 Ichimoku Kinko Hyo，是一种多功能指标，定义了支撑和
    阻力，识别趋势方向，衡量动量并提供交易
    信号。Ichimoku Kinko Hyo 翻译为“一瞥均衡图”。通过
    一瞥，图表分析师可以识别趋势并在该趋势内寻找潜在信号
    。

    Parameters
    ----------
    data : list[Data]
        用于计算的数据列表。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"。
    conversion : PositiveInt, optional
        转换线的周期数，默认为 9。
    base : PositiveInt, optional
        基准线的周期数，默认为 26。
    lagging : PositiveInt, optional
        滞后跨度的周期数，默认为 52。
    offset : PositiveInt, optional
        偏移的周期数，默认为 26。
    lookahead : bool, optional
        删除 Chikou Span 列以防止潜在的数据泄漏

    Returns
    -------
    OBBject[list[Data]]
        计算后的数据。
    """
    validate_data(data, [conversion, base, lagging])
    df = basemodel_to_df(data, index=index)
    df_target = get_target_columns(df, ["high", "low", "close"])
    df_ichimoku, df_span = df_target.ta.ichimoku(
        tenkan=conversion,
        kijun=base,
        senkou=lagging,
        offset=offset,
        lookahead=lookahead,
    )

    df_result = df.join(df_span.add_prefix("span_"), how="left")
    df_result = df_result.join(df_ichimoku, how="left")

    results = df_to_basemodel(df_result.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Clenow Volatility Adjusted Momentum.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "clenow_data = obb.technical.clenow(data=stock_data.results, period=90)",
            ],
        ),
        APIEx(parameters={"period": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def clenow(
    data: list[Data],
    index: str = "date",
    target: str = "close",
    period: PositiveInt = 90,
) -> OBBject[list[Data]]:
    """计算 Clenow 波动率调整动量。

    Clenow 波动率调整动量是一种理解市场动量的复杂方法。
    它调整了波动率，通过考虑价格变动在设定时期内受其波动率的影响，
    提供了真实动量的更清晰图景。它有助于识别更强、更可靠的趋势。

    Parameters
    ----------
    data : list[Data]
        要用于计算的数据列表。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"。
    target : str, optional
        目标列名，默认为 "close"。
    period : PositiveInt, optional
        动量的周期数，默认为 90。

    Returns
    -------
    OBBject[list[Data]]
        计算后的数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, period)
    df = basemodel_to_df(data, index=index)
    df_target = get_target_column(df, target)

    r2, coef, _ = clenow_momentum(df_target, period)

    df_clenow = pd.DataFrame.from_dict(
        {
            "r^2": f"{r2:.5f}",
            "fit_coef": f"{coef:.5f}",
            "factor": f"{coef * r2:.5f}",
        },
        orient="index",
    ).transpose()

    output = pd.concat([df, df_clenow], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Accumulation/Distribution Line.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "ad_data = obb.technical.ad(data=stock_data.results, offset=0)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def ad(data: list[Data], index: str = "date", offset: int = 0) -> OBBject[list[Data]]:
    """计算累积/派发线。

    类似于能量潮指标 (OBV)。
    根据收盘价是否高于前一收盘价，将成交量乘以 +1/-1 求和。
    然而，累积/派发指标将成交量乘以
    收盘位置值 (CLV)。CLV 基于单根柱线内的变动，
    可以是 +1、-1 或零。

    通过观察指标相对于价格的方向背离来解释累积/派发线。
    如果累积/派发线呈上升趋势，则表明价格可能会随之上升。
    此外，如果累积/派发线变平而价格仍在上升（或下降），
    则表明价格即将变平。

    Parameters
    ----------
    data : list[Data]
        要用于计算的数据列表。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"。
    offset : int, optional
        AD 的偏移量，默认为 0。

    Returns
    -------
    OBBject[list[Data]]
        计算后的数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    df = basemodel_to_df(data, index=index)
    df_target = get_target_columns(df, ["high", "low", "close", "volume"])
    ad_df = pd.DataFrame(df_target.ta.ad(offset=offset).dropna())

    output = pd.concat([df, ad_df], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Average Directional Index (ADX).",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "adx_data = obb.technical.adx(data=stock_data.results, length=50, scalar=100.0, drift=1)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def adx(
    data: list[Data],
    index: str = "date",
    length: int = 50,
    scalar: float = 100.0,
    drift: int = 1,
) -> OBBject[list[Data]]:
    """计算平均趋向指数 (ADX)。

    ADX 是趋向指标 (DX) 的 Welles Wilder 风格的移动平均线。
    值的范围从 0 到 100，但很少超过 60。要解释 ADX，请将
    高数值视为强趋势，低数值视为弱趋势。

    Parameters
    ----------
    data : list[Data]
        要用于计算的数据列表。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"。
    length : int, optional
        ADX 的周期数，默认为 50。
    scalar : float, optional
        ADX 的标量值，默认为 100.0。
    drift : int, optional
        ADX 的漂移值，默认为 1。

    Returns
    -------
    OBBject[list[Data]]
        计算后的数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, length)
    df = basemodel_to_df(data, index=index)
    df_target = get_target_columns(df, ["close", "high", "low"])
    df_adx = pd.DataFrame(
        df_target.ta.adx(length=length, scalar=scalar, drift=drift).dropna()
    )

    output = pd.concat([df, df_adx], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Average True Range (ATR).",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "wma_data = obb.technical.wma(data=stock_data.results, target='close', length=50, offset=0)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def wma(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """计算加权移动平均线 (WMA)。

    加权移动平均线对近期数据赋予更多权重，对过去数据赋予较少权重。
    这是通过将每个柱线的价格乘以一个加权因子来完成的。由于其
    独特的计算方式，WMA 将比相应的简单
    移动平均线更紧密地跟随价格。

    Parameters
    ----------
    data : list[Data]
        用于计算的数据。
    target : str
        目标列名。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"。
    length : int, optional
        WMA 的长度，默认为 50。
    offset : int, optional
        WMA 的偏移量，默认为 0。

    Returns
    -------
    OBBject[list[Data]]
        WMA 数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, length)
    df = basemodel_to_df(data, index=index)
    df_target = get_target_column(df, target).to_frame()
    df_wma = pd.DataFrame(
        df_target.ta.wma(
            length=length,
            offset=offset,
            close=target,
            prefix=target,
        ).dropna()
    )

    output = pd.concat([df, df_wma], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Commodity Channel Index (CCI).",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "cci_data = obb.technical.cci(data=stock_data.results, length=14, scalar=0.015)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def cci(
    data: list[Data],
    index: str = "date",
    length: PositiveInt = 14,
    scalar: PositiveFloat = 0.015,
) -> OBBject[list[Data]]:
    """计算顺势指标 (CCI)。

    CCI 旨在检测市场趋势的开始和结束。
    100 到 -100 的范围是正常的交易范围。此范围之外的 CCI 值
    表示超买或超卖情况。您还可以在 CCI 中寻找价格
    背离。如果价格创出新高，而 CCI 没有，
    那么价格回调是可能的。

    Parameters
    ----------
    data : list[Data]
        用于 CCI 计算的数据。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"。
    length : PositiveInt, optional
        CCI 的长度，默认为 14。
    scalar : PositiveFloat, optional
        CCI 的标量，默认为 0.015。

    Returns
    -------
    OBBject[list[Data]]
        CCI 数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, length)
    df = basemodel_to_df(data, index=index)
    df_target = get_target_columns(df, ["close", "high", "low"])
    cci_df = pd.DataFrame(df_target.ta.cci(length=length, scalar=scalar).dropna())

    output = pd.concat([df, cci_df], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Relative Strength Index (RSI).",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "rsi_data = obb.technical.rsi(data=stock_data.results, target='close', length=14, scalar=100.0, drift=1)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def rsi(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 14,
    scalar: float = 100.0,
    drift: int = 1,
) -> OBBject[list[Data]]:
    """计算相对强弱指数 (RSI)。

    RSI 计算近期价格上涨变动与绝对价格
    变动的比率。RSI 范围从 0 到 100。
    当值超过 70/低于 30 时，RSI 被解释为超买/超卖指标。
    您也可以寻找与价格的背离。如果
    价格创出新高/新低，而 RSI 没有，这表明反转。

    Parameters
    ----------
    data : list[Data]
        用于 RSI 计算的数据。
    target : str
        目标列名。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"
    length : int, optional
        RSI 的长度，默认为 14
    scalar : float, optional
        用于 RSI 的标量，默认为 100.0
    drift : int, optional
        用于 RSI 的漂移，默认为 1

    Returns
    -------
    OBBject[list[Data]]
        RSI 数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, length)
    df = basemodel_to_df(data, index=index)
    df_target = get_target_column(df, target).to_frame()
    rsi_df = pd.DataFrame(
        df_target.ta.rsi(
            length=length,
            scalar=scalar,
            drift=drift,
            close=target,
            prefix=target,
        ).dropna()
    )

    output = pd.concat([df, rsi_df], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Stochastic Oscillator.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "stoch_data = obb.technical.stoch(data=stock_data.results, fast_k_period=14, slow_d_period=3, slow_k_period=3)",  # noqa: E501  # pylint: disable=line-too-long
            ],
        ),
    ],
)
def stoch(
    data: list[Data],
    index: str = "date",
    fast_k_period: NonNegativeInt = 14,
    slow_d_period: NonNegativeInt = 3,
    slow_k_period: NonNegativeInt = 3,
) -> OBBject[list[Data]]:
    """计算随机震荡指标。

    随机震荡指标衡量收盘价相对于
    近期交易范围的位置。值的范围从零到 100。%D 值超过 75
    表示超买情况；值低于 25 表示超卖情况。
    当快速 %D 上穿慢速 %D 时，为买入信号；当其
    下穿时，为卖出信号。原始 %K 通常被认为太不稳定，不适合用于
    交叉信号。

    Parameters
    ----------
    data : list[Data]
        用于随机震荡指标计算的数据。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"。
    fast_k_period : NonNegativeInt, optional
        快速 %K 周期，默认为 14。
    slow_d_period : NonNegativeInt, optional
        慢速 %D 周期，默认为 3。
    slow_k_period : NonNegativeInt, optional
        慢速 %K 周期，默认为 3。

    Returns
    -------
    OBBject[list[Data]]
        随机震荡指标数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, [fast_k_period, slow_d_period, slow_k_period])
    df = basemodel_to_df(data, index=index)
    df_target = get_target_columns(df, ["close", "high", "low"])
    stoch_df = pd.DataFrame(
        df_target.ta.stoch(
            fast_k_period=fast_k_period,
            slow_d_period=slow_d_period,
            slow_k_period=slow_k_period,
        ).dropna()
    )

    output = pd.concat([df, stoch_df], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Keltner Channels.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "kc_data = obb.technical.kc(data=stock_data.results, length=20, scalar=20, mamode='ema', offset=0)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def kc(
    data: list[Data],
    index: str = "date",
    length: PositiveInt = 20,
    scalar: PositiveFloat = 20,
    mamode: Literal["ema", "sma", "wma", "hma", "zlma"] = "ema",
    offset: NonNegativeInt = 0,
) -> OBBject[list[Data]]:
    """计算凯尔特纳通道。

    凯尔特纳通道是基于波动率的带状线，位于
    资产价格的两侧，有助于确定
    趋势的方向。凯尔特纳通道使用平均
    真实波幅 (ATR) 或波动率，突破顶部
    和底部障碍之上或之下并不表示持续。

    Parameters
    ----------
    data : list[Data]
        用于凯尔特纳通道计算的数据。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"
    length : PositiveInt, optional
        凯尔特纳通道的长度，默认为 20
    scalar : PositiveFloat, optional
        用于凯尔特纳通道的标量，默认为 20
    mamode : Literal["ema", "sma", "wma", "hma", "zlma"], optional
        用于凯尔特纳通道的移动平均模式，默认为 "ema"
    offset : NonNegativeInt, optional
        用于凯尔特纳通道的偏移量，默认为 0

    Returns
    -------
    OBBject[list[Data]]
        凯尔特纳通道数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, length)
    df = basemodel_to_df(data, index=index)
    df_target = get_target_columns(df, ["high", "low", "close"])
    kc_df = pd.DataFrame(
        df_target.ta.kc(
            length=length,
            scalar=scalar,
            mamode=mamode,
            offset=offset,
        ).dropna()
    )
    output = pd.concat([df, kc_df], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Center of Gravity (CG).",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "cg_data = obb.technical.cg(data=stock_data.results, length=14)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def cg(
    data: list[Data], index: str = "date", length: PositiveInt = 14
) -> OBBject[list[Data]]:
    """计算重心指标。

    简而言之，重心指标用于预测未来的价格变动，
    并在价格反转发生后立即进行交易。然而，就像其他震荡指标一样，
    COG 指标在区间震荡市场中产生最佳结果，当
    价格趋于平稳时应避免使用。使用它的交易者将能够密切推测资产
    即将发生的价格变化。

    Parameters
    ----------
    data : list[Data]
        用于 COG 计算的数据。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"
    length : PositiveInt, optional
        COG 的长度，默认为 14

    Returns
    -------
    OBBject[list[Data]]
        COG 数据。
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, length)
    df = basemodel_to_df(data, index=index)
    df_target = get_target_columns(df, ["high", "low", "close"])
    cg_df = pd.DataFrame(df_target.ta.cg(length=length).dropna())

    output = pd.concat([df, cg_df], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Realized Volatility Cones.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='yfinance')",
                "cones_data = obb.technical.cones(data=stock_data.results, lower_q=0.25, upper_q=0.75, model='std')",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def cones(
    data: list[Data],
    index: str = "date",
    lower_q: float = 0.25,
    upper_q: float = 0.75,
    model: Literal[
        "std",
        "parkinson",
        "garman_klass",
        "hodges_tompkins",
        "rogers_satchell",
        "yang_zhang",
    ] = "std",
    is_crypto: bool = False,
    trading_periods: int | None = None,
) -> OBBject[list[Data]]:
    """计算随时间滚动窗口的已实现波动率分位数。

    锥体指标旨在通过对波动率分位数的详细分析来绘制
    价格变动的起伏。通过检查特定时间框架内的波动率范围，它提供了
    市场行为的细致视图，突出显示稳定和动荡时期。

    计算波动率的模型是可选的，可以是以下之一：
    - 标准差 (Standard deviation)
    - 帕金森 (Parkinson)
    - 加曼-克拉斯 (Garman-Klass)
    - 霍奇斯-汤普金斯 (Hodges-Tompkins)
    - 罗杰斯-萨切尔 (Rogers-Satchell)
    - 杨-张 (Yang-Zhang)

    有关更多信息，请阅读模型参数说明。

    Parameters
    ----------
    data : list[Data]
        用于计算的数据。
    index : str, optional
        用于 `data` 的索引列名，默认为 "date"
    lower_q : float, optional
        用于计算的下分位数
    upper_q : float, optional
        用于计算的上分位数
    model : Literal["std", "parkinson", "garman_klass", "hodges_tompkins", "rogers_satchell", "yang_zhang"], optional
        用于计算已实现波动率的模型

            标准差衡量回报从平均回报分散的程度。
            它是最常见（且有偏差）的波动率估计量。

            帕金森波动率使用当天的最高价和最低价，而不仅仅是收盘价到收盘价。
            它对于捕捉当天的价格大幅波动很有用。

            加曼-克拉斯波动率通过考虑开盘价和收盘价扩展了帕金森波动率。
            由于市场在交易时段的开盘和收盘期间最为活跃，
            它使波动率估计更加准确。

            霍奇斯-汤普金斯波动率是对使用重叠数据样本进行估计的偏差校正。
            它产生无偏估计并显着提高效率。

            罗杰斯-萨切尔是衡量平均回报不等于零的波动率的估计量。
            与帕金森和加曼-克拉斯估计量不同，罗杰斯-萨切尔包含漂移项，
            平均回报不等于零。

            杨-张波动率是隔夜（收盘到开盘波动率）的组合。
            它是罗杰斯-萨切尔波动率和开盘到收盘波动率的加权平均值。
    is_crypto : bool, optional
        数据是否为加密货币。如果为 True，则波动率计算为 365 天而不是 252 天。
    trading_periods : Optional[int] [default: 252]
        一年中的交易周期数。

    Returns
    -------
    OBBject[list[Data]]
        锥体数据。
    """
    if lower_q > upper_q:
        lower_q, upper_q = upper_q, lower_q

    df = basemodel_to_df(data, index=index)
    df_cones = calculate_cones(
        data=df,
        lower_q=lower_q,
        upper_q=upper_q,
        model=model,
        is_crypto=is_crypto,
        trading_periods=trading_periods,
    )
    results = df_to_basemodel(df_cones)

    return OBBject(results=results)


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get the Exponential Moving Average (EMA).",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "ema_data = obb.technical.ema(data=stock_data.results, target='close', length=50, offset=0)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def ema(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """计算指数移动平均线 (EMA)。

    EMA 是一种累积计算，包括所有数据。过去的值对平均值的
    贡献递减，而最近的值有更大的
    贡献。这种方法使移动平均线对数据变化
    更敏感。

    Parameters
    ----------
    data : list[Data]
        The data to use for the calculation.
    target : str
        Target column name.
    index : str, optional
        Index column name to use with `data`, by default "date"
    length : int, optional
        The length of the calculation, by default 50.
    offset : int, optional
        The offset of the calculation, by default 0.

    Returns
    -------
    OBBject[list[Data]]
        The calculated data.
    """
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    import pandas_ta as ta  # noqa

    validate_data(data, length)
    df = basemodel_to_df(data, index=index)
    df_target = get_target_column(df, target).to_frame()
    ema_df = pd.DataFrame(
        df_target.ta.ema(
            length=length, offset=offset, close=target, prefix=target
        ).dropna()
    )

    output = pd.concat([df, ema_df], axis=1)
    results = df_to_basemodel(output.reset_index())

    return OBBject(results=results)
