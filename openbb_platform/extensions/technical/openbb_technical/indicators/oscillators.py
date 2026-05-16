"""Oscillator-family technical indicators."""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.utils import basemodel_to_df
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, PositiveFloat, PositiveInt

from openbb_technical.helpers import validate_data

# Bare 'date' alias for function signatures so the static-package builder
# writes 'date' (which it imports from datetime) rather than 'dateType' which it does not.
date = dateType


router = Router(prefix="", description="Oscillator indicators.")


class RsiQueryParams(QueryParams):
    """Query parameters for the Relative Strength Index endpoint.

    Parameters
    ----------
    data : list[Data]
        Input price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    target : str, optional
        Target column to apply RSI to, by default ``"close"``.
    length : PositiveInt, optional
        Lookback window in bars, by default 14.
    scalar : PositiveFloat, optional
        Output scaling. ``100`` produces the conventional 0–100 range,
        by default 100.0.
    drift : PositiveInt, optional
        Difference period for momentum, by default 1.
    """

    __category__ = "oscillator"
    __output_columns__ = ("date", "rsi")

    data: list[Data] = Field(description="Input price series.")
    index: str = Field(default="date", description="Index column name in ``data``.")
    target: str = Field(default="close", description="Target column to apply RSI to.")
    length: PositiveInt = Field(default=14, description="Lookback window in bars.")
    scalar: PositiveFloat = Field(
        default=100.0,
        description="Output scaling. ``100`` produces the conventional 0–100 range.",
    )
    drift: PositiveInt = Field(default=1, description="Difference period for momentum.")


class RsiData(Data):
    """One row of the RSI time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    rsi : float, optional
        RSI value over the trailing ``length`` bars on ``target``. ``None``
        for warm-up rows preceding ``length``.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    rsi: float | None = Field(
        description="RSI value over the trailing ``length`` bars on ``target``.",
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="RSI(14) on daily TSLA closes.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "rsi = obb.technical.rsi(data=data, length=14)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def rsi(
    data: list[Data],
    index: str = "date",
    target: str = "close",
    length: int = 14,
    scalar: float = 100.0,
    drift: int = 1,
) -> OBBject[list[Data]]:
    """Calculate the Relative Strength Index (RSI), Wilder's momentum oscillator.

    RSI compares the magnitude of recent up-moves to the magnitude of recent
    down-moves over a trailing window and rescales the ratio to a bounded
    0–100 range. The classic formulation uses Wilder smoothing on the average
    gain and average loss; the indicator then expresses average gain as a
    share of total absolute change. Traders read values above 70 as overbought
    and below 30 as oversold, watch divergences against price for trend
    exhaustion, and use the 50-line as a momentum bias filter.

    Parameters
    ----------
    data : list[Data]
        Input price series containing the ``target`` column.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    target : str, optional
        Target column to apply RSI to, by default ``"close"``.
    length : PositiveInt, optional
        Lookback window in bars, by default 14.
    scalar : PositiveFloat, optional
        Output scaling. ``100`` produces the conventional 0–100 range,
        by default 100.0.
    drift : PositiveInt, optional
        Difference period for momentum, by default 1.

    Returns
    -------
    OBBject[list[RsiData]]
        RSI time series with warm-up rows dropped.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = RsiQueryParams(
        data=data,
        index=index,
        target=target,
        length=length,
        scalar=scalar,
        drift=drift,
    )
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    series = df.ta.rsi(
        close=params.target,
        length=params.length,
        scalar=params.scalar,
        drift=params.drift,
    )
    out = (
        pd.DataFrame({"rsi": series})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[RsiData(**row) for row in out.to_dict(orient="records")])


class StochQueryParams(QueryParams):
    """Query parameters for the Stochastic Oscillator endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series. ``high``, ``low``, and ``close`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    fast_k_period : PositiveInt, optional
        Fast %K lookback, by default 14.
    slow_d_period : PositiveInt, optional
        Slow %D smoothing, by default 3.
    slow_k_period : PositiveInt, optional
        Slow %K smoothing, by default 3.
    """

    __category__ = "oscillator"
    __output_columns__ = ("date", "k", "d")

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(default="date")
    fast_k_period: PositiveInt = Field(default=14, description="Fast %K lookback.")
    slow_d_period: PositiveInt = Field(default=3, description="Slow %D smoothing.")
    slow_k_period: PositiveInt = Field(default=3, description="Slow %K smoothing.")


class StochData(Data):
    """One row of the Stochastic Oscillator.

    Parameters
    ----------
    date : date | str
        Observation date.
    k : float, optional
        Slow %K — current close relative to the recent high/low range,
        smoothed by ``slow_k_period``.
    d : float, optional
        Slow %D — moving average of %K over ``slow_d_period`` bars.
    """

    date: datetime | dateType | str
    k: float | None = Field(description="%K — current close vs. recent range.")
    d: float | None = Field(description="%D — moving average of %K.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Stochastic oscillator on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "stoch = obb.technical.stoch(data=data)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def stoch(
    data: list[Data],
    index: str = "date",
    fast_k_period: int = 14,
    slow_d_period: int = 3,
    slow_k_period: int = 3,
) -> OBBject[list[Data]]:
    """Calculate the Stochastic Oscillator (%K and %D).

    The Stochastic Oscillator locates the most recent close within the trailing
    high–low range and rescales the result to a 0–100 band. Raw %K is the
    percentage position of close within the lookback range; slow %K applies a
    short smoothing, and %D is a further moving average of %K. Readings above
    80 indicate the close is near the period high (overbought), readings below
    20 indicate the close is near the period low (oversold). Crossovers
    between %K and %D, together with bullish or bearish divergences from
    price, are the conventional trading signals.

    Parameters
    ----------
    data : list[Data]
        OHLC price series. ``high``, ``low``, and ``close`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    fast_k_period : PositiveInt, optional
        Fast %K lookback, by default 14.
    slow_d_period : PositiveInt, optional
        Slow %D smoothing, by default 3.
    slow_k_period : PositiveInt, optional
        Slow %K smoothing, by default 3.

    Returns
    -------
    OBBject[list[StochData]]
        %K and %D time series with warm-up rows dropped.
    """
    import pandas_ta as ta  # noqa: F401

    params = StochQueryParams(
        data=data,
        index=index,
        fast_k_period=fast_k_period,
        slow_d_period=slow_d_period,
        slow_k_period=slow_k_period,
    )
    validate_data(
        params.data,
        [params.fast_k_period, params.slow_d_period, params.slow_k_period],
    )
    df = basemodel_to_df(params.data, index=params.index)
    table = df.ta.stoch(
        k=params.fast_k_period,
        d=params.slow_d_period,
        smooth_k=params.slow_k_period,
    )
    k_col = (
        f"STOCHk_{params.fast_k_period}_{params.slow_d_period}_{params.slow_k_period}"
    )
    d_col = (
        f"STOCHd_{params.fast_k_period}_{params.slow_d_period}_{params.slow_k_period}"
    )
    out = (
        table[[k_col, d_col]]
        .rename(columns={k_col: "k", d_col: "d"})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[StochData(**row) for row in out.to_dict(orient="records")])


class CciQueryParams(QueryParams):
    """Query parameters for the Commodity Channel Index endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series. ``high``, ``low``, and ``close`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Lookback window in bars, by default 14.
    scalar : PositiveFloat, optional
        Mean-deviation scaling factor (Lambert's original constant),
        by default 0.015.
    """

    __category__ = "oscillator"
    __output_columns__ = ("date", "cci")

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=14, description="Lookback window in bars.")
    scalar: PositiveFloat = Field(
        default=0.015,
        description="Mean-deviation scaling factor (Lambert's original constant).",
    )


class CciData(Data):
    """One row of the CCI time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    cci : float, optional
        CCI value over the trailing ``length`` bars. ``None`` for warm-up
        rows preceding ``length``.
    """

    date: datetime | dateType | str
    cci: float | None = Field(
        description="CCI value over the trailing ``length`` bars."
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="CCI(14) on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "cci = obb.technical.cci(data=data, length=14)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def cci(
    data: list[Data],
    index: str = "date",
    length: int = 14,
    scalar: float = 0.015,
) -> OBBject[list[Data]]:
    """Calculate the Commodity Channel Index (CCI), Lambert's mean-reversion oscillator.

    CCI measures the deviation of the current typical price — the average of
    high, low, and close — from its trailing simple moving average, normalised
    by the mean absolute deviation of typical price over the same window and
    scaled by Lambert's 0.015 constant. The constant is chosen so that
    approximately 70–80% of values fall in the ``±100`` band, leaving readings
    outside ``±100`` to flag unusually strong moves. Traders treat
    ``CCI > +100`` as a strong-trend or overbought signal and ``CCI < −100``
    as a strong-trend or oversold signal, and watch zero-line crossings as
    trend-change cues.

    Parameters
    ----------
    data : list[Data]
        OHLC price series. ``high``, ``low``, and ``close`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Lookback window in bars, by default 14.
    scalar : PositiveFloat, optional
        Mean-deviation scaling factor, by default 0.015.

    Returns
    -------
    OBBject[list[CciData]]
        CCI time series with warm-up rows dropped.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = CciQueryParams(data=data, index=index, length=length, scalar=scalar)
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    series = df.ta.cci(length=params.length, scalar=params.scalar)
    out = (
        pd.DataFrame({"cci": series})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[CciData(**row) for row in out.to_dict(orient="records")])


class FisherQueryParams(QueryParams):
    """Query parameters for the Fisher Transform endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series. ``high`` and ``low`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Fisher transform window, by default 14.
    signal : PositiveInt, optional
        Lag for the signal line, by default 1.
    """

    __category__ = "oscillator"
    __output_columns__ = ("date", "fisher", "signal")

    data: list[Data] = Field(description="OHLC price series (uses high + low).")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=14, description="Fisher transform window.")
    signal: PositiveInt = Field(default=1, description="Lag for the signal line.")


class FisherData(Data):
    """One row of the Fisher Transform output.

    Parameters
    ----------
    date : date | str
        Observation date.
    fisher : float, optional
        Fisher Transform value over the trailing ``length`` bars.
    signal : float, optional
        Lagged Fisher signal line trailing ``fisher`` by ``signal`` bars.
    """

    date: datetime | dateType | str
    fisher: float | None = Field(description="Fisher Transform value.")
    signal: float | None = Field(description="Lagged Fisher signal line.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Fisher Transform on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "fisher = obb.technical.fisher(data=data, length=14, signal=1)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def fisher(
    data: list[Data],
    index: str = "date",
    length: int = 14,
    signal: int = 1,
) -> OBBject[list[Data]]:
    """Calculate Ehlers' Fisher Transform of price with a signal line.

    The Fisher Transform rescales the median price (the average of high and
    low) into the ``[-1, 1]`` range over the lookback window, then applies the
    inverse hyperbolic tangent: ``0.5 * ln((1 + x) / (1 - x))``. The transform
    sharpens turning points by converting a typically near-Gaussian price
    distribution into one with heavier, more peaked tails, so extreme readings
    correspond more reliably to swing highs and lows. The signal line is a
    lagged copy of the transform; crossings between the two lines are used as
    timely entry and exit cues, especially around historical extremes.

    Parameters
    ----------
    data : list[Data]
        OHLC price series; ``high`` and ``low`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Fisher transform window, by default 14.
    signal : PositiveInt, optional
        Lag for the signal line, by default 1.

    Returns
    -------
    OBBject[list[FisherData]]
        Fisher and signal time series with warm-up rows dropped.
    """
    import pandas_ta as ta  # noqa: F401

    params = FisherQueryParams(data=data, index=index, length=length, signal=signal)
    validate_data(params.data, [params.length, params.signal])
    df = basemodel_to_df(params.data, index=params.index)
    table = df.ta.fisher(length=params.length, signal=params.signal)
    fisher_col = f"FISHERT_{params.length}_{params.signal}"
    signal_col = f"FISHERTs_{params.length}_{params.signal}"
    out = (
        table[[fisher_col, signal_col]]
        .rename(columns={fisher_col: "fisher", signal_col: "signal"})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[FisherData(**row) for row in out.to_dict(orient="records")])


class CgQueryParams(QueryParams):
    """Query parameters for the Center of Gravity endpoint.

    Parameters
    ----------
    data : list[Data]
        Price series. The implementation uses the median of high/low/close.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Lookback window in bars, by default 14.
    """

    __category__ = "oscillator"
    __output_columns__ = ("date", "cg")

    data: list[Data] = Field(description="Price series (uses high/low/close median).")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=14, description="Lookback window in bars.")


class CgData(Data):
    """One row of the Center of Gravity output.

    Parameters
    ----------
    date : date | str
        Observation date.
    cg : float, optional
        Center of Gravity value over the trailing ``length`` bars.
    """

    date: datetime | dateType | str
    cg: float | None = Field(description="Center of Gravity value.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Center of Gravity on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "cg = obb.technical.cg(data=data, length=14)",
            ],
        ),
        APIEx(parameters={"length": 2, "data": APIEx.mock_data("timeseries")}),
    ],
)
def cg(
    data: list[Data],
    index: str = "date",
    length: int = 14,
) -> OBBject[list[Data]]:
    """Calculate Ehlers' Center of Gravity oscillator.

    The Center of Gravity treats the trailing window of prices as a weighted
    distribution and reports the position of its centroid, weighting each
    price by its age within the window. Because the calculation is a linear,
    minimum-lag combination of recent prices, it responds to swings with
    almost no delay relative to moving-average oscillators. Ehlers proposed
    the indicator as a near-zero-lag turning-point detector; traders use
    crossings against a one-bar-lagged copy or against zero to flag
    short-term direction changes in oscillatory markets.

    Parameters
    ----------
    data : list[Data]
        Price series; uses median of high/low/close.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Lookback window in bars, by default 14.

    Returns
    -------
    OBBject[list[CgData]]
        Center of Gravity time series with warm-up rows dropped.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = CgQueryParams(data=data, index=index, length=length)
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    series = df.ta.cg(length=params.length)
    out = (
        pd.DataFrame({"cg": series})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[CgData(**row) for row in out.to_dict(orient="records")])


class WilliamsRQueryParams(QueryParams):
    """Query parameters for the Williams %R endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series. ``high``, ``low``, and ``close`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Lookback window in bars, by default 14.
    """

    __category__ = "oscillator"
    __output_columns__ = ("date", "williams_r")

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=14, description="Lookback window in bars.")


class WilliamsRData(Data):
    """One row of the Williams %R output.

    Parameters
    ----------
    date : date | str
        Observation date.
    williams_r : float, optional
        Williams %R — close relative to the trailing high/low range, scaled
        to the range ``[-100, 0]``.
    """

    date: datetime | dateType | str
    williams_r: float | None = Field(
        description="Williams %R — close relative to the trailing high/low range (−100 to 0).",
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Williams %R on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "wr = obb.technical.williams_r(data=data, length=14)",
            ],
        ),
        APIEx(parameters={"length": 14, "data": APIEx.mock_data("timeseries")}),
    ],
)
def williams_r(
    data: list[Data],
    index: str = "date",
    length: int = 14,
) -> OBBject[list[Data]]:
    """Calculate Williams %R, a momentum oscillator inverted from fast stochastic %K.

    Williams %R locates the current close within the trailing high–low range
    and scales the result to the ``[-100, 0]`` band: ``-100 * (highest_high
    - close) / (highest_high - lowest_low)``. Mechanically it is the negative
    image of fast stochastic %K. Readings above ``-20`` indicate the close
    is near the recent high (overbought), and readings below ``-80`` indicate
    the close is near the recent low (oversold). Failure swings, in which the
    indicator fails to reach an extreme after a price extreme, are a
    traditional reversal signal.

    Parameters
    ----------
    data : list[Data]
        OHLC price series; ``high``, ``low``, and ``close`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Lookback window in bars, by default 14.

    Returns
    -------
    OBBject[list[WilliamsRData]]
        Williams %R time series with warm-up rows dropped.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = WilliamsRQueryParams(data=data, index=index, length=length)
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    series = df.ta.willr(length=params.length)
    out = (
        pd.DataFrame({"williams_r": series})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(
        results=[WilliamsRData(**row) for row in out.to_dict(orient="records")]
    )


class MfiQueryParams(QueryParams):
    """Query parameters for the Money Flow Index endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLCV price series. ``high``, ``low``, ``close``, and ``volume`` are
        required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Lookback window in bars, by default 14.
    """

    __category__ = "oscillator"
    __output_columns__ = ("date", "mfi")

    data: list[Data] = Field(description="OHLCV price series — ``volume`` is required.")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=14, description="Lookback window in bars.")


class MfiData(Data):
    """One row of the Money Flow Index output.

    Parameters
    ----------
    date : date | str
        Observation date.
    mfi : float, optional
        Money Flow Index — volume-weighted RSI on typical price, scaled to
        the 0–100 range.
    """

    date: datetime | dateType | str
    mfi: float | None = Field(
        description="Money Flow Index — volume-weighted RSI on typical price (0–100).",
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="MFI(14) on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "mfi = obb.technical.mfi(data=data, length=14)",
            ],
        ),
        APIEx(parameters={"length": 14, "data": APIEx.mock_data("timeseries")}),
    ],
)
def mfi(
    data: list[Data],
    index: str = "date",
    length: int = 14,
) -> OBBject[list[Data]]:
    """Calculate the Money Flow Index (MFI), a volume-weighted RSI.

    MFI computes raw money flow as typical price times volume on each bar,
    classifies each bar as positive or negative depending on whether typical
    price rose or fell relative to the prior bar, then forms the money flow
    ratio of positive to negative flow over the lookback. The ratio is
    transformed into a bounded 0–100 oscillator using the same algebra as
    RSI. Because volume enters the numerator, MFI flags moves that lack
    participation; conventional overbought and oversold thresholds are 80
    and 20, and divergences against price are a standard reversal signal.

    Parameters
    ----------
    data : list[Data]
        OHLCV price series; ``high``, ``low``, ``close``, and ``volume``
        are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Lookback window in bars, by default 14.

    Returns
    -------
    OBBject[list[MfiData]]
        MFI time series with warm-up rows dropped.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = MfiQueryParams(data=data, index=index, length=length)
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    series = df.ta.mfi(length=params.length)
    out = (
        pd.DataFrame({"mfi": series})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[MfiData(**row) for row in out.to_dict(orient="records")])


class TrixQueryParams(QueryParams):
    """Query parameters for the TRIX endpoint.

    Parameters
    ----------
    data : list[Data]
        Input price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    target : str, optional
        Target column to apply TRIX to, by default ``"close"``.
    length : PositiveInt, optional
        Triple-EMA window, by default 30.
    signal : PositiveInt, optional
        Signal line EMA length, by default 9.
    """

    __category__ = "oscillator"
    __output_columns__ = ("date", "trix", "signal")

    data: list[Data] = Field(description="Input price series.")
    index: str = Field(default="date")
    target: str = Field(default="close", description="Target column to apply TRIX to.")
    length: PositiveInt = Field(default=30, description="Triple-EMA window.")
    signal: PositiveInt = Field(default=9, description="Signal line EMA length.")


class TrixData(Data):
    """One row of the TRIX output.

    Parameters
    ----------
    date : date | str
        Observation date.
    trix : float, optional
        1-day rate of change of a triple-EMA of ``target``.
    signal : float, optional
        EMA of TRIX over ``signal`` bars.
    """

    date: datetime | dateType | str
    trix: float | None = Field(description="1-day ROC of a triple-EMA of ``target``.")
    signal: float | None = Field(description="EMA of TRIX, length ``signal``.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="TRIX(30, 9) on daily TSLA closes.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "trix = obb.technical.trix(data=data, length=30, signal=9)",
            ],
        ),
        APIEx(
            parameters={"length": 5, "signal": 3, "data": APIEx.mock_data("timeseries")}
        ),
    ],
)
def trix(
    data: list[Data],
    index: str = "date",
    target: str = "close",
    length: int = 30,
    signal: int = 9,
) -> OBBject[list[Data]]:
    """Calculate TRIX — the rate of change of a triple-smoothed EMA — with signal.

    TRIX applies three successive exponential moving averages of length
    ``length`` to the target price and then reports the percentage rate of
    change of the resulting series from one bar to the next. The triple
    smoothing strips out cycles shorter than the EMA window, so TRIX
    oscillates around zero and isolates the dominant trend. Traders treat
    zero-line crossings as trend changes and crossings of TRIX above or
    below its signal-line EMA as confirmation, with divergences against
    price serving as exhaustion warnings.

    Parameters
    ----------
    data : list[Data]
        Input price series containing the ``target`` column.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    target : str, optional
        Target column to apply TRIX to, by default ``"close"``.
    length : PositiveInt, optional
        Triple-EMA window, by default 30.
    signal : PositiveInt, optional
        Signal line EMA length, by default 9.

    Returns
    -------
    OBBject[list[TrixData]]
        TRIX and signal time series with warm-up rows dropped.
    """
    import pandas_ta as ta  # noqa: F401

    params = TrixQueryParams(
        data=data, index=index, target=target, length=length, signal=signal
    )
    validate_data(params.data, [params.length, params.signal])
    df = basemodel_to_df(params.data, index=params.index)
    target_df = df[[params.target]]
    table = target_df.ta.trix(
        close=params.target, length=params.length, signal=params.signal
    )
    trix_col = f"TRIX_{params.length}_{params.signal}"
    signal_col = f"TRIXs_{params.length}_{params.signal}"
    out = (
        table[[trix_col, signal_col]]
        .rename(columns={trix_col: "trix", signal_col: "signal"})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[TrixData(**row) for row in out.to_dict(orient="records")])


class UltimateOscillatorQueryParams(QueryParams):
    """Query parameters for Larry Williams' Ultimate Oscillator endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series. ``high``, ``low``, and ``close`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    fast : PositiveInt, optional
        Short-period lookback, by default 7.
    medium : PositiveInt, optional
        Medium-period lookback, by default 14.
    slow : PositiveInt, optional
        Long-period lookback, by default 28.
    fast_weight : PositiveFloat, optional
        Weight applied to the fast period, by default 4.0.
    medium_weight : PositiveFloat, optional
        Weight applied to the medium period, by default 2.0.
    slow_weight : PositiveFloat, optional
        Weight applied to the slow period, by default 1.0.
    """

    __category__ = "oscillator"
    __output_columns__ = ("date", "ultimate_oscillator")

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(default="date")
    fast: PositiveInt = Field(default=7, description="Short-period lookback.")
    medium: PositiveInt = Field(default=14, description="Medium-period lookback.")
    slow: PositiveInt = Field(default=28, description="Long-period lookback.")
    fast_weight: PositiveFloat = Field(
        default=4.0, description="Weight applied to the fast period."
    )
    medium_weight: PositiveFloat = Field(
        default=2.0, description="Weight applied to the medium period."
    )
    slow_weight: PositiveFloat = Field(
        default=1.0, description="Weight applied to the slow period."
    )


class UltimateOscillatorData(Data):
    """One row of the Ultimate Oscillator output.

    Parameters
    ----------
    date : date | str
        Observation date.
    ultimate_oscillator : float, optional
        Weighted blend of buying pressure over the fast, medium, and slow
        timeframes, scaled to the 0–100 range.
    """

    date: datetime | dateType | str
    ultimate_oscillator: float | None = Field(
        description="Weighted blend of buying pressure over three timeframes (0–100).",
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Ultimate Oscillator on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "uo = obb.technical.ultimate_oscillator(data=data)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def ultimate_oscillator(
    data: list[Data],
    index: str = "date",
    fast: int = 7,
    medium: int = 14,
    slow: int = 28,
    fast_weight: float = 4.0,
    medium_weight: float = 2.0,
    slow_weight: float = 1.0,
) -> OBBject[list[Data]]:
    """Calculate Larry Williams' Ultimate Oscillator across three timeframes.

    The Ultimate Oscillator computes buying pressure on each bar as the close
    minus the lesser of the prior close and the current low, normalises it
    by true range, and forms three rolling sums over the fast, medium, and
    slow lookbacks. The three normalised sums are combined with user-supplied
    weights and rescaled to a 0–100 oscillator. Folding multiple horizons
    into a single line reduces the false signals that plague single-period
    momentum oscillators. Traders watch for divergences between price and
    indicator extremes (notably below 30 or above 70) as the highest-quality
    reversal cues.

    Parameters
    ----------
    data : list[Data]
        OHLC price series; ``high``, ``low``, and ``close`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    fast : PositiveInt, optional
        Short-period lookback, by default 7.
    medium : PositiveInt, optional
        Medium-period lookback, by default 14.
    slow : PositiveInt, optional
        Long-period lookback, by default 28.
    fast_weight : PositiveFloat, optional
        Weight applied to the fast period, by default 4.0.
    medium_weight : PositiveFloat, optional
        Weight applied to the medium period, by default 2.0.
    slow_weight : PositiveFloat, optional
        Weight applied to the slow period, by default 1.0.

    Returns
    -------
    OBBject[list[UltimateOscillatorData]]
        Ultimate Oscillator time series with warm-up rows dropped.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = UltimateOscillatorQueryParams(
        data=data,
        index=index,
        fast=fast,
        medium=medium,
        slow=slow,
        fast_weight=fast_weight,
        medium_weight=medium_weight,
        slow_weight=slow_weight,
    )
    validate_data(params.data, [params.fast, params.medium, params.slow])
    df = basemodel_to_df(params.data, index=params.index)
    series = df.ta.uo(
        fast=params.fast,
        medium=params.medium,
        slow=params.slow,
        fast_w=params.fast_weight,
        medium_w=params.medium_weight,
        slow_w=params.slow_weight,
    )
    out = (
        pd.DataFrame({"ultimate_oscillator": series})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(
        results=[UltimateOscillatorData(**row) for row in out.to_dict(orient="records")]
    )


class AwesomeOscillatorQueryParams(QueryParams):
    """Query parameters for Bill Williams' Awesome Oscillator endpoint.

    Parameters
    ----------
    data : list[Data]
        Price series. Uses the median of high and low on each bar.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    fast : PositiveInt, optional
        Short SMA window on median price, by default 5.
    slow : PositiveInt, optional
        Long SMA window on median price, by default 34.
    """

    __category__ = "oscillator"
    __output_columns__ = ("date", "awesome_oscillator")

    data: list[Data] = Field(description="Price series — uses median of high/low.")
    index: str = Field(default="date")
    fast: PositiveInt = Field(
        default=5, description="Short SMA window on median price."
    )
    slow: PositiveInt = Field(
        default=34, description="Long SMA window on median price."
    )


class AwesomeOscillatorData(Data):
    """One row of the Awesome Oscillator output.

    Parameters
    ----------
    date : date | str
        Observation date.
    awesome_oscillator : float, optional
        Fast SMA minus slow SMA of median price.
    """

    date: datetime | dateType | str
    awesome_oscillator: float | None = Field(
        description="Fast SMA minus slow SMA of median price.",
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Awesome Oscillator on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "ao = obb.technical.awesome_oscillator(data=data)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def awesome_oscillator(
    data: list[Data],
    index: str = "date",
    fast: int = 5,
    slow: int = 34,
) -> OBBject[list[Data]]:
    """Calculate Bill Williams' Awesome Oscillator as a momentum histogram.

    The Awesome Oscillator subtracts a long simple moving average of the
    median price (typically 34 bars) from a short simple moving average
    (typically 5 bars), both taken on ``(high + low) / 2``. The difference
    is plotted as a histogram around zero: positive values indicate
    short-term momentum is faster than long-term momentum (bullish bias),
    negative values indicate the opposite. Traders watch zero-line
    crossings, the ``twin peaks`` reversal pattern in which two successive
    troughs or peaks diverge from price, and the ``saucer`` pattern of
    three consecutive bars on the same side of zero with changing slope.

    Parameters
    ----------
    data : list[Data]
        Price series; uses the median of high and low.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    fast : PositiveInt, optional
        Short SMA window on median price, by default 5.
    slow : PositiveInt, optional
        Long SMA window on median price, by default 34.

    Returns
    -------
    OBBject[list[AwesomeOscillatorData]]
        Awesome Oscillator time series with warm-up rows dropped.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = AwesomeOscillatorQueryParams(data=data, index=index, fast=fast, slow=slow)
    validate_data(params.data, [params.fast, params.slow])
    df = basemodel_to_df(params.data, index=params.index)
    series = df.ta.ao(fast=params.fast, slow=params.slow)
    out = (
        pd.DataFrame({"awesome_oscillator": series})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(
        results=[AwesomeOscillatorData(**row) for row in out.to_dict(orient="records")]
    )


__all__ = [
    "AwesomeOscillatorData",
    "AwesomeOscillatorQueryParams",
    "CciData",
    "CciQueryParams",
    "CgData",
    "CgQueryParams",
    "FisherData",
    "FisherQueryParams",
    "MfiData",
    "MfiQueryParams",
    "RsiData",
    "RsiQueryParams",
    "StochData",
    "StochQueryParams",
    "TrixData",
    "TrixQueryParams",
    "UltimateOscillatorData",
    "UltimateOscillatorQueryParams",
    "WilliamsRData",
    "WilliamsRQueryParams",
    "awesome_oscillator",
    "cci",
    "cg",
    "fisher",
    "mfi",
    "router",
    "rsi",
    "stoch",
    "trix",
    "ultimate_oscillator",
    "williams_r",
]
