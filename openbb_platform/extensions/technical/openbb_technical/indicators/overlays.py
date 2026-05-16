"""Overlay-family technical indicators."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import TYPE_CHECKING, Literal

from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.utils import basemodel_to_df
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, NonNegativeInt, PositiveFloat, PositiveInt, field_validator

from openbb_technical.helpers import validate_data

# Bare 'date' alias for function signatures so the static-package builder
# writes 'date' (which it imports from datetime) rather than 'dateType' which it does not.
date = dateType


router = Router(prefix="", description="Overlay indicators.")


def _nan_to_none(row: dict) -> dict:
    """Replace ``float('nan')`` values with ``None`` so pydantic emits explicit nulls.

    Parameters
    ----------
    row : dict
        Mapping from column name to scalar value.

    Returns
    -------
    dict
        Same mapping with any NaN float replaced by ``None``.
    """
    import math

    return {
        k: (None if isinstance(v, float) and math.isnan(v) else v)
        for k, v in row.items()
    }


if TYPE_CHECKING:
    import pandas as pd


def _single_overlay(
    df,
    indicator: str,
    target: str,
    length: int,
    offset: int,
    extra: dict | None = None,
) -> pd.DataFrame:
    """Run a single-output pandas-ta moving average on the target column.

    Parameters
    ----------
    df : pandas.DataFrame
        Source frame containing the target column.
    indicator : str
        Name of the pandas-ta moving-average accessor (e.g. ``"sma"``).
    target : str
        Column in ``df`` to smooth.
    length : int
        Window length in bars.
    offset : int
        Output offset; positive values shift the series forward.
    extra : dict, optional
        Additional keyword arguments forwarded to the pandas-ta accessor.

    Returns
    -------
    pandas.DataFrame
        Single-column frame named after ``indicator`` with warm-up rows
        dropped and the index reset.
    """
    import pandas as pd

    extra = extra or {}
    series = getattr(df[[target]].ta, indicator)(
        length=length, offset=offset, close=target, **extra
    )
    return pd.DataFrame({indicator: series}).dropna().reset_index()


class SmaQueryParams(QueryParams):
    """Query parameters for the Simple Moving Average endpoint.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Window length in bars, by default 50.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.
    """

    __category__ = "overlay"
    __output_columns__ = ("date", "sma")

    data: list[Data] = Field(description="Price series.")
    target: str = Field(default="close", description="Column to smooth.")
    index: str = Field(default="date", description="Index column name in ``data``.")
    length: PositiveInt = Field(default=50, description="Window length in bars.")
    offset: int = Field(
        default=0, description="Output offset, positive shifts forward."
    )


class SmaData(Data):
    """One row of the SMA time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    sma : float, optional
        Simple moving average of ``target`` over the trailing ``length`` bars.
        ``None`` during the warm-up rows preceding ``length``.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    sma: float | None = Field(
        description="Simple moving average of ``target`` over ``length`` bars."
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="50-bar SMA on TSLA close.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "sma = obb.technical.sma(data=data, length=50)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 2}),
    ],
)
def sma(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """Calculate the Simple Moving Average over the trailing window.

    The Simple Moving Average is the unweighted arithmetic mean of the most
    recent ``length`` observations of ``target``. Every observation in the
    window receives identical weight, so the SMA lags faster smoothers but is
    the simplest baseline reference for trend direction. Traders commonly use
    the SMA to define support and resistance, to identify trend-following
    crossovers between fast and slow windows, and as the centreline for
    volatility envelopes such as Bollinger Bands.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Window length in bars, by default 50.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.

    Returns
    -------
    OBBject[list[SmaData]]
        Simple moving-average time series with warm-up rows dropped.
    """
    import pandas_ta as ta  # noqa: F401

    params = SmaQueryParams(
        data=data, target=target, index=index, length=length, offset=offset
    )
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    out = _single_overlay(
        df, "sma", params.target, params.length, params.offset
    ).rename(columns={params.index: "date"})
    return OBBject(results=[SmaData(**row) for row in out.to_dict(orient="records")])


class EmaQueryParams(QueryParams):
    """Query parameters for the Exponential Moving Average endpoint.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        EMA period in bars, by default 50.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.
    """

    __category__ = "overlay"
    __output_columns__ = ("date", "ema")

    data: list[Data] = Field(description="Price series.")
    target: str = Field(default="close")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=50, description="EMA period.")
    offset: int = Field(default=0)


class EmaData(Data):
    """One row of the EMA time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    ema : float, optional
        Exponential moving average of ``target``. ``None`` during the warm-up
        rows preceding ``length``.
    """

    date: datetime | dateType | str
    ema: float | None = Field(description="Exponential moving average of ``target``.")


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 2})],
)
def ema(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """Calculate the Exponential Moving Average with recency-weighted smoothing.

    The Exponential Moving Average applies geometrically decaying weights to
    historical observations of ``target``, with the smoothing constant
    ``alpha = 2 / (length + 1)``. Because the most recent bar carries the most
    weight, the EMA reacts to new information faster than the SMA at the cost
    of being more sensitive to noise. EMAs are widely used as fast and slow
    legs of crossover systems and as the smoothing kernel inside the MACD,
    Keltner Channels, and many momentum oscillators.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        EMA period in bars, by default 50.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.

    Returns
    -------
    OBBject[list[EmaData]]
        Exponential moving-average time series with warm-up rows dropped.
    """
    import pandas_ta as ta  # noqa: F401

    params = EmaQueryParams(
        data=data, target=target, index=index, length=length, offset=offset
    )
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    out = _single_overlay(
        df, "ema", params.target, params.length, params.offset
    ).rename(columns={params.index: "date"})
    return OBBject(results=[EmaData(**row) for row in out.to_dict(orient="records")])


class HmaQueryParams(QueryParams):
    """Query parameters for the Hull Moving Average endpoint.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        HMA period in bars, by default 50.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.
    """

    __category__ = "overlay"
    __output_columns__ = ("date", "hma")

    data: list[Data] = Field(description="Price series.")
    target: str = Field(default="close")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=50, description="HMA period.")
    offset: int = Field(default=0)


class HmaData(Data):
    """One row of the Hull Moving Average time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    hma : float, optional
        Hull moving average — a lag-reduced blend of two WMAs of differing
        lengths re-smoothed by the WMA of ``sqrt(length)``. ``None`` during
        warm-up.
    """

    date: datetime | dateType | str
    hma: float | None = Field(
        description="Hull moving average — lag-reduced WMA blend."
    )


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 4})],
)
def hma(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """Calculate Alan Hull's lag-reduced moving average.

    The Hull Moving Average computes ``WMA(2 * WMA(length/2) - WMA(length))``
    re-smoothed by ``WMA(sqrt(length))``. The subtraction of the slower WMA
    from twice the faster WMA cancels much of the lag inherent in linearly
    weighted averages, and the final ``sqrt(length)`` WMA restores smoothness.
    The HMA tracks price almost as quickly as the underlying series while
    suppressing high-frequency noise, which makes it popular for trend
    identification and as a centreline for directional trading systems.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        HMA period in bars, by default 50.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.

    Returns
    -------
    OBBject[list[HmaData]]
        Hull moving-average time series with warm-up rows dropped.
    """
    import pandas_ta as ta  # noqa: F401

    params = HmaQueryParams(
        data=data, target=target, index=index, length=length, offset=offset
    )
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    out = _single_overlay(
        df, "hma", params.target, params.length, params.offset
    ).rename(columns={params.index: "date"})
    return OBBject(results=[HmaData(**row) for row in out.to_dict(orient="records")])


class WmaQueryParams(QueryParams):
    """Query parameters for the Weighted Moving Average endpoint.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        WMA period in bars, by default 50.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.
    """

    __category__ = "overlay"
    __output_columns__ = ("date", "wma")

    data: list[Data] = Field(description="Price series.")
    target: str = Field(default="close")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=50, description="WMA period.")
    offset: int = Field(default=0)


class WmaData(Data):
    """One row of the WMA time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    wma : float, optional
        Linearly-weighted moving average of ``target`` over the trailing
        ``length`` bars. ``None`` during warm-up.
    """

    date: datetime | dateType | str
    wma: float | None = Field(
        description="Linearly-weighted moving average of ``target``."
    )


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 2})],
)
def wma(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """Calculate the linearly-Weighted Moving Average.

    The Weighted Moving Average assigns linearly decreasing integer weights to
    the observations in the trailing window — the most recent bar gets weight
    ``length``, the next gets weight ``length - 1``, and so on down to weight
    one. The weighted sum is divided by the triangular number ``length *
    (length + 1) / 2``. The WMA is more responsive than the SMA but more
    stable than the EMA at equal length, making it a useful intermediate
    smoother and the building block for the Hull Moving Average.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        WMA period in bars, by default 50.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.

    Returns
    -------
    OBBject[list[WmaData]]
        Weighted moving-average time series with warm-up rows dropped.
    """
    import pandas_ta as ta  # noqa: F401

    params = WmaQueryParams(
        data=data, target=target, index=index, length=length, offset=offset
    )
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    out = _single_overlay(
        df, "wma", params.target, params.length, params.offset
    ).rename(columns={params.index: "date"})
    return OBBject(results=[WmaData(**row) for row in out.to_dict(orient="records")])


class ZlmaQueryParams(QueryParams):
    """Query parameters for the Zero-Lag Moving Average endpoint.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        ZLMA period in bars, by default 50.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.
    """

    __category__ = "overlay"
    __output_columns__ = ("date", "zlma")

    data: list[Data] = Field(description="Price series.")
    target: str = Field(default="close")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=50, description="ZLMA period.")
    offset: int = Field(default=0)


class ZlmaData(Data):
    """One row of the Zero-Lag Moving Average time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    zlma : float, optional
        Zero-lag exponential moving average of ``target`` per Ehlers and Way.
        ``None`` during warm-up.
    """

    date: datetime | dateType | str
    zlma: float | None = Field(
        description="Zero-Lag EMA of ``target`` — Ehlers/Way de-lagged EMA."
    )


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 2})],
)
def zlma(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 50,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """Calculate the Zero-Lag Exponential Moving Average of Ehlers and Way.

    The Zero-Lag Moving Average attempts to remove the lag inherent in
    exponential smoothing by feeding the EMA an error-corrected input
    constructed as ``price + (price - price[lag])`` where ``lag = (length - 1)
    / 2``. This pre-emphasis approximates the future direction of price and
    cancels much of the phase delay of an ordinary EMA. The result is a
    smoother that follows turning points more tightly than an EMA of the same
    length, at the cost of occasional overshoot near sharp inflections.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        ZLMA period in bars, by default 50.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.

    Returns
    -------
    OBBject[list[ZlmaData]]
        Zero-lag moving-average time series with warm-up rows dropped.
    """
    import pandas_ta as ta  # noqa: F401

    params = ZlmaQueryParams(
        data=data, target=target, index=index, length=length, offset=offset
    )
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    out = _single_overlay(
        df, "zlma", params.target, params.length, params.offset
    ).rename(columns={params.index: "date"})
    return OBBject(results=[ZlmaData(**row) for row in out.to_dict(orient="records")])


class TemaQueryParams(QueryParams):
    """Query parameters for the Triple Exponential Moving Average endpoint.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        TEMA period in bars, by default 10.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.
    """

    __category__ = "overlay"
    __output_columns__ = ("date", "tema")

    data: list[Data] = Field(description="Price series.")
    target: str = Field(default="close")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=10, description="TEMA period.")
    offset: int = Field(default=0)


class TemaData(Data):
    """One row of the Triple EMA time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    tema : float, optional
        Triple exponential moving average computed as
        ``3*EMA - 3*EMA(EMA) + EMA(EMA(EMA))``. ``None`` during warm-up.
    """

    date: datetime | dateType | str
    tema: float | None = Field(
        description="Triple EMA — ``3*EMA - 3*EMA(EMA) + EMA(EMA(EMA))``."
    )


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 3})],
)
def tema(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 10,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """Calculate Patrick Mulloy's Triple Exponential Moving Average.

    The Triple Exponential Moving Average combines three nested EMAs of the
    same length as ``3*EMA(price) - 3*EMA(EMA(price)) + EMA(EMA(EMA(price)))``.
    Each successive EMA introduces additional smoothing and additional lag;
    Mulloy's coefficient blend cancels the bulk of the lag at the expense of
    longer warm-up. The TEMA reacts more quickly than a single EMA to changes
    in trend while remaining smoother than the underlying price, and it is a
    common substitute for the EMA inside crossover and trend-following
    systems.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        TEMA period in bars, by default 10.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.

    Returns
    -------
    OBBject[list[TemaData]]
        Triple exponential moving-average time series with warm-up rows
        dropped.
    """
    import pandas_ta as ta  # noqa: F401

    params = TemaQueryParams(
        data=data, target=target, index=index, length=length, offset=offset
    )
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    out = _single_overlay(
        df, "tema", params.target, params.length, params.offset
    ).rename(columns={params.index: "date"})
    return OBBject(results=[TemaData(**row) for row in out.to_dict(orient="records")])


class DemaQueryParams(QueryParams):
    """Query parameters for the Double Exponential Moving Average endpoint.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        DEMA period in bars, by default 10.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.
    """

    __category__ = "overlay"
    __output_columns__ = ("date", "dema")

    data: list[Data] = Field(description="Price series.")
    target: str = Field(default="close")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=10, description="DEMA period.")
    offset: int = Field(default=0)


class DemaData(Data):
    """One row of the Double EMA time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    dema : float, optional
        Double exponential moving average computed as ``2*EMA - EMA(EMA)``.
        ``None`` during warm-up.
    """

    date: datetime | dateType | str
    dema: float | None = Field(description="Double EMA — ``2*EMA - EMA(EMA)``.")


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 3})],
)
def dema(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 10,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """Calculate Patrick Mulloy's Double Exponential Moving Average.

    The Double Exponential Moving Average combines two nested EMAs of the same
    length as ``2*EMA(price) - EMA(EMA(price))``. The second EMA captures the
    lag accumulated by the first; subtracting it removes most of that lag
    while leaving the smoothing intact. DEMA reacts faster than a single EMA
    of equal length and is typically used as a more responsive replacement
    for the EMA in trend-following overlays. It sits between EMA and TEMA on
    the smoothness/responsiveness tradeoff.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        DEMA period in bars, by default 10.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.

    Returns
    -------
    OBBject[list[DemaData]]
        Double exponential moving-average time series with warm-up rows
        dropped.
    """
    import pandas_ta as ta  # noqa: F401

    params = DemaQueryParams(
        data=data, target=target, index=index, length=length, offset=offset
    )
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    out = _single_overlay(
        df, "dema", params.target, params.length, params.offset
    ).rename(columns={params.index: "date"})
    return OBBject(results=[DemaData(**row) for row in out.to_dict(orient="records")])


class KamaQueryParams(QueryParams):
    """Query parameters for the Kaufman Adaptive Moving Average endpoint.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Efficiency-ratio lookback in bars, by default 10.
    fast : PositiveInt, optional
        Fastest EMA period bound used to construct the smoothing constant,
        by default 2.
    slow : PositiveInt, optional
        Slowest EMA period bound used to construct the smoothing constant,
        by default 30.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.
    """

    __category__ = "overlay"
    __output_columns__ = ("date", "kama")

    data: list[Data] = Field(description="Price series.")
    target: str = Field(default="close")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=10, description="Efficiency-ratio lookback.")
    fast: PositiveInt = Field(default=2, description="Fastest EMA period bound.")
    slow: PositiveInt = Field(default=30, description="Slowest EMA period bound.")
    offset: int = Field(default=0)


class KamaData(Data):
    """One row of the KAMA time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    kama : float, optional
        Kaufman adaptive moving average of ``target``. ``None`` during the
        warm-up rows preceding ``length``.
    """

    date: datetime | dateType | str
    kama: float | None = Field(
        description="Kaufman adaptive moving average of ``target``."
    )


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 3})],
)
def kama(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 10,
    fast: int = 2,
    slow: int = 30,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """Calculate Perry Kaufman's Adaptive Moving Average.

    The Kaufman Adaptive Moving Average modulates its smoothing constant by
    Kaufman's efficiency ratio — the absolute net price change over the
    lookback divided by the cumulative absolute bar-to-bar change. When the
    market trends, the efficiency ratio approaches one and KAMA smooths with
    the ``fast`` EMA constant so it tracks price closely; when the market
    chops, the ratio falls toward zero and KAMA smooths with the ``slow``
    constant so it filters noise. The result is an overlay that is
    responsive in trending regimes and steady in ranging regimes.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Efficiency-ratio lookback in bars, by default 10.
    fast : PositiveInt, optional
        Fastest EMA period bound used to construct the smoothing constant,
        by default 2.
    slow : PositiveInt, optional
        Slowest EMA period bound used to construct the smoothing constant,
        by default 30.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.

    Returns
    -------
    OBBject[list[KamaData]]
        Kaufman adaptive moving-average time series with warm-up rows dropped.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = KamaQueryParams(
        data=data,
        target=target,
        index=index,
        length=length,
        fast=fast,
        slow=slow,
        offset=offset,
    )
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    series = df[[params.target]].ta.kama(
        length=params.length,
        fast=params.fast,
        slow=params.slow,
        offset=params.offset,
        close=params.target,
    )
    out = (
        pd.DataFrame({"kama": series})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[KamaData(**row) for row in out.to_dict(orient="records")])


class FramaQueryParams(QueryParams):
    """Query parameters for the Fractal Adaptive Moving Average endpoint.

    Parameters
    ----------
    data : list[Data]
        Price series with ``high`` and ``low`` columns.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    window : PositiveInt, optional
        Window length in bars. Must be even because the estimator splits the
        window in halves to estimate the fractal dimension. By default 10.
    """

    __category__ = "overlay"
    __output_columns__ = ("date", "frama")

    data: list[Data] = Field(
        description="Price series with ``high`` and ``low`` columns."
    )
    index: str = Field(default="date")
    window: PositiveInt = Field(default=10, description="Window length — must be even.")

    @field_validator("window")
    @classmethod
    def window_must_be_even(cls, v: int) -> int:
        """Ehlers FRAMA requires an even window."""
        if v % 2:
            raise ValueError("frama requires an even window.")
        return v


class FramaData(Data):
    """One row of the FRAMA time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    frama : float, optional
        Fractal adaptive moving average per Ehlers (2005). ``None`` during
        the warm-up rows preceding ``window``.
    """

    date: datetime | dateType | str
    frama: float | None = Field(
        description="Fractal adaptive moving average — Ehlers (2005)."
    )


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "window": 4})],
)
def frama(
    data: list[Data],
    index: str = "date",
    window: int = 10,
) -> OBBject[list[Data]]:
    """Calculate John Ehlers' Fractal Adaptive Moving Average.

    The Fractal Adaptive Moving Average derives an adaptive smoothing constant
    from an estimate of the price fractal dimension over the lookback window.
    The window is split into halves; the high-low ranges of the two halves
    and of the full window are compared on a log scale to produce a fractal
    dimension ``d`` between one (perfectly trending) and two (perfectly
    space-filling). The smoothing constant is then ``alpha = exp(-4.6 * (d -
    1))``, clipped to ``[0.01, 1]``. FRAMA tightens against price when the
    market trends and relaxes into a heavy smoother when the market chops.

    Parameters
    ----------
    data : list[Data]
        Price series with ``high`` and ``low`` columns.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    window : PositiveInt, optional
        Window length in bars; must be even, by default 10.

    Returns
    -------
    OBBject[list[FramaData]]
        Fractal adaptive moving-average time series with warm-up rows dropped.
    """
    import numpy as np
    import pandas as pd

    params = FramaQueryParams(data=data, index=index, window=window)
    validate_data(params.data, [params.window])
    df = basemodel_to_df(params.data, index=params.index)
    n = params.window
    half = n // 2
    high = df["high"]
    low = df["low"]
    close = df["close"]
    h_full = high.rolling(n).max()
    l_full = low.rolling(n).min()
    n3 = (h_full - l_full) / n
    h_first = high.rolling(half).max().shift(half)
    l_first = low.rolling(half).min().shift(half)
    n1 = (h_first - l_first) / half
    h_second = high.rolling(half).max()
    l_second = low.rolling(half).min()
    n2 = (h_second - l_second) / half
    with np.errstate(divide="ignore", invalid="ignore"):
        d = (np.log(n1 + n2) - np.log(n3)) / np.log(2)
    alpha = np.exp(-4.6 * (d - 1)).clip(lower=0.01, upper=1.0)
    alpha = alpha.fillna(1.0)
    out_vals: list[float | None] = []
    prev: float | None = None
    close_vals = close.tolist()
    alpha_vals = alpha.tolist()
    for i, c in enumerate(close_vals):
        if i < n - 1:
            out_vals.append(None)
            continue
        if prev is None:
            prev = c
        a = alpha_vals[i]
        prev = a * c + (1 - a) * prev
        out_vals.append(float(prev))
    out = (
        pd.DataFrame({"frama": out_vals}, index=df.index)
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[FramaData(**row) for row in out.to_dict(orient="records")])


class VwmaQueryParams(QueryParams):
    """Query parameters for the Volume Weighted Moving Average endpoint.

    Parameters
    ----------
    data : list[Data]
        Price series with ``close`` and ``volume`` columns.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        VWMA period in bars, by default 10.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.
    """

    __category__ = "overlay"
    __output_columns__ = ("date", "vwma")

    data: list[Data] = Field(description="Price series with ``close`` and ``volume``.")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=10, description="VWMA period.")
    offset: int = Field(default=0)


class VwmaData(Data):
    """One row of the VWMA time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    vwma : float, optional
        Volume-weighted moving average of close over the trailing ``length``
        bars. ``None`` during warm-up.
    """

    date: datetime | dateType | str
    vwma: float | None = Field(description="Volume weighted moving average of close.")


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 3})],
)
def vwma(
    data: list[Data],
    index: str = "date",
    length: int = 10,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """Calculate the Volume Weighted Moving Average.

    The Volume Weighted Moving Average is the sum of ``close * volume`` over
    the trailing window divided by the sum of ``volume`` over the same window.
    Bars on heavy volume therefore exert more influence on the smoothed value
    than bars on light volume. Compared with the SMA, the VWMA tilts toward
    prices that the market actually transacted at, which can produce earlier
    crossover signals during accumulation or distribution and dampens the
    influence of low-conviction price moves on thin trading.

    Parameters
    ----------
    data : list[Data]
        Price series with ``close`` and ``volume`` columns.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        VWMA period in bars, by default 10.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.

    Returns
    -------
    OBBject[list[VwmaData]]
        Volume-weighted moving-average time series with warm-up rows dropped.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = VwmaQueryParams(data=data, index=index, length=length, offset=offset)
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    series = df.ta.vwma(length=params.length, offset=params.offset)
    out = (
        pd.DataFrame({"vwma": series})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[VwmaData(**row) for row in out.to_dict(orient="records")])


class BbandsQueryParams(QueryParams):
    """Query parameters for the Bollinger Bands endpoint.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth and band, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Moving-average period in bars, by default 20.
    std : PositiveFloat, optional
        Standard-deviation multiplier for the bands, by default 2.0.
    mamode : {"sma", "ema", "wma", "rma"}, optional
        Type of moving average for the middle band, by default ``"sma"``.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.
    """

    __category__ = "overlay"
    __output_columns__ = ("date", "lower", "middle", "upper", "bandwidth", "percent")

    data: list[Data] = Field(description="Price series.")
    target: str = Field(default="close")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=20, description="Moving-average period.")
    std: PositiveFloat = Field(
        default=2.0, description="Standard-deviation multiplier."
    )
    mamode: Literal["sma", "ema", "wma", "rma"] = Field(
        default="sma", description="Type of moving average for the middle band."
    )
    offset: int = Field(default=0)


class BbandsData(Data):
    """One row of the Bollinger Bands time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    lower : float, optional
        Lower band — middle minus ``std`` rolling standard deviations.
    middle : float, optional
        Centre moving average of ``target``.
    upper : float, optional
        Upper band — middle plus ``std`` rolling standard deviations.
    bandwidth : float, optional
        ``(upper - lower) / middle`` — the band width relative to the centre.
    percent : float, optional
        ``(price - lower) / (upper - lower)`` — the position of price within
        the band, conventionally called %B.
    """

    date: datetime | dateType | str
    lower: float | None = Field(
        description="Lower band — middle minus ``std`` deviations."
    )
    middle: float | None = Field(description="Center moving average.")
    upper: float | None = Field(
        description="Upper band — middle plus ``std`` deviations."
    )
    bandwidth: float | None = Field(
        description="``(upper - lower) / middle`` — width relative to the centre."
    )
    percent: float | None = Field(
        description="``(price - lower) / (upper - lower)`` — position within the band."
    )


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 2})],
)
def bbands(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    length: int = 20,
    std: float = 2.0,
    mamode: Literal["sma", "ema", "wma", "rma"] = "sma",
    offset: int = 0,
) -> OBBject[list[Data]]:
    """Calculate Bollinger Bands around a moving-average centreline.

    Bollinger Bands plot a moving average together with two envelope lines
    spaced ``std`` rolling standard deviations above and below it. The
    distance between the bands therefore expands when realised volatility
    rises and contracts when it falls — narrow bands (the "squeeze") often
    precede expansion in price range, while excursions outside the bands
    signal that recent price is unusually far from the moving average. The
    derived ``bandwidth`` and ``percent`` (%B) outputs summarise volatility
    regime and position within the band in scale-free form.

    Parameters
    ----------
    data : list[Data]
        Price series.
    target : str, optional
        Column to smooth and band, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Moving-average period in bars, by default 20.
    std : PositiveFloat, optional
        Standard-deviation multiplier for the bands, by default 2.0.
    mamode : {"sma", "ema", "wma", "rma"}, optional
        Type of moving average for the middle band, by default ``"sma"``.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.

    Returns
    -------
    OBBject[list[BbandsData]]
        Lower, middle, upper, bandwidth, and %B time series with warm-up rows
        dropped.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = BbandsQueryParams(
        data=data,
        target=target,
        index=index,
        length=length,
        std=std,
        mamode=mamode,
        offset=offset,
    )
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    raw = df[[params.target]].ta.bbands(
        length=params.length,
        std=params.std,
        mamode=params.mamode,
        offset=params.offset,
        close=params.target,
    )
    raw.columns = ["lower", "middle", "upper", "bandwidth", "percent"]
    out = (
        pd.DataFrame(raw).dropna().reset_index().rename(columns={params.index: "date"})
    )
    return OBBject(results=[BbandsData(**row) for row in out.to_dict(orient="records")])


class DonchianQueryParams(QueryParams):
    """Query parameters for the Donchian Channel endpoint.

    Parameters
    ----------
    data : list[Data]
        Price series with ``high`` and ``low`` columns.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    lower_length : PositiveInt, optional
        Lookback for the lower band in bars, by default 20.
    upper_length : PositiveInt, optional
        Lookback for the upper band in bars, by default 20.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.
    """

    __category__ = "overlay"
    __output_columns__ = ("date", "lower", "middle", "upper")

    data: list[Data] = Field(description="Price series with high/low columns.")
    index: str = Field(default="date")
    lower_length: PositiveInt = Field(
        default=20, description="Lookback for the lower band."
    )
    upper_length: PositiveInt = Field(
        default=20, description="Lookback for the upper band."
    )
    offset: int = Field(default=0)


class DonchianData(Data):
    """One row of the Donchian Channel time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    lower : float, optional
        Trailing minimum low over ``lower_length`` bars.
    middle : float, optional
        Midpoint between the upper and lower bands.
    upper : float, optional
        Trailing maximum high over ``upper_length`` bars.
    """

    date: datetime | dateType | str
    lower: float | None = Field(description="Trailing min over ``lower_length`` bars.")
    middle: float | None = Field(description="Midpoint between upper and lower bands.")
    upper: float | None = Field(description="Trailing max over ``upper_length`` bars.")


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "data": APIEx.mock_data("timeseries"),
                "lower_length": 1,
                "upper_length": 3,
            }
        )
    ],
)
def donchian(
    data: list[Data],
    index: str = "date",
    lower_length: int = 20,
    upper_length: int = 20,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """Calculate the Donchian Channel — trailing high/low price envelope.

    The Donchian Channel plots the rolling maximum high over ``upper_length``
    bars as the upper band, the rolling minimum low over ``lower_length`` bars
    as the lower band, and their midpoint as the centreline. The envelope
    therefore traces the extreme price excursions of the lookback window
    rather than statistical bands around an average. Donchian Channels are
    the original Richard Donchian and later "Turtle" breakout system —
    breaches above the upper band are entered as long, breaches below the
    lower band as short — and remain a clean visualisation of regime range.

    Parameters
    ----------
    data : list[Data]
        Price series with ``high`` and ``low`` columns.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    lower_length : PositiveInt, optional
        Lookback for the lower band in bars, by default 20.
    upper_length : PositiveInt, optional
        Lookback for the upper band in bars, by default 20.
    offset : int, optional
        Output offset; positive values shift the series forward, by default 0.

    Returns
    -------
    OBBject[list[DonchianData]]
        Lower, middle, and upper band time series with warm-up rows dropped.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = DonchianQueryParams(
        data=data,
        index=index,
        lower_length=lower_length,
        upper_length=upper_length,
        offset=offset,
    )
    validate_data(params.data, [params.lower_length, params.upper_length])
    df = basemodel_to_df(params.data, index=params.index)
    raw = df.ta.donchian(
        lower_length=params.lower_length,
        upper_length=params.upper_length,
        offset=params.offset,
    )
    raw.columns = ["lower", "middle", "upper"]
    out = (
        pd.DataFrame(raw).dropna().reset_index().rename(columns={params.index: "date"})
    )
    return OBBject(
        results=[DonchianData(**row) for row in out.to_dict(orient="records")]
    )


class KcQueryParams(QueryParams):
    """Query parameters for the Keltner Channel endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Centreline moving-average period in bars, by default 20.
    scalar : PositiveFloat, optional
        ATR multiplier applied to set the band width, by default 2.0.
    mamode : {"ema", "sma"}, optional
        Centreline moving-average type, by default ``"ema"``.
    offset : NonNegativeInt, optional
        Output offset in bars, by default 0.
    """

    __category__ = "overlay"
    __output_columns__ = ("date", "lower", "middle", "upper")

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=20, description="Centerline MA period.")
    scalar: PositiveFloat = Field(
        default=2.0, description="ATR multiplier for the bands."
    )
    mamode: Literal["ema", "sma"] = Field(
        default="ema", description="Centreline moving-average type."
    )
    offset: NonNegativeInt = Field(default=0)


class KcData(Data):
    """One row of the Keltner Channel time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    lower : float, optional
        Centreline minus ``scalar * ATR``.
    middle : float, optional
        Centreline moving average.
    upper : float, optional
        Centreline plus ``scalar * ATR``.
    """

    date: datetime | dateType | str
    lower: float | None = Field(description="Centerline minus ``scalar * ATR``.")
    middle: float | None = Field(description="Centreline moving average.")
    upper: float | None = Field(description="Centerline plus ``scalar * ATR``.")


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 2})],
)
def kc(
    data: list[Data],
    index: str = "date",
    length: int = 20,
    scalar: float = 2.0,
    mamode: Literal["ema", "sma"] = "ema",
    offset: int = 0,
) -> OBBject[list[Data]]:
    """Calculate the Keltner Channel — an ATR-scaled volatility envelope.

    The Keltner Channel plots a moving-average centreline together with two
    bands set at ``scalar * ATR(length)`` above and below the centre. Because
    the band width scales with the Average True Range rather than the
    rolling standard deviation of price, the Keltner Channel responds to
    gap-inclusive volatility and tends to remain smoother than Bollinger
    Bands during volatile periods. Traders use the channel to identify
    breakouts when price closes outside the band and to gauge directional
    strength relative to the centreline.

    Parameters
    ----------
    data : list[Data]
        OHLC price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        Centreline moving-average period in bars, by default 20.
    scalar : PositiveFloat, optional
        ATR multiplier applied to set the band width, by default 2.0.
    mamode : {"ema", "sma"}, optional
        Centreline moving-average type, by default ``"ema"``.
    offset : NonNegativeInt, optional
        Output offset in bars, by default 0.

    Returns
    -------
    OBBject[list[KcData]]
        Lower, middle, and upper band time series with warm-up rows dropped.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = KcQueryParams(
        data=data,
        index=index,
        length=length,
        scalar=scalar,
        mamode=mamode,
        offset=offset,
    )
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    raw = df.ta.kc(
        length=params.length,
        scalar=params.scalar,
        mamode=params.mamode,
        offset=params.offset,
    )
    raw.columns = ["lower", "middle", "upper"]
    out = (
        pd.DataFrame(raw).dropna().reset_index().rename(columns={params.index: "date"})
    )
    return OBBject(results=[KcData(**row) for row in out.to_dict(orient="records")])


class IchimokuQueryParams(QueryParams):
    """Query parameters for the Ichimoku Cloud endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    conversion : PositiveInt, optional
        Tenkan-sen (conversion-line) lookback in bars, by default 9.
    base : PositiveInt, optional
        Kijun-sen (base-line) lookback in bars, by default 26.
    lagging : PositiveInt, optional
        Senkou Span B lookback in bars, by default 52.
    offset : PositiveInt, optional
        Forward projection of the cloud in bars, by default 26.
    lookahead : bool, optional
        When ``True``, emit the Chikou Span (look-ahead). Disabled by default
        to prevent data leakage in backtests.
    """

    __category__ = "overlay"
    __output_columns__ = (
        "date",
        "tenkan_sen",
        "kijun_sen",
        "senkou_a",
        "senkou_b",
        "chikou_span",
    )

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(default="date")
    conversion: PositiveInt = Field(default=9, description="Tenkan-sen lookback.")
    base: PositiveInt = Field(default=26, description="Kijun-sen lookback.")
    lagging: PositiveInt = Field(default=52, description="Senkou Span B lookback.")
    offset: PositiveInt = Field(
        default=26, description="Forward projection for the cloud."
    )
    lookahead: bool = Field(
        default=False,
        description="If ``True``, emit the Chikou Span (look-ahead). Off by default to prevent data leakage.",
    )


class IchimokuData(Data):
    """One row of the Ichimoku Cloud time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    tenkan_sen : float, optional
        Conversion line — midpoint of the trailing ``conversion``-bar
        high/low.
    kijun_sen : float, optional
        Base line — midpoint of the trailing ``base``-bar high/low.
    senkou_a : float, optional
        Leading Span A — midpoint of ``tenkan_sen`` and ``kijun_sen`` projected
        ``offset`` bars forward.
    senkou_b : float, optional
        Leading Span B — midpoint of the trailing ``lagging``-bar high/low
        projected ``offset`` bars forward.
    chikou_span : float, optional
        Lagging Span — close projected ``offset`` bars backward. Always
        ``None`` when ``lookahead=False``.
    """

    date: datetime | dateType | str
    tenkan_sen: float | None = Field(description="Conversion line.")
    kijun_sen: float | None = Field(description="Base line.")
    senkou_a: float | None = Field(description="Leading span A.")
    senkou_b: float | None = Field(description="Leading span B.")
    chikou_span: float | None = Field(
        default=None,
        description="Lagging span. Always ``None`` when ``lookahead=False``.",
    )


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries")})],
)
def ichimoku(
    data: list[Data],
    index: str = "date",
    conversion: int = 9,
    base: int = 26,
    lagging: int = 52,
    offset: int = 26,
    lookahead: bool = False,
) -> OBBject[list[Data]]:
    """Calculate the Ichimoku Kinko Hyo cloud — a five-component trend overlay.

    Ichimoku Kinko Hyo, "one-glance equilibrium chart", composes five lines
    that together summarise trend, momentum, and support/resistance. The
    Tenkan-sen and Kijun-sen are the midpoints of recent short and medium
    high/low ranges and act as fast and slow trend lines. Senkou Span A
    (midpoint of Tenkan and Kijun) and Senkou Span B (midpoint of the long
    high/low range) are projected forward by ``offset`` bars to form the
    Kumo (cloud), whose colour and thickness signal trend direction and
    strength. The Chikou Span is the close shifted backward and is emitted
    only when ``lookahead=True`` because it introduces look-ahead bias.

    Parameters
    ----------
    data : list[Data]
        OHLC price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    conversion : PositiveInt, optional
        Tenkan-sen lookback in bars, by default 9.
    base : PositiveInt, optional
        Kijun-sen lookback in bars, by default 26.
    lagging : PositiveInt, optional
        Senkou Span B lookback in bars, by default 52.
    offset : PositiveInt, optional
        Forward projection of the cloud in bars, by default 26.
    lookahead : bool, optional
        When ``True``, emit the Chikou Span; off by default to prevent data
        leakage.

    Returns
    -------
    OBBject[list[IchimokuData]]
        Tenkan-sen, Kijun-sen, Senkou Span A, Senkou Span B, and optional
        Chikou Span time series with all-NaN rows dropped.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = IchimokuQueryParams(
        data=data,
        index=index,
        conversion=conversion,
        base=base,
        lagging=lagging,
        offset=offset,
        lookahead=lookahead,
    )
    validate_data(params.data, [params.conversion, params.base, params.lagging])
    df = basemodel_to_df(params.data, index=params.index)
    if params.index == "date":
        df.index = pd.to_datetime(df.index)
    history, _ = df.ta.ichimoku(
        tenkan=params.conversion,
        kijun=params.base,
        senkou=params.lagging,
        offset=params.offset,
        lookahead=params.lookahead,
    )
    rename = {
        f"ISA_{params.conversion}": "senkou_a",
        f"ISB_{params.base}": "senkou_b",
        f"ITS_{params.conversion}": "tenkan_sen",
        f"IKS_{params.base}": "kijun_sen",
        f"ICS_{params.base}": "chikou_span",
    }
    history = history.rename(columns=rename)
    if "chikou_span" not in history.columns:
        history["chikou_span"] = None
    out = (
        history[["tenkan_sen", "kijun_sen", "senkou_a", "senkou_b", "chikou_span"]]
        .dropna(how="all")
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(
        results=[
            IchimokuData(**_nan_to_none(row)) for row in out.to_dict(orient="records")
        ]
    )


class SupertrendQueryParams(QueryParams):
    """Query parameters for the Supertrend endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        ATR lookback in bars, by default 7.
    multiplier : PositiveFloat, optional
        ATR multiplier used to position the bands above and below the median
        price, by default 3.0.
    """

    __category__ = "overlay"
    __output_columns__ = ("date", "supertrend", "direction", "long_band", "short_band")

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=7, description="ATR lookback.")
    multiplier: PositiveFloat = Field(
        default=3.0, description="ATR multiplier for the bands."
    )


class SupertrendData(Data):
    """One row of the Supertrend time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    supertrend : float, optional
        Current trailing-stop value — the active band in the prevailing
        direction.
    direction : {-1, 1}, optional
        Trend direction. ``1`` when the trend is up, ``-1`` when down.
        ``None`` during warm-up.
    long_band : float, optional
        Long-side band; populated only when the trend is up.
    short_band : float, optional
        Short-side band; populated only when the trend is down.
    """

    date: datetime | dateType | str
    supertrend: float | None = Field(description="Current trailing-stop value.")
    direction: Literal[-1, 1] | None = Field(
        default=None,
        description="``1`` when the trend is up, ``-1`` when down. ``None`` during warm-up.",
    )
    long_band: float | None = Field(
        description="Long-side band — populated only when the trend is up."
    )
    short_band: float | None = Field(
        description="Short-side band — populated only when the trend is down."
    )


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 2})],
)
def supertrend(
    data: list[Data],
    index: str = "date",
    length: int = 7,
    multiplier: float = 3.0,
) -> OBBject[list[Data]]:
    """Calculate the Supertrend ATR-banded trailing-stop overlay.

    Supertrend constructs upper and lower bands at ``median price +/-
    multiplier * ATR(length)`` and emits a single trailing-stop line that
    flips between them according to whether close trades above or below the
    most-recent active band. While the trend is up, ``long_band`` (the lower
    band) is the trailing stop; on a close below it, direction flips to down,
    ``short_band`` (the upper band) becomes the trailing stop, and the
    ``supertrend`` line snaps above price. The flips give a discrete trend
    state that traders use for systematic stop-management and regime
    classification.

    Parameters
    ----------
    data : list[Data]
        OHLC price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        ATR lookback in bars, by default 7.
    multiplier : PositiveFloat, optional
        ATR multiplier used to position the bands, by default 3.0.

    Returns
    -------
    OBBject[list[SupertrendData]]
        Supertrend line, direction, and active long/short band time series
        with warm-up rows dropped.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = SupertrendQueryParams(
        data=data, index=index, length=length, multiplier=multiplier
    )
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    raw = df.ta.supertrend(length=params.length, multiplier=params.multiplier)
    raw.columns = ["supertrend", "direction", "long_band", "short_band"]
    out = pd.DataFrame(raw).reset_index().rename(columns={params.index: "date"})
    records = []
    for row in out.to_dict(orient="records"):
        st = row["supertrend"]
        if st is None or (isinstance(st, float) and pd.isna(st)):
            continue
        direction_val = row["direction"]
        if direction_val is None or (
            isinstance(direction_val, float) and pd.isna(direction_val)
        ):
            row["direction"] = None
        else:
            row["direction"] = int(direction_val)
        for key in ("long_band", "short_band"):
            v = row[key]
            if isinstance(v, float) and pd.isna(v):
                row[key] = None
        records.append(SupertrendData(**row))
    return OBBject(results=records)


__all__ = [
    "BbandsData",
    "BbandsQueryParams",
    "DemaData",
    "DemaQueryParams",
    "DonchianData",
    "DonchianQueryParams",
    "EmaData",
    "EmaQueryParams",
    "FramaData",
    "FramaQueryParams",
    "HmaData",
    "HmaQueryParams",
    "IchimokuData",
    "IchimokuQueryParams",
    "KamaData",
    "KamaQueryParams",
    "KcData",
    "KcQueryParams",
    "SmaData",
    "SmaQueryParams",
    "SupertrendData",
    "SupertrendQueryParams",
    "TemaData",
    "TemaQueryParams",
    "VwmaData",
    "VwmaQueryParams",
    "WmaData",
    "WmaQueryParams",
    "ZlmaData",
    "ZlmaQueryParams",
    "bbands",
    "dema",
    "donchian",
    "ema",
    "frama",
    "hma",
    "ichimoku",
    "kama",
    "kc",
    "router",
    "sma",
    "supertrend",
    "tema",
    "vwma",
    "wma",
    "zlma",
]
