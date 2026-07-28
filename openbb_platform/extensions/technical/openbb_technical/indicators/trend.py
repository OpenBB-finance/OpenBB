"""Trend-family technical indicators."""

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


router = Router(prefix="", description="Trend indicators.")


class MacdQueryParams(QueryParams):
    """Query parameters for the MACD endpoint.

    Parameters
    ----------
    data : list[Data]
        Input price series containing the ``target`` column.
    target : str, optional
        Column to compute MACD on, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    fast : PositiveInt, optional
        Fast EMA window in bars, by default 12.
    slow : PositiveInt, optional
        Slow EMA window in bars, by default 26.
    signal : PositiveInt, optional
        Signal-line EMA window in bars, by default 9.
    """

    __category__ = "trend"
    __output_columns__ = ("date", "macd", "signal", "histogram")

    data: list[Data] = Field(description="Input price series.")
    target: str = Field(default="close", description="Column to compute MACD on.")
    index: str = Field(default="date", description="Index column name in ``data``.")
    fast: PositiveInt = Field(default=12, description="Fast EMA window.")
    slow: PositiveInt = Field(default=26, description="Slow EMA window.")
    signal: PositiveInt = Field(default=9, description="Signal-line EMA window.")


class MacdData(Data):
    """One row of the MACD time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    macd : float, optional
        MACD line — fast EMA of ``target`` minus slow EMA of ``target``.
    signal : float, optional
        Signal line — EMA of the MACD line over ``signal`` bars.
    histogram : float, optional
        MACD line minus signal line.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    macd: float | None = Field(description="MACD line — fast EMA minus slow EMA.")
    signal: float | None = Field(description="Signal line — EMA of MACD.")
    histogram: float | None = Field(description="MACD minus signal.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="MACD(12,26,9) on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "macd = obb.technical.macd(data=data, fast=12, slow=26, signal=9)",
            ],
        ),
        APIEx(
            description="MACD with short windows for mock data.",
            parameters={
                "data": APIEx.mock_data("timeseries"),
                "fast": 2,
                "slow": 3,
                "signal": 1,
            },
        ),
    ],
)
def macd(params: MacdQueryParams) -> OBBject[list[MacdData]]:
    """Calculate the Moving Average Convergence Divergence (MACD) oscillator."""
    import pandas_ta as ta  # noqa: F401

    validate_data(params.data, [params.fast, params.slow, params.signal])
    df = basemodel_to_df(params.data, index=params.index)
    result = (
        df[params.target]
        .to_frame()
        .ta.macd(
            fast=params.fast,
            slow=params.slow,
            signal=params.signal,
            close=params.target,
        )
    )
    rename = {
        f"MACD_{params.fast}_{params.slow}_{params.signal}": "macd",
        f"MACDs_{params.fast}_{params.slow}_{params.signal}": "signal",
        f"MACDh_{params.fast}_{params.slow}_{params.signal}": "histogram",
    }
    out = (
        result.rename(columns=rename)
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    out = out[["date", "macd", "signal", "histogram"]]
    return OBBject(results=[MacdData(**row) for row in out.to_dict(orient="records")])


class AdxQueryParams(QueryParams):
    """Query parameters for the ADX endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series. ``high``, ``low``, and ``close`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        ADX lookback window in bars, by default 14.
    scalar : PositiveFloat, optional
        Output magnification factor, by default 100.0.
    drift : PositiveInt, optional
        Difference period for directional movement, by default 1.
    """

    __category__ = "trend"
    __output_columns__ = ("date", "adx")

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    length: PositiveInt = Field(default=14, description="ADX lookback window.")
    scalar: PositiveFloat = Field(
        default=100.0, description="Output magnification factor."
    )
    drift: PositiveInt = Field(
        default=1, description="Difference period for directional movement."
    )


class AdxData(Data):
    """One row of the ADX time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    adx : float, optional
        Average Directional Index over the trailing ``length`` bars. ``None``
        for warm-up rows preceding ``length``.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    adx: float | None = Field(
        description="Average Directional Index — trend-strength score."
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="ADX(14) on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "adx = obb.technical.adx(data=data, length=14)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 2}),
    ],
)
def adx(params: AdxQueryParams) -> OBBject[list[AdxData]]:
    """Calculate Wilder's Average Directional Index (ADX), a trend-strength gauge."""
    import pandas_ta as ta  # noqa: F401

    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    result = df.ta.adx(length=params.length, scalar=params.scalar, drift=params.drift)
    series = result[f"ADX_{params.length}"].rename("adx")
    out = (
        series.to_frame().dropna().reset_index().rename(columns={params.index: "date"})
    )
    return OBBject(results=[AdxData(**row) for row in out.to_dict(orient="records")])


class DiQueryParams(QueryParams):
    """Query parameters for the Directional Indicators endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series. ``high``, ``low``, and ``close`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Lookback window for +DI and -DI in bars, by default 14.
    scalar : PositiveFloat, optional
        Output magnification factor, by default 100.0.
    drift : PositiveInt, optional
        Difference period for directional movement, by default 1.
    """

    __category__ = "trend"
    __output_columns__ = ("date", "plus_di", "minus_di", "dx")

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    length: PositiveInt = Field(
        default=14, description="Lookback window for +DI / -DI."
    )
    scalar: PositiveFloat = Field(
        default=100.0, description="Output magnification factor."
    )
    drift: PositiveInt = Field(
        default=1, description="Difference period for directional movement."
    )


class DiData(Data):
    """One row of the Directional Indicators time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    plus_di : float, optional
        Positive Directional Indicator (+DI) — Wilder-smoothed upward
        directional movement, scaled by ``scalar``.
    minus_di : float, optional
        Negative Directional Indicator (-DI) — Wilder-smoothed downward
        directional movement, scaled by ``scalar``.
    dx : float, optional
        Raw Directional Index ``|+DI - -DI| / (+DI + -DI) * scalar``.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    plus_di: float | None = Field(description="Positive Directional Indicator (+DI).")
    minus_di: float | None = Field(description="Negative Directional Indicator (-DI).")
    dx: float | None = Field(
        description="Directional Index — |+DI - -DI| / (+DI + -DI) * scalar."
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="+DI / -DI / DX(14) on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "di = obb.technical.di(data=data, length=14)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 2}),
    ],
)
def di(params: DiQueryParams) -> OBBject[list[DiData]]:
    """Calculate the Directional Indicators (+DI, -DI) and raw DX from Wilder's system."""
    import pandas_ta as ta  # noqa: F401

    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    result = df.ta.adx(length=params.length, scalar=params.scalar, drift=params.drift)
    plus = result[f"DMP_{params.length}"]
    minus = result[f"DMN_{params.length}"]
    total = plus + minus
    dx_series = (plus - minus).abs() / total.where(total != 0) * params.scalar
    out = (
        plus.to_frame(name="plus_di")
        .assign(minus_di=minus, dx=dx_series)
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[DiData(**row) for row in out.to_dict(orient="records")])


class AroonQueryParams(QueryParams):
    """Query parameters for the Aroon endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series. ``high`` and ``low`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Aroon lookback window in bars, by default 25.
    scalar : PositiveFloat, optional
        Output magnification factor, by default 100.0.
    """

    __category__ = "trend"
    __output_columns__ = ("date", "aroon_up", "aroon_down", "aroon_oscillator")

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    length: PositiveInt = Field(default=25, description="Aroon lookback window.")
    scalar: PositiveFloat = Field(
        default=100.0, description="Output magnification factor."
    )


class AroonData(Data):
    """One row of the Aroon time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    aroon_up : float, optional
        Bars since the highest high over the trailing ``length`` bars, scaled
        to ``[0, scalar]``. High values indicate a recent new high.
    aroon_down : float, optional
        Bars since the lowest low over the trailing ``length`` bars, scaled
        to ``[0, scalar]``. High values indicate a recent new low.
    aroon_oscillator : float, optional
        Difference ``aroon_up - aroon_down``; positive in uptrends, negative
        in downtrends.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    aroon_up: float | None = Field(description="Bars since the highest high, scaled.")
    aroon_down: float | None = Field(description="Bars since the lowest low, scaled.")
    aroon_oscillator: float | None = Field(
        description="``aroon_up`` minus ``aroon_down``."
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Aroon(25) on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "aroon = obb.technical.aroon(data=data, length=25)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 2}),
    ],
)
def aroon(params: AroonQueryParams) -> OBBject[list[AroonData]]:
    """Calculate the Aroon Up, Aroon Down, and Aroon Oscillator series."""
    import pandas_ta as ta  # noqa: F401

    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    result = df.ta.aroon(length=params.length, scalar=params.scalar)
    rename = {
        f"AROONU_{params.length}": "aroon_up",
        f"AROOND_{params.length}": "aroon_down",
        f"AROONOSC_{params.length}": "aroon_oscillator",
    }
    out = (
        result.rename(columns=rename)
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    out = out[["date", "aroon_up", "aroon_down", "aroon_oscillator"]]
    return OBBject(results=[AroonData(**row) for row in out.to_dict(orient="records")])


class ChoppinessQueryParams(QueryParams):
    """Query parameters for the Choppiness Index endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series. ``high``, ``low``, and ``close`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Choppiness lookback window in bars, by default 14.
    atr_length : PositiveInt, optional
        ATR window used inside the choppiness calculation, by default 1.
    scalar : PositiveFloat, optional
        Output magnification factor, by default 100.0.
    """

    __category__ = "trend"
    __output_columns__ = ("date", "choppiness")

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    length: PositiveInt = Field(default=14, description="Choppiness lookback window.")
    atr_length: PositiveInt = Field(
        default=1, description="ATR window used inside choppiness."
    )
    scalar: PositiveFloat = Field(
        default=100.0, description="Output magnification factor."
    )


class ChoppinessData(Data):
    """One row of the Choppiness Index time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    choppiness : float, optional
        Choppiness Index over the trailing ``length`` bars. High values
        (typically above ~61.8) indicate sideways, choppy action; low values
        (typically below ~38.2) indicate a directional trend.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    choppiness: float | None = Field(
        description="Choppiness Index — high values mean sideways action."
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Choppiness(14) on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "chop = obb.technical.choppiness(data=data, length=14)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 2}),
    ],
)
def choppiness(params: ChoppinessQueryParams) -> OBBject[list[ChoppinessData]]:
    """Calculate the Choppiness Index, a trending-vs-sideways regime classifier."""
    import pandas_ta as ta  # noqa: F401

    validate_data(params.data, [params.length, params.atr_length])
    df = basemodel_to_df(params.data, index=params.index)
    series = df.ta.chop(
        length=params.length,
        atr_length=params.atr_length,
        scalar=params.scalar,
    ).rename("choppiness")
    out = (
        series.to_frame().dropna().reset_index().rename(columns={params.index: "date"})
    )
    return OBBject(
        results=[ChoppinessData(**row) for row in out.to_dict(orient="records")]
    )


__all__ = [
    "AdxData",
    "AdxQueryParams",
    "AroonData",
    "AroonQueryParams",
    "ChoppinessData",
    "ChoppinessQueryParams",
    "DiData",
    "DiQueryParams",
    "MacdData",
    "MacdQueryParams",
    "adx",
    "aroon",
    "choppiness",
    "di",
    "macd",
    "router",
]
