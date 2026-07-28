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
) -> "pd.DataFrame":
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
def sma(params: SmaQueryParams) -> OBBject[list[SmaData]]:
    """Calculate the Simple Moving Average over the trailing window."""
    import pandas_ta as ta  # noqa: F401

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
    target: str = Field(
        default="close", description='Column to smooth, by default ``"close"``.'
    )
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    length: PositiveInt = Field(default=50, description="EMA period.")
    offset: int = Field(
        default=0,
        description="Output offset; positive values shift the series forward, by default 0.",
    )


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

    date: datetime | dateType | str = Field(description="Observation date.")
    ema: float | None = Field(description="Exponential moving average of ``target``.")


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 2})],
)
def ema(params: EmaQueryParams) -> OBBject[list[EmaData]]:
    """Calculate the Exponential Moving Average with recency-weighted smoothing."""
    import pandas_ta as ta  # noqa: F401

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
    target: str = Field(
        default="close", description='Column to smooth, by default ``"close"``.'
    )
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    length: PositiveInt = Field(default=50, description="HMA period.")
    offset: int = Field(
        default=0,
        description="Output offset; positive values shift the series forward, by default 0.",
    )


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

    date: datetime | dateType | str = Field(description="Observation date.")
    hma: float | None = Field(
        description="Hull moving average — lag-reduced WMA blend."
    )


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 4})],
)
def hma(params: HmaQueryParams) -> OBBject[list[HmaData]]:
    """Calculate Alan Hull's lag-reduced moving average."""
    import pandas_ta as ta  # noqa: F401

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
    target: str = Field(
        default="close", description='Column to smooth, by default ``"close"``.'
    )
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    length: PositiveInt = Field(default=50, description="WMA period.")
    offset: int = Field(
        default=0,
        description="Output offset; positive values shift the series forward, by default 0.",
    )


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

    date: datetime | dateType | str = Field(description="Observation date.")
    wma: float | None = Field(
        description="Linearly-weighted moving average of ``target``."
    )


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 2})],
)
def wma(params: WmaQueryParams) -> OBBject[list[WmaData]]:
    """Calculate the linearly-Weighted Moving Average."""
    import pandas_ta as ta  # noqa: F401

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
    target: str = Field(
        default="close", description='Column to smooth, by default ``"close"``.'
    )
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    length: PositiveInt = Field(default=50, description="ZLMA period.")
    offset: int = Field(
        default=0,
        description="Output offset; positive values shift the series forward, by default 0.",
    )


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

    date: datetime | dateType | str = Field(description="Observation date.")
    zlma: float | None = Field(
        description="Zero-Lag EMA of ``target`` — Ehlers/Way de-lagged EMA."
    )


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 2})],
)
def zlma(params: ZlmaQueryParams) -> OBBject[list[ZlmaData]]:
    """Calculate the Zero-Lag Exponential Moving Average of Ehlers and Way."""
    import pandas_ta as ta  # noqa: F401

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
    target: str = Field(
        default="close", description='Column to smooth, by default ``"close"``.'
    )
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    length: PositiveInt = Field(default=10, description="TEMA period.")
    offset: int = Field(
        default=0,
        description="Output offset; positive values shift the series forward, by default 0.",
    )


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

    date: datetime | dateType | str = Field(description="Observation date.")
    tema: float | None = Field(
        description="Triple EMA — ``3*EMA - 3*EMA(EMA) + EMA(EMA(EMA))``."
    )


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 3})],
)
def tema(params: TemaQueryParams) -> OBBject[list[TemaData]]:
    """Calculate Patrick Mulloy's Triple Exponential Moving Average."""
    import pandas_ta as ta  # noqa: F401

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
    target: str = Field(
        default="close", description='Column to smooth, by default ``"close"``.'
    )
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    length: PositiveInt = Field(default=10, description="DEMA period.")
    offset: int = Field(
        default=0,
        description="Output offset; positive values shift the series forward, by default 0.",
    )


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

    date: datetime | dateType | str = Field(description="Observation date.")
    dema: float | None = Field(description="Double EMA — ``2*EMA - EMA(EMA)``.")


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 3})],
)
def dema(params: DemaQueryParams) -> OBBject[list[DemaData]]:
    """Calculate Patrick Mulloy's Double Exponential Moving Average."""
    import pandas_ta as ta  # noqa: F401

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
    target: str = Field(
        default="close", description='Column to smooth, by default ``"close"``.'
    )
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    length: PositiveInt = Field(default=10, description="Efficiency-ratio lookback.")
    fast: PositiveInt = Field(default=2, description="Fastest EMA period bound.")
    slow: PositiveInt = Field(default=30, description="Slowest EMA period bound.")
    offset: int = Field(
        default=0,
        description="Output offset; positive values shift the series forward, by default 0.",
    )


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

    date: datetime | dateType | str = Field(description="Observation date.")
    kama: float | None = Field(
        description="Kaufman adaptive moving average of ``target``."
    )


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 3})],
)
def kama(params: KamaQueryParams) -> OBBject[list[KamaData]]:
    """Calculate Perry Kaufman's Adaptive Moving Average."""
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

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
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
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

    date: datetime | dateType | str = Field(description="Observation date.")
    frama: float | None = Field(
        description="Fractal adaptive moving average — Ehlers (2005)."
    )


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "window": 4})],
)
def frama(params: FramaQueryParams) -> OBBject[list[FramaData]]:
    """Calculate John Ehlers' Fractal Adaptive Moving Average."""
    import numpy as np
    import pandas as pd

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
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    length: PositiveInt = Field(default=10, description="VWMA period.")
    offset: int = Field(
        default=0,
        description="Output offset; positive values shift the series forward, by default 0.",
    )


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

    date: datetime | dateType | str = Field(description="Observation date.")
    vwma: float | None = Field(description="Volume weighted moving average of close.")


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 3})],
)
def vwma(params: VwmaQueryParams) -> OBBject[list[VwmaData]]:
    """Calculate the Volume Weighted Moving Average."""
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

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
    target: str = Field(
        default="close",
        description='Column to smooth and band, by default ``"close"``.',
    )
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    length: PositiveInt = Field(default=20, description="Moving-average period.")
    std: PositiveFloat = Field(
        default=2.0, description="Standard-deviation multiplier."
    )
    mamode: Literal["sma", "ema", "wma", "rma"] = Field(
        default="sma", description="Type of moving average for the middle band."
    )
    offset: int = Field(
        default=0,
        description="Output offset; positive values shift the series forward, by default 0.",
    )


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

    date: datetime | dateType | str = Field(description="Observation date.")
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
def bbands(params: BbandsQueryParams) -> OBBject[list[BbandsData]]:
    """Calculate Bollinger Bands around a moving-average centreline."""
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

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
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    lower_length: PositiveInt = Field(
        default=20, description="Lookback for the lower band."
    )
    upper_length: PositiveInt = Field(
        default=20, description="Lookback for the upper band."
    )
    offset: int = Field(
        default=0,
        description="Output offset; positive values shift the series forward, by default 0.",
    )


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

    date: datetime | dateType | str = Field(description="Observation date.")
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
def donchian(params: DonchianQueryParams) -> OBBject[list[DonchianData]]:
    """Calculate the Donchian Channel — trailing high/low price envelope."""
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

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
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    length: PositiveInt = Field(default=20, description="Centerline MA period.")
    scalar: PositiveFloat = Field(
        default=2.0, description="ATR multiplier for the bands."
    )
    mamode: Literal["ema", "sma"] = Field(
        default="ema", description="Centreline moving-average type."
    )
    offset: NonNegativeInt = Field(
        default=0, description="Output offset in bars, by default 0."
    )


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

    date: datetime | dateType | str = Field(description="Observation date.")
    lower: float | None = Field(description="Centerline minus ``scalar * ATR``.")
    middle: float | None = Field(description="Centreline moving average.")
    upper: float | None = Field(description="Centerline plus ``scalar * ATR``.")


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 2})],
)
def kc(params: KcQueryParams) -> OBBject[list[KcData]]:
    """Calculate the Keltner Channel — an ATR-scaled volatility envelope."""
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

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
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
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

    date: datetime | dateType | str = Field(description="Observation date.")
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
def ichimoku(params: IchimokuQueryParams) -> OBBject[list[IchimokuData]]:
    """Calculate the Ichimoku Kinko Hyo cloud — a five-component trend overlay."""
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

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
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
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

    date: datetime | dateType | str = Field(description="Observation date.")
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
def supertrend(params: SupertrendQueryParams) -> OBBject[list[SupertrendData]]:
    """Calculate the Supertrend ATR-banded trailing-stop overlay."""
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

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
