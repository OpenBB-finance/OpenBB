"""Technical Analysis Router."""

# pylint: disable=too-many-lines
from typing import Any, Dict, List, Literal, Optional

import pandas as pd
import pandas_ta as ta
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
router = Router(prefix="", description="Technical Analysis tools.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Calculate the Relative Strength Ratio and Relative Strength Momentum"
            + " for a group of symbols against a benchmark.",
            code=[
                "stock_data = obb.equity.price.historical("
                + "symbol='AAPL,MSFT,GOOGL,META,AMZN,TSLA,SPY', start_date='2022-01-01', provider='yfinance')",
                "rr_data = obb.technical.relative_rotation(data=stock_data.results, benchmark='SPY')",
                "rs_ratios = rr_data.results.rs_ratios",
                "rs_momentum = rr_data.results.rs_momentum",
            ],
        ),
        PythonEx(
            description="When the assets are not traded 252 days per year,"
            + "adjust the momentum and volatility periods accordingly.",
            code=[
                "crypto_data = obb.crypto.price.historical("
                + " symbol='BTCUSD,ETHUSD,SOLUSD', start_date='2021-01-01', provider='yfinance')",
                "rr_data = obb.technical.relative_rotation(data=crypto_data.results, benchmark='BTCUSD',"
                + " long_period=365, short_period=30, window=30, trading_periods=365)",
            ],
        ),
        APIEx(
            description="Note that the mock data displayed here is insufficient."
            + " It must contain multiple symbols, with the benchmark, and be daily data at least 1 year in length.",
            parameters={"benchmark": "SPY", "data": APIEx.mock_data("timeseries")},
        ),
    ],
)
async def relative_rotation(
    data: List[Data],
    benchmark: str,
    study: Literal["price", "volume", "volatility"] = "price",
    long_period: Optional[int] = 252,
    short_period: Optional[int] = 21,
    window: Optional[int] = 21,
    trading_periods: Optional[int] = 252,
    chart_params: Optional[Dict[str, Any]] = None,
) -> OBBject[RelativeRotationData]:
    """Calculate the Relative Strength Ratio and Relative Strength Momentum for a group of symbols against a benchmark.

    Parameters
    ----------
    data : list[Data]
        The data to be used for the relative rotation calculations.
        This should be the multi-symbol output from the 'equity.price.historical' endpoint, or similar.
        Or a pivot table with the 'date' column as the index, the symbols as the columns, and the 'study' as the values.
        It is recommended to use the 'equity.price.historical' endpoint to get the data, and feed the results as-is.
    benchmark : str
        The symbol to be used as the benchmark.
    study : Literal[price, volume, volatility]
        The data point for the calculations. If 'price', the closing price will be used.
        If 'volatility', the standard deviation of the closing price will be used.
        If 'data' is supplied as a pivot table,
        the 'study' will assume the values are the closing price and 'volume' will be ignored.
    long_period : int, optional
        The length of the long period for momentum calculation, by default 252.
        Adjust this value when supplying a time series with an interval that is not daily.
        For example, if the data is monthly, the long period should be 12.
    short_period : int, optional
        The length of the short period for momentum calculation, by default 21.
        Adjust this value when supplying a time series with an interval that is not daily.
    window : int, optional
        The length of window for the standard deviation calculation, by default 21.
        Adjust this value when supplying a time series with an interval that is not daily.
    trading_periods : int, optional
        The number of trading periods per year, for the standard deviation calculation, by default 252.
        Adjust this value when supplying a time series with an interval that is not daily.
    chart_params : dict[str, Any], optional
        Additional parameters to pass when `chart=True` and the `openbb-charting` extension is installed.
        Parameters can be passed again to redraw the chart using the charting.to_chart() method of the response.

        ChartParams
        -----------
        date : str, optional
            A target end date within the data to use for the chart, by default is the last date in the data.
        show_tails : bool
            Show the tails on the chart, by default True.
        tail_periods : int
            Number of periods to show in the tails, by default 16.
        tail_interval : Literal[day, week, month]
            Interval to show the tails, by default 'week'.
        title : str, optional
            Title of the chart.

    Returns
    -------
    OBBject[RelativeRotationData]
        results : RelativeRotationData
            symbols : list[str]:
                The symbols that are being compared against the benchmark.
            benchmark : str
                The benchmark symbol.
            study : Literal[price, volume, volatility]
                The data point for the selected.
            long_period : int
                The length of the long period for momentum calculation, as entered by the user.
            short_period : int
                The length of the short period for momentum calculation, as entered by the user.
            window : int
                The length of window for the standard deviation calculation.
            trading_periods : int
                The number of trading periods per year, for the standard deviation calculation.
            start_date : str
                The start date of the data after adjusting the length of the data for the calculations.
            end_date : str
                The end date of the data.
            symbols_data : list[Data]
                The data representing the selected 'study' for each symbol.
            benchmark_data : list[Data]
                The data representing the selected 'study' for the benchmark.
            rs_ratios : list[Data]
                The normalized relative strength ratios data.
            rs_momentum : list[Data]
                The normalized relative strength momentum data.
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
            description="Get the Average True Range.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "atr_data = obb.technical.atr(data=stock_data.results)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def atr(
    data: List[Data],
    index: str = "date",
    length: PositiveInt = 14,
    mamode: Literal["rma", "ema", "sma", "wma"] = "rma",
    drift: NonNegativeInt = 1,
    offset: int = 0,
) -> OBBject[List[Data]]:
    """Calculate the Average True Range.

    Used to measure volatility, especially volatility caused by gaps or limit moves.
    The ATR metric helps understand how much the values in your data change on average,
    giving insights into the stability or unpredictability during a certain period.
    It's particularly useful for spotting trends of increase or decrease in variations,
    without getting into technical trading details.
    The method considers not just the day-to-day changes but also accounts for any
    sudden jumps or drops, ensuring you get a comprehensive view of movement.

    Parameters
    ----------
    data : List[Data]
        List of data to apply the indicator to.
    index : str, optional
        Index column name, by default "date"
    length : PositiveInt, optional
        It's period, by default 14
    mamode : Literal["rma", "ema", "sma", "wma"], optional
        Moving average mode, by default "rma"
    drift : NonNegativeInt, optional
        The difference period, by default 1
    offset : int, optional
        How many periods to offset the result, by default 0

    Returns
    -------
    OBBject[List[Data]]
        List of data with the indicator applied.
    """
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
            description="Get the Bollinger Band Width.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "fib_data = obb.technical.fib(data=stock_data.results, period=120)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def fib(
    data: List[Data],
    index: str = "date",
    close_column: Literal["close", "adj_close"] = "close",
    period: PositiveInt = 120,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> OBBject[List[Data]]:
    """Create Fibonacci Retracement Levels.

    This method draws from a classic technique to pinpoint significant price levels
    that often indicate where the market might find support or resistance.
    It's a tool used to gauge potential turning points in the data by applying a
    mathematical approach rooted in nature's patterns. Is used to get insights into
    where prices could head next, based on historical movements.

    Parameters
    ----------
    data : List[Data]
        List of data to apply the indicator to.
    index : str, optional
        Index column name, by default "date"
    period : PositiveInt, optional
        Period to calculate the indicator, by default 120

    Returns
    -------
    OBBject[List[Data]]
        List of data with the indicator applied.
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
            description="Get the On Balance Volume (OBV).",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "obv_data = obb.technical.obv(data=stock_data.results, offset=0)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def obv(
    data: List[Data],
    index: str = "date",
    offset: int = 0,
) -> OBBject[List[Data]]:
    """Calculate the On Balance Volume (OBV).

    Is a cumulative total of the up and down volume. When the close is higher than the
    previous close, the volume is added to the running total, and when the close is
    lower than the previous close, the volume is subtracted from the running total.

    To interpret the OBV, look for the OBV to move with the price or precede price moves.
    If the price moves before the OBV, then it is a non-confirmed move. A series of rising peaks,
    or falling troughs, in the OBV indicates a strong trend. If the OBV is flat, then the market
    is not trending.

    Parameters
    ----------
    data : List[Data]
        List of data to apply the indicator to.
    index : str, optional
        Index column name, by default "date"
    offset : int, optional
        How many periods to offset the result, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        List of data with the indicator applied.
    """
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
            description="Perform the Fisher Transform.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "fisher_data = obb.technical.fisher(data=stock_data.results, length=14, signal=1)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def fisher(
    data: List[Data],
    index: str = "date",
    length: PositiveInt = 14,
    signal: PositiveInt = 1,
) -> OBBject[List[Data]]:
    """Perform the Fisher Transform.

    A technical indicator created by John F. Ehlers that converts prices into a Gaussian
    normal distribution. The indicator highlights when prices have moved to an extreme,
    based on recent prices.
    This may help in spotting turning points in the price of an asset. It also helps
    show the trend and isolate the price waves within a trend.

    Parameters
    ----------
    data : List[Data]
        List of data to apply the indicator to.
    index : str, optional
        Index column name, by default "date"
    length : PositiveInt, optional
        Fisher period, by default 14
    signal : PositiveInt, optional
        Fisher Signal period, by default 1

    Returns
    -------
    OBBject[List[Data]]
        List of data with the indicator applied.
    """
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
            description="Get the Accumulation/Distribution Oscillator.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "adosc_data = obb.technical.adosc(data=stock_data.results, fast=3, slow=10, offset=0)",
            ],
        ),
        APIEx(parameters={"fast": 2, "slow": 4, "data": APIEx.mock_data("timeseries")}),
    ],
)
def adosc(
    data: List[Data],
    index: str = "date",
    fast: PositiveInt = 3,
    slow: PositiveInt = 10,
    offset: int = 0,
) -> OBBject[List[Data]]:
    """Calculate the Accumulation/Distribution Oscillator.

    Also known as the Chaikin Oscillator.

    Essentially a momentum indicator, but of the Accumulation-Distribution line
    rather than merely price. It looks at both the strength of price moves and the
    underlying buying and selling pressure during a given time period. The oscillator
    reading above zero indicates net buying pressure, while one below zero registers
    net selling pressure. Divergence between the indicator and pure price moves are
    the most common signals from the indicator, and often flag market turning points.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    fast : PositiveInt, optional
        Number of periods to be used for the fast calculation, by default 3.
    slow : PositiveInt, optional
        Number of periods to be used for the slow calculation, by default 10.
    offset : int, optional
        Offset to be used for the calculation, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.
    """
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
            description="Get the Chande Momentum Oscillator.",
            code=[
                "stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')",
                "bbands_data = obb.technical.bbands(data=stock_data.results, target='close', length=50, std=2, mamode='sma')",  # noqa: E501
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def bbands(
    data: List[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    std: NonNegativeFloat = 2,
    mamode: Literal["sma", "ema", "wma", "rma"] = "sma",
    offset: int = 0,
) -> OBBject[List[Data]]:
    """Calculate the Bollinger Bands.

    Consist of three lines. The middle band is a simple moving average (generally 20
    periods) of the typical price (TP). The upper and lower bands are F standard
    deviations (generally 2) above and below the middle band.
    The bands widen and narrow when the volatility of the price is higher or lower,
    respectively.

    Bollinger Bands do not, in themselves, generate buy or sell signals;
    they are an indicator of overbought or oversold conditions. When the price is near the
    upper or lower band it indicates that a reversal may be imminent. The middle band
    becomes a support or resistance level. The upper and lower bands can also be
    interpreted as price targets. When the price bounces off of the lower band and crosses
    the middle band, then the upper band becomes the price target.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    target : str
        Target column name.
    index : str, optional
        Index column name to use with `data`, by default "date".
    length : int, optional
        Number of periods to be used for the calculation, by default 50.
    std : NonNegativeFloat, optional
        Standard deviation to be used for the calculation, by default 2.
    mamode : Literal["sma", "ema", "wma", "rma"], optional
        Moving average mode to be used for the calculation, by default "sma".
    offset : int, optional
        Offset to be used for the calculation, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.
    """
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
    data: List[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
) -> OBBject[List[Data]]:
    """Calculate the zero lag exponential moving average (ZLEMA).

    Created by John Ehlers and Ric Way. The idea is do a
    regular exponential moving average (EMA) calculation but
    on a de-lagged data instead of doing it on the regular data.
    Data is de-lagged by removing the data from "lag" days ago
    thus removing (or attempting to) the cumulative effect of
    the moving average.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    target : str
        Target column name.
    index : str, optional
        Index column name to use with `data`, by default "date".
    length : int, optional
        Number of periods to be used for the calculation, by default 50.
    offset : int, optional
        Offset to be used for the calculation, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.
    """
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
    data: List[Data],
    index: str = "date",
    length: int = 25,
    scalar: float = 100,
) -> OBBject[List[Data]]:
    """Calculate the Aroon Indicator.

    The word aroon is Sanskrit for "dawn's early light." The Aroon
    indicator attempts to show when a new trend is dawning. The indicator consists
    of two lines (Up and Down) that measure how long it has been since the highest
    high/lowest low has occurred within an n period range.

    When the Aroon Up is staying between 70 and 100 then it indicates an upward trend.
    When the Aroon Down is staying between 70 and 100 then it indicates an downward trend.
    A strong upward trend is indicated when the Aroon Up is above 70 while the Aroon Down is below 30.
    Likewise, a strong downward trend is indicated when the Aroon Down is above 70 while
    the Aroon Up is below 30. Also look for crossovers. When the Aroon Down crosses above
    the Aroon Up, it indicates a weakening of the upward trend (and vice versa).

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    index: str, optional
        Index column name to use with `data`, by default "date".
    length : int, optional
        Number of periods to be used for the calculation, by default 25.
    scalar : float, optional
        Scalar to be used for the calculation, by default 100.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.
    """
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
    data: List[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
) -> OBBject[List[Data]]:
    """Calculate the Simple Moving Average (SMA).

    Moving Averages are used to smooth the data in an array to
    help eliminate noise and identify trends. The Simple Moving Average is literally
    the simplest form of a moving average. Each output value is the average of the
    previous n values. In a Simple Moving Average, each value in the time period carries
    equal weight, and values outside of the time period are not included in the average.
    This makes it less responsive to recent changes in the data, which can be useful for
    filtering out those changes.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    target : str
        Target column name.
    index : str, optional
        Index column name to use with `data`, by default "date".
    length : int, optional
        Number of periods to be used for the calculation, by default 50.
    offset : int, optional
        Offset from the current period, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.
    """
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
    data: List[Data],
    index: str = "date",
    target: str = "close",
    show_all: bool = True,
    asint: bool = True,
    offset: int = 0,
) -> OBBject[List[Data]]:
    """Calculate the Demark sequential indicator.

    This indicator offers a strategic way to spot potential reversals in market trends.
    It's designed to highlight moments when the current trend may be running out of steam,
    suggesting a possible shift in direction. By focusing on specific patterns in price movements, it provides
    valuable insights for making informed decisions on future changes and identifies trend exhaustion points
    with precision.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    target : str, optional
        Target column name, by default "close".
    show_all : bool, optional
        Show 1 - 13. If set to False, show 6 - 9
    asint : bool, optional
        If True, fill NAs with 0 and change type to int, by default True.
    offset : int, optional
        How many periods to offset the result

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.
    """
    df = basemodel_to_df(data, index=index)
    df_target = get_target_column(df, target).to_frame()
    _demark = ta.td_seq(
        df_target[target], asint=asint, show_all=show_all, offset=offset
    )
    demark_df = df[[target]].reset_index().join(_demark)
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
    data: List[Data],
    index: str = "date",
    anchor: str = "D",
    offset: int = 0,
) -> OBBject[List[Data]]:
    """Calculate the Volume Weighted Average Price (VWAP).

    Measures the average typical price by volume.
    It is typically used with intraday charts to identify general direction.
    It helps to understand the true average price factoring in the volume of transactions,
    and serves as a benchmark for assessing the market's direction over short periods, such as a single trading day.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    anchor : str, optional
        Anchor period to use for the calculation, by default "D".
        See Timeseries Offset Aliases below for additional options:
        https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases
    offset : int, optional
        Offset from the current period, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.
    """
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
    data: List[Data],
    target: str = "close",
    index: str = "date",
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> OBBject[List[Data]]:
    """Calculate the Moving Average Convergence Divergence (MACD).

    Difference between two Exponential Moving Averages. The Signal line is an
    Exponential Moving Average of the MACD.

    The MACD signals trend changes and indicates the start of new trend direction.
    High values indicate overbought conditions, low values indicate oversold conditions.
    Divergence with the price indicates an end to the current trend, especially if the
    MACD is at extreme high or low values. When the MACD line crosses above the
    signal line a buy signal is generated. When the MACD crosses below the signal line a
    sell signal is generated. To confirm the signal, the MACD should be above zero for a buy,
    and below zero for a sell.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    target : str
        Target column name.
    fast : int, optional
        Number of periods for the fast EMA, by default 12.
    slow : int, optional
        Number of periods for the slow EMA, by default 26.
    signal : int, optional
        Number of periods for the signal EMA, by default 9.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.
    """
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
    data: List[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
) -> OBBject[List[Data]]:
    """Calculate the Hull Moving Average (HMA).

    Solves the age old dilemma of making a moving average more responsive to current
    price activity whilst maintaining curve smoothness.
    In fact the HMA almost eliminates lag altogether and manages to improve smoothing
    at the same time.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    target : str
        Target column name.
    index : str, optional
        Index column name to use with `data`, by default "date".
    length : int, optional
        Number of periods for the HMA, by default 50.
    offset : int, optional
        Offset of the HMA, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.
    """
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
    data: List[Data],
    index: str = "date",
    lower_length: PositiveInt = 20,
    upper_length: PositiveInt = 20,
    offset: int = 0,
) -> OBBject[List[Data]]:
    """Calculate the Donchian Channels.

    Three lines generated by moving average calculations that comprise an indicator
    formed by upper and lower bands around a midrange or median band. The upper band
    marks the highest price of a security over N periods while the lower band
    marks the lowest price of a security over N periods. The area
    between the upper and lower bands represents the Donchian Channel.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    lower_length : PositiveInt, optional
        Number of periods for the lower band, by default 20.
    upper_length : PositiveInt, optional
        Number of periods for the upper band, by default 20.
    offset : int, optional
        Offset of the Donchian Channel, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.
    """
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
    data: List[Data],
    index: str = "date",
    conversion: PositiveInt = 9,
    base: PositiveInt = 26,
    lagging: PositiveInt = 52,
    offset: PositiveInt = 26,
    lookahead: bool = False,
) -> OBBject[List[Data]]:
    """Calculate the Ichimoku Cloud.

    Also known as Ichimoku Kinko Hyo, is a versatile indicator that defines support and
    resistance, identifies trend direction, gauges momentum and provides trading
    signals. Ichimoku Kinko Hyo translates into "one look equilibrium chart". With
    one look, chartists can identify the trend and look for potential signals within
    that trend.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    conversion : PositiveInt, optional
        Number of periods for the conversion line, by default 9.
    base : PositiveInt, optional
        Number of periods for the base line, by default 26.
    lagging : PositiveInt, optional
        Number of periods for the lagging span, by default 52.
    offset : PositiveInt, optional
        Number of periods for the offset, by default 26.
    lookahead : bool, optional
        drops the Chikou Span Column to prevent potential data leak

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.
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
    data: List[Data],
    index: str = "date",
    target: str = "close",
    period: PositiveInt = 90,
) -> OBBject[List[Data]]:
    """Calculate the Clenow Volatility Adjusted Momentum.

    The Clenow Volatility Adjusted Momentum is a sophisticated approach to understanding market momentum with a twist.
    It adjusts for volatility, offering a clearer picture of true momentum by considering how price movements are
    influenced by their volatility over a set period. It helps in identifying stronger, more reliable trends.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    target : str, optional
        Target column name, by default "close".
    period : PositiveInt, optional
        Number of periods for the momentum, by default 90.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.
    """
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
def ad(data: List[Data], index: str = "date", offset: int = 0) -> OBBject[List[Data]]:
    """Calculate the Accumulation/Distribution Line.

    Similar to the On Balance Volume (OBV).
    Sums the volume times +1/-1 based on whether the close is higher than the previous
    close. The Accumulation/Distribution indicator, however multiplies the volume by the
    close location value (CLV). The CLV is based on the movement of the issue within a
    single bar and can be +1, -1 or zero.


    The Accumulation/Distribution Line is interpreted by looking for a divergence in
    the direction of the indicator relative to price. If the Accumulation/Distribution
    Line is trending upward it indicates that the price may follow. Also, if the
    Accumulation/Distribution Line becomes flat while the price is still rising (or falling)
    then it signals an impending flattening of the price.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    offset : int, optional
        Offset of the AD, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.
    """
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
    data: List[Data],
    index: str = "date",
    length: int = 50,
    scalar: float = 100.0,
    drift: int = 1,
) -> OBBject[List[Data]]:
    """Calculate the Average Directional Index (ADX).

    The ADX is a Welles Wilder style moving average of the Directional Movement Index (DX).
    The values range from 0 to 100, but rarely get above 60. To interpret the ADX, consider
    a high number to be a strong trend, and a low number, a weak trend.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    length : int, optional
        Number of periods for the ADX, by default 50.
    scalar : float, optional
        Scalar value for the ADX, by default 100.0.
    drift : int, optional
        Drift value for the ADX, by default 1.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.
    """
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
    data: List[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
) -> OBBject[List[Data]]:
    """Calculate the Weighted Moving Average (WMA).

    A Weighted Moving Average puts more weight on recent data and less on past data.
    This is done by multiplying each bar's price by a weighting factor. Because of its
    unique calculation, WMA will follow prices more closely than a corresponding Simple
    Moving Average.

    Parameters
    ----------
    data : List[Data]
        The data to use for the calculation.
    target : str
        Target column name.
    index : str, optional
        Index column name to use with `data`, by default "date".
    length : int, optional
        The length of the WMA, by default 50.
    offset : int, optional
        The offset of the WMA, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        The WMA data.
    """
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
    data: List[Data],
    index: str = "date",
    length: PositiveInt = 14,
    scalar: PositiveFloat = 0.015,
) -> OBBject[List[Data]]:
    """Calculate the Commodity Channel Index (CCI).

    The CCI is designed to detect beginning and ending market trends.
    The range of 100 to -100 is the normal trading range. CCI values outside of this
    range indicate overbought or oversold conditions. You can also look for price
    divergence in the CCI. If the price is making new highs, and the CCI is not,
    then a price correction is likely.

    Parameters
    ----------
    data : List[Data]
        The data to use for the CCI calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    length : PositiveInt, optional
        The length of the CCI, by default 14.
    scalar : PositiveFloat, optional
        The scalar of the CCI, by default 0.015.

    Returns
    -------
    OBBject[List[Data]]
        The CCI data.
    """
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
    data: List[Data],
    target: str = "close",
    index: str = "date",
    length: int = 14,
    scalar: float = 100.0,
    drift: int = 1,
) -> OBBject[List[Data]]:
    """Calculate the Relative Strength Index (RSI).

    RSI calculates a ratio of the recent upward price movements to the absolute price
    movement. The RSI ranges from 0 to 100.
    The RSI is interpreted as an overbought/oversold indicator when
    the value is over 70/below 30. You can also look for divergence with price. If
    the price is making new highs/lows, and the RSI is not, it indicates a reversal.

    Parameters
    ----------
    data : List[Data]
        The data to use for the RSI calculation.
    target : str
        Target column name.
    index : str, optional
        Index column name to use with `data`, by default "date"
    length : int, optional
        The length of the RSI, by default 14
    scalar : float, optional
        The scalar to use for the RSI, by default 100.0
    drift : int, optional
        The drift to use for the RSI, by default 1

    Returns
    -------
    OBBject[List[Data]]
        The RSI data.
    """
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
    data: List[Data],
    index: str = "date",
    fast_k_period: NonNegativeInt = 14,
    slow_d_period: NonNegativeInt = 3,
    slow_k_period: NonNegativeInt = 3,
) -> OBBject[List[Data]]:
    """Calculate the Stochastic Oscillator.

    The Stochastic Oscillator measures where the close is in relation
    to the recent trading range. The values range from zero to 100. %D values over 75
    indicate an overbought condition; values under 25 indicate an oversold condition.
    When the Fast %D crosses above the Slow %D, it is a buy signal; when it crosses
    below, it is a sell signal. The Raw %K is generally considered too erratic to use
    for crossover signals.

    Parameters
    ----------
    data : List[Data]
        The data to use for the Stochastic Oscillator calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    fast_k_period : NonNegativeInt, optional
        The fast %K period, by default 14.
    slow_d_period : NonNegativeInt, optional
        The slow %D period, by default 3.
    slow_k_period : NonNegativeInt, optional
        The slow %K period, by default 3.

    Returns
    -------
    OBBject[List[Data]]
        The Stochastic Oscillator data.
    """
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
    data: List[Data],
    index: str = "date",
    length: PositiveInt = 20,
    scalar: PositiveFloat = 20,
    mamode: Literal["ema", "sma", "wma", "hma", "zlma"] = "ema",
    offset: NonNegativeInt = 0,
) -> OBBject[List[Data]]:
    """Calculate the Keltner Channels.

    Keltner Channels are volatility-based bands that are placed
    on either side of an asset's price and can aid in determining
    the direction of a trend.The Keltner channel uses the average
    true range (ATR) or volatility, with breaks above or below the top
    and bottom barriers signaling a continuation.

    Parameters
    ----------
    data : List[Data]
        The data to use for the Keltner Channels calculation.
    index : str, optional
        Index column name to use with `data`, by default "date"
    length : PositiveInt, optional
        The length of the Keltner Channels, by default 20
    scalar : PositiveFloat, optional
        The scalar to use for the Keltner Channels, by default 20
    mamode : Literal["ema", "sma", "wma", "hma", "zlma"], optional
        The moving average mode to use for the Keltner Channels, by default "ema"
    offset : NonNegativeInt, optional
        The offset to use for the Keltner Channels, by default 0

    Returns
    -------
    OBBject[List[Data]]
        The Keltner Channels data.
    """
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
    data: List[Data], index: str = "date", length: PositiveInt = 14
) -> OBBject[List[Data]]:
    """Calculate the Center of Gravity.

    The Center of Gravity indicator, in short, is used to anticipate future price movements
    and to trade on price reversals as soon as they happen. However, just like other oscillators,
    the COG indicator returns the best results in range-bound markets and should be avoided when
    the price is trending. Traders who use it will be able to closely speculate the upcoming
    price change of the asset.

    Parameters
    ----------
    data : List[Data]
        The data to use for the COG calculation.
    index : str, optional
        Index column name to use with `data`, by default "date"
    length : PositiveInt, optional
        The length of the COG, by default 14

    Returns
    -------
    OBBject[List[Data]]
        The COG data.
    """
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
    data: List[Data],
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
    trading_periods: Optional[int] = None,
) -> OBBject[List[Data]]:
    """Calculate the realized volatility quantiles over rolling windows of time.

    The cones indicator is designed to map out the ebb and flow of price movements through a detailed analysis of
    volatility quantiles. By examining the range of volatility within specific time frames, it offers a nuanced view of
    market behavior, highlighting periods of stability and turbulence.

    The model for calculating volatility is selectable and can be one of the following:
    - Standard deviation
    - Parkinson
    - Garman-Klass
    - Hodges-Tompkins
    - Rogers-Satchell
    - Yang-Zhang

    Read more about it in the model parameter description.

    Parameters
    ----------
    data : List[Data]
        The data to use for the calculation.
    index : str, optional
        Index column name to use with `data`, by default "date"
    lower_q : float, optional
        The lower quantile value for calculations
    upper_q : float, optional
        The upper quantile value for calculations
    model : Literal["std", "parkinson", "garman_klass", "hodges_tompkins", "rogers_satchell", "yang_zhang"], optional
        The model used to calculate realized volatility

            Standard deviation measures how widely returns are dispersed from the average return.
            It is the most common (and biased) estimator of volatility.

            Parkinson volatility uses the high and low price of the day rather than just close to close prices.
            It is useful for capturing large price movements during the day.

            Garman-Klass volatility extends Parkinson volatility by taking into account the opening and closing price.
            As markets are most active during the opening and closing of a trading session;
            it makes volatility estimation more accurate.

            Hodges-Tompkins volatility is a bias correction for estimation using an overlapping data sample.
            It produces unbiased estimates and a substantial gain in efficiency.

            Rogers-Satchell is an estimator for measuring the volatility with an average return not equal to zero.
            Unlike Parkinson and Garman-Klass estimators, Rogers-Satchell incorporates a drift term,
            mean return not equal to zero.

            Yang-Zhang volatility is the combination of the overnight (close-to-open volatility).
            It is a weighted average of the Rogers-Satchell volatility and the open-to-close volatility.
    is_crypto : bool, optional
        Whether the data is crypto or not. If True, volatility is calculated for 365 days instead of 252
    trading_periods : Optional[int] [default: 252]
        Number of trading periods in a year.

    Returns
    -------
    OBBject[List[Data]]
        The cones data.
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
    data: List[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
) -> OBBject[List[Data]]:
    """Calculate the Exponential Moving Average (EMA).

    EMA is a cumulative calculation, including all data. Past values have
    a diminishing contribution to the average, while more recent values have a greater
    contribution. This method allows the moving average to be more responsive to changes
    in the data.

    Parameters
    ----------
    data : List[Data]
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
    OBBject[List[Data]]
        The calculated data.
    """
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
