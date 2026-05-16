"""Volatility-family technical indicators."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Literal

from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.utils import basemodel_to_df
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, PositiveInt, field_validator

from openbb_technical.helpers import (
    calculate_cones,
    garman_klass,
    hodges_tompkins,
    parkinson,
    rogers_satchell,
    standard_deviation,
    validate_data,
    yang_zhang,
)

# Bare 'date' alias for function signatures so the static-package builder
# writes 'date' (which it imports from datetime) rather than 'dateType' which it does not.
date = dateType

router = Router(prefix="", description="Volatility indicators.")


RealizedVolatilityModel = Literal[
    "std",
    "parkinson",
    "garman_klass",
    "hodges_tompkins",
    "rogers_satchell",
    "yang_zhang",
]


_VOL_FUNCTIONS = {
    "std": standard_deviation,
    "parkinson": parkinson,
    "garman_klass": garman_klass,
    "hodges_tompkins": hodges_tompkins,
    "rogers_satchell": rogers_satchell,
    "yang_zhang": yang_zhang,
}


class RealizedVolatilityQueryParams(QueryParams):
    """Query parameters for the realized-volatility endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC(V) price series. ``parkinson``, ``garman_klass``, ``rogers_satchell``,
        and ``yang_zhang`` require ``high`` and ``low`` columns; ``garman_klass``
        and ``yang_zhang`` additionally require ``open``.
    model : RealizedVolatilityModel, optional
        Volatility estimator, by default ``yang_zhang``. ``yang_zhang`` has the
        lowest variance among the six and accommodates overnight drift;
        ``parkinson`` and ``rogers_satchell`` are range-based and drift-invariant;
        ``hodges_tompkins`` is a bias-corrected close-to-close estimator.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    window : PositiveInt, optional
        Rolling window length in bars, by default 30.
    trading_periods : PositiveInt, optional
        Annualisation factor. When unset, resolves to 365 if ``is_crypto`` is
        ``True``, otherwise 252.
    is_crypto : bool, optional
        When ``True`` and ``trading_periods`` is unset, annualise over 365
        instead of 252, by default ``False``.
    clean : bool, optional
        Drop the leading warm-up rows where the rolling window has not yet
        filled, by default ``True``.
    """

    __category__ = "volatility"
    __output_columns__ = ("date", "volatility", "model", "window", "trading_periods")

    data: list[Data] = Field(description="Input OHLC(V) price series.")
    model: RealizedVolatilityModel = Field(
        default="yang_zhang",
        description=(
            "Volatility estimator. ``yang_zhang`` is the lowest-error blend; "
            "``parkinson`` and ``rogers_satchell`` are range-based and "
            "drift-invariant; ``hodges_tompkins`` is bias-corrected close-to-close."
        ),
    )
    index: str = Field(default="date", description="Index column name in ``data``.")
    window: PositiveInt = Field(
        default=30, description="Rolling window length in bars."
    )
    trading_periods: PositiveInt | None = Field(
        default=None,
        description=(
            "Annualisation factor. ``None`` resolves to 365 when ``is_crypto`` "
            "is true, otherwise 252."
        ),
    )
    is_crypto: bool = Field(
        default=False,
        description=(
            "When true and ``trading_periods`` is unset, annualise over 365 "
            "instead of 252."
        ),
    )
    clean: bool = Field(
        default=True,
        description="Drop the leading warm-up rows where the rolling window is incomplete.",
    )

    @field_validator("window")
    @classmethod
    def window_minimum_for_model(cls, v: int, info) -> int:
        """Enforce ``window >= 2`` for ``hodges_tompkins`` and ``yang_zhang``."""
        model = info.data.get("model", "std")
        if model in {"hodges_tompkins", "yang_zhang"} and v < 2:
            raise ValueError(f"{model} requires window >= 2.")
        return v


class RealizedVolatilityData(Data):
    """One row of the realized-volatility time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    volatility : float, optional
        Annualised realised volatility per the chosen ``model`` over the trailing
        ``window`` bars. ``None`` during warm-up when ``clean=False``.
    model : RealizedVolatilityModel
        Estimator used to produce this row.
    window : int
        Rolling window length used to produce this row.
    trading_periods : int
        Annualisation factor used to produce this row.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    volatility: float | None = Field(
        description=(
            "Annualised realised volatility per the chosen ``model`` over "
            "the trailing ``window`` bars. ``None`` during warm-up when "
            "``clean=False``."
        ),
    )
    model: RealizedVolatilityModel = Field(
        description="Echoed on every row so the response is self-describing.",
    )
    window: int = Field(description="Window used to produce this row.")
    trading_periods: int = Field(
        description="Annualisation factor used to produce this row."
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Yang-Zhang realised volatility on daily SPY.",
            code=[
                "data = obb.equity.price.historical(symbol='SPY', start_date='2022-01-01', provider='yfinance').results",
                "rv = obb.technical.realized_volatility(data=data, model='yang_zhang', window=30)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries"), "model": "parkinson"}),
    ],
)
def realized_volatility(
    data: list[Data],
    model: Literal[
        "std",
        "parkinson",
        "garman_klass",
        "hodges_tompkins",
        "rogers_satchell",
        "yang_zhang",
    ] = "yang_zhang",
    index: str = "date",
    window: int = 30,
    trading_periods: int | None = None,
    is_crypto: bool = False,
    clean: bool = True,
) -> OBBject[list[Data]]:
    """Calculate annualised rolling realised volatility under a chosen estimator.

    Realised volatility quantifies the dispersion of returns over a trailing
    window, scaled to an annual horizon. Six estimators are supported. The
    close-to-close standard-deviation estimator (``std``) is the textbook choice
    but discards intraday information. Range-based estimators (``parkinson``,
    ``garman_klass``, ``rogers_satchell``) extract additional signal from the
    high/low/open prices and have lower estimator variance per observation.
    ``hodges_tompkins`` corrects the small-sample bias of the close-to-close
    estimator; ``yang_zhang`` blends overnight, open-to-close, and Rogers-Satchell
    drift-invariant pieces and is the minimum-variance estimator that
    accommodates non-zero drift.

    Parameters
    ----------
    data : list[Data]
        OHLC(V) price series. Range-based estimators require ``high`` and
        ``low``; ``garman_klass`` and ``yang_zhang`` additionally require
        ``open``.
    model : RealizedVolatilityModel, optional
        Estimator to apply, by default ``"yang_zhang"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    window : PositiveInt, optional
        Rolling window length in bars, by default 30.
    trading_periods : PositiveInt, optional
        Annualisation factor. When unset, resolves to 365 if ``is_crypto`` is
        ``True``, otherwise 252.
    is_crypto : bool, optional
        When ``True`` and ``trading_periods`` is unset, annualise over 365
        instead of 252, by default ``False``.
    clean : bool, optional
        Drop leading warm-up rows where the rolling window has not yet
        filled, by default ``True``.

    Returns
    -------
    OBBject[list[RealizedVolatilityData]]
        Annualised volatility time series with ``model``, ``window``, and
        ``trading_periods`` echoed on every row.
    """
    params = RealizedVolatilityQueryParams(
        data=data,
        model=model,
        index=index,
        window=window,
        trading_periods=trading_periods,
        is_crypto=is_crypto,
        clean=clean,
    )
    validate_data(params.data, [params.window])
    df = basemodel_to_df(params.data, index=params.index)
    series = _VOL_FUNCTIONS[params.model](
        df,
        window=params.window,
        trading_periods=params.trading_periods,
        is_crypto=params.is_crypto,
        clean=params.clean,
    )
    resolved_tp = params.trading_periods or (365 if params.is_crypto else 252)
    out = (
        series.to_frame(name="volatility")
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    out["model"] = params.model
    out["window"] = params.window
    out["trading_periods"] = resolved_tp
    return OBBject(
        results=[RealizedVolatilityData(**row) for row in out.to_dict(orient="records")]
    )


class RealizedVolatilityCompareQueryParams(QueryParams):
    """Query parameters for the side-by-side realized-volatility endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series. All four price columns (``open``, ``high``, ``low``,
        ``close``) are required because every estimator family is evaluated.
    models : list[RealizedVolatilityModel], optional
        Estimators to compute, defaults to all six.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    window : PositiveInt, optional
        Rolling window length in bars, by default 30.
    trading_periods : PositiveInt, optional
        Annualisation factor. When unset, resolves to 365 if ``is_crypto`` is
        ``True``, otherwise 252.
    is_crypto : bool, optional
        When ``True`` and ``trading_periods`` is unset, annualise over 365
        instead of 252, by default ``False``.
    clean : bool, optional
        Drop rows where any requested model has not yet warmed up, by default
        ``True``.
    """

    __category__ = "volatility"
    __output_columns__ = (
        "date",
        "std",
        "parkinson",
        "garman_klass",
        "hodges_tompkins",
        "rogers_satchell",
        "yang_zhang",
    )

    data: list[Data] = Field(
        description="Input OHLC price series — every column required."
    )
    models: list[RealizedVolatilityModel] = Field(  # ty: ignore[invalid-assignment]
        default_factory=lambda: [
            "std",
            "parkinson",
            "garman_klass",
            "hodges_tompkins",
            "rogers_satchell",
            "yang_zhang",
        ],
        description="Estimators to compute. Defaults to all six.",
    )
    index: str = Field(default="date")
    window: PositiveInt = Field(default=30)
    trading_periods: PositiveInt | None = Field(default=None)
    is_crypto: bool = Field(default=False)
    clean: bool = Field(
        default=True,
        description="Drop rows where ANY requested model has not yet warmed up.",
    )


class RealizedVolatilityCompareData(Data):
    """One row aligning every requested estimator on the same date.

    Parameters
    ----------
    date : date | str
        Observation date.
    std : float, optional
        Close-to-close standard-deviation volatility.
    parkinson : float, optional
        Parkinson range-based volatility.
    garman_klass : float, optional
        Garman-Klass OHLC volatility.
    hodges_tompkins : float, optional
        Bias-corrected close-to-close volatility.
    rogers_satchell : float, optional
        Rogers-Satchell drift-invariant volatility.
    yang_zhang : float, optional
        Yang-Zhang minimum-variance volatility.
    """

    date: datetime | dateType | str
    std: float | None = None
    parkinson: float | None = None
    garman_klass: float | None = None
    hodges_tompkins: float | None = None
    rogers_satchell: float | None = None
    yang_zhang: float | None = None


@router.command(
    methods=["POST"],
    examples=[APIEx(parameters={"data": APIEx.mock_data("timeseries")})],
)
def realized_volatility_compare(
    data: list[Data],
    models: list[
        Literal[
            "std",
            "parkinson",
            "garman_klass",
            "hodges_tompkins",
            "rogers_satchell",
            "yang_zhang",
        ]
    ]
    | None = None,
    index: str = "date",
    window: int = 30,
    trading_periods: int | None = None,
    is_crypto: bool = False,
    clean: bool = True,
) -> OBBject[list[Data]]:
    """Compute realised volatility under every requested estimator, side by side.

    This endpoint returns a wide-format time series with one column per
    estimator, aligned on a common date index. It is useful for visualising
    estimator dispersion — range-based estimators typically respond more
    quickly to regime shifts than close-to-close, and ``yang_zhang`` typically
    sits between the range-based and close-to-close families.

    Parameters
    ----------
    data : list[Data]
        OHLC price series. All four price columns are required.
    models : list[RealizedVolatilityModel], optional
        Estimators to compute. ``None`` selects all six.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    window : PositiveInt, optional
        Rolling window length in bars, by default 30.
    trading_periods : PositiveInt, optional
        Annualisation factor. When unset, resolves to 365 if ``is_crypto`` is
        ``True``, otherwise 252.
    is_crypto : bool, optional
        When ``True`` and ``trading_periods`` is unset, annualise over 365
        instead of 252, by default ``False``.
    clean : bool, optional
        Drop rows where any requested model has not yet warmed up, by default
        ``True``.

    Returns
    -------
    OBBject[list[RealizedVolatilityCompareData]]
        Wide-format frame with one column per requested estimator.
    """
    import pandas as pd

    default_models: list[RealizedVolatilityModel] = [
        "std",
        "parkinson",
        "garman_klass",
        "hodges_tompkins",
        "rogers_satchell",
        "yang_zhang",
    ]
    params = RealizedVolatilityCompareQueryParams(
        data=data,
        models=models or default_models,
        index=index,
        window=window,
        trading_periods=trading_periods,
        is_crypto=is_crypto,
        clean=clean,
    )
    validate_data(params.data, [params.window])
    df = basemodel_to_df(params.data, index=params.index)
    columns: dict[str, pd.Series] = {}
    for m in params.models:
        columns[m] = _VOL_FUNCTIONS[m](  # ty: ignore[invalid-assignment]
            df,
            window=params.window,
            trading_periods=params.trading_periods,
            is_crypto=params.is_crypto,
            clean=False,
        )
    wide = pd.DataFrame(columns)
    if params.clean:
        wide = wide.dropna(how="any")
    wide = wide.reset_index().rename(columns={params.index: "date"})
    return OBBject(
        results=[
            RealizedVolatilityCompareData(**row)
            for row in wide.to_dict(orient="records")
        ]
    )


class ConesQueryParams(QueryParams):
    """Query parameters for the volatility-cones endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    lower_q : float, optional
        Lower quantile for the cone band, by default 0.25. Must be in
        ``(0, 1)`` and strictly less than ``upper_q``.
    upper_q : float, optional
        Upper quantile for the cone band, by default 0.75. Must be in
        ``(0, 1)`` and strictly greater than ``lower_q``.
    model : RealizedVolatilityModel, optional
        Estimator applied to each rolling window, by default ``"std"``.
    is_crypto : bool, optional
        When ``True`` and ``trading_periods`` is unset, annualise over 365
        instead of 252, by default ``False``.
    trading_periods : PositiveInt, optional
        Annualisation factor. When unset, resolves to 365 if ``is_crypto`` is
        ``True``, otherwise 252.
    """

    __category__ = "volatility"
    __output_columns__ = (
        "window",
        "realized",
        "min",
        "lower",
        "median",
        "upper",
        "max",
    )

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(default="date")
    lower_q: float = Field(
        default=0.25,
        description="Lower quantile for the cone band (0–1, exclusive of 1).",
    )
    upper_q: float = Field(
        default=0.75,
        description="Upper quantile for the cone band (0–1, exclusive of 1).",
    )
    model: RealizedVolatilityModel = Field(default="std")
    is_crypto: bool = Field(default=False)
    trading_periods: PositiveInt | None = Field(default=None)


class ConesData(Data):
    """One row per analysis window for the cones table.

    Parameters
    ----------
    window : int
        Rolling window length in bars (typically 10, 30, 60, 90, 120, 150, 180,
        210, 240, 270, 300, 330, 360).
    realized : float, optional
        Most-recent annualised volatility at this window.
    min : float, optional
        Historical minimum of annualised volatility at this window.
    lower : float, optional
        Lower-quantile cone band at this window.
    median : float, optional
        Historical median of annualised volatility at this window.
    upper : float, optional
        Upper-quantile cone band at this window.
    max : float, optional
        Historical maximum of annualised volatility at this window.
    """

    window: int = Field(description="Rolling window length in bars.")
    realized: float | None = Field(description="Most-recent annualised volatility.")
    min: float | None
    lower: float | None = Field(description="Lower-quantile cone band.")
    median: float | None
    upper: float | None = Field(description="Upper-quantile cone band.")
    max: float | None


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Get volatility cones for the past two years of SPY.",
            code=[
                "data = obb.equity.price.historical(symbol='SPY', start_date='2022-01-01', provider='yfinance').results",
                "cones = obb.technical.cones(data=data, model='yang_zhang')",
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
    """Build a volatility-cone snapshot summarising realised volatility by window.

    A volatility cone visualises how realised volatility depends on the lookback
    horizon. For each rolling window (10, 30, 60, …, 360 bars by default) the
    endpoint reports the most-recent annualised volatility alongside the
    historical minimum, lower quantile, median, upper quantile, and maximum of
    rolling volatility at that window. The most-recent value plotted against
    the historical band exposes whether the market is unusually quiet or
    turbulent relative to its own past behaviour at that horizon.

    Parameters
    ----------
    data : list[Data]
        OHLC price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    lower_q : float, optional
        Lower quantile for the cone band, by default 0.25.
    upper_q : float, optional
        Upper quantile for the cone band, by default 0.75.
    model : RealizedVolatilityModel, optional
        Estimator to apply at each window, by default ``"std"``.
    is_crypto : bool, optional
        When ``True`` and ``trading_periods`` is unset, annualise over 365
        instead of 252, by default ``False``.
    trading_periods : PositiveInt, optional
        Annualisation factor. When unset, resolves to 365 if ``is_crypto`` is
        ``True``, otherwise 252.

    Returns
    -------
    OBBject[list[ConesData]]
        One row per analysis window with realised, min, lower, median, upper,
        max columns.
    """
    params = ConesQueryParams(
        data=data,
        index=index,
        lower_q=lower_q,
        upper_q=upper_q,
        model=model,
        is_crypto=is_crypto,
        trading_periods=trading_periods,
    )
    df = basemodel_to_df(params.data, index=params.index)
    table = calculate_cones(
        df,
        lower_q=params.lower_q,
        upper_q=params.upper_q,
        is_crypto=params.is_crypto,
        model=params.model,
        trading_periods=params.trading_periods,
    )
    rename = {
        col: (
            "lower"
            if col.startswith("lower_")
            else "upper"
            if col.startswith("upper_")
            else col
        )
        for col in table.columns
    }
    out = table.rename(columns=rename).copy()
    out["window"] = out["window"].astype(int)
    return OBBject(results=[ConesData(**row) for row in out.to_dict(orient="records")])


class AtrQueryParams(QueryParams):
    """Query parameters for the Average True Range endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series. ``high``, ``low``, and ``close`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        ATR lookback window, by default 14.
    mamode : {"sma", "ema", "wma", "rma"}, optional
        Smoothing applied to true-range. ``rma`` is the Wilder default,
        by default ``"rma"``.
    drift : PositiveInt, optional
        Difference period for true-range, by default 1.
    offset : int, optional
        Shift the output series by this many bars, by default 0.
    """

    __category__ = "volatility"
    __output_columns__ = ("date", "atr")

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(default="date")
    length: PositiveInt = Field(default=14, description="ATR lookback window.")
    mamode: Literal["sma", "ema", "wma", "rma"] = Field(
        default="rma",
        description="Smoothing applied to true-range. ``rma`` is the Wilder default.",
    )
    drift: PositiveInt = Field(
        default=1, description="Difference period for true-range."
    )
    offset: int = Field(default=0)


class AtrData(Data):
    """One row of the ATR time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    atr : float, optional
        Average true range over the trailing ``length`` bars. ``None`` for the
        warm-up rows preceding ``length``.
    """

    date: datetime | dateType | str
    atr: float | None = Field(
        description="Average true range over the trailing ``length`` bars."
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="ATR(14) on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "atr = obb.technical.atr(data=data, length=14)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries"), "length": 14}),
    ],
)
def atr(
    data: list[Data],
    index: str = "date",
    length: int = 14,
    mamode: Literal["sma", "ema", "wma", "rma"] = "rma",
    drift: int = 1,
    offset: int = 0,
) -> OBBject[list[Data]]:
    """Calculate the Average True Range (ATR), Wilder's volatility measure.

    ATR is the trailing average of the true range, where true range on each
    bar is the maximum of (a) high minus low, (b) absolute value of high minus
    previous close, and (c) absolute value of low minus previous close. By
    including gaps, true range captures volatility that close-to-close measures
    miss. ATR is non-directional — it measures the magnitude of price
    excursions, not their sign — and is a standard input for position-sizing
    rules and stop-loss placement.

    Parameters
    ----------
    data : list[Data]
        OHLC price series; ``high``, ``low``, and ``close`` are required.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    length : PositiveInt, optional
        ATR lookback window in bars, by default 14.
    mamode : {"sma", "ema", "wma", "rma"}, optional
        Smoothing applied to true-range. ``rma`` is the Wilder default,
        by default ``"rma"``.
    drift : PositiveInt, optional
        Difference period for true-range, by default 1.
    offset : int, optional
        Shift the output series by this many bars, by default 0.

    Returns
    -------
    OBBject[list[AtrData]]
        ATR time series with warm-up rows dropped.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = AtrQueryParams(
        data=data,
        index=index,
        length=length,
        mamode=mamode,
        drift=drift,
        offset=offset,
    )
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)
    series = df.ta.atr(
        length=params.length,
        mamode=params.mamode,
        drift=params.drift,
        offset=params.offset,
    )
    out = (
        pd.DataFrame({"atr": series})
        .dropna()
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    return OBBject(results=[AtrData(**row) for row in out.to_dict(orient="records")])


__all__ = [
    "AtrData",
    "AtrQueryParams",
    "ConesData",
    "ConesQueryParams",
    "RealizedVolatilityCompareData",
    "RealizedVolatilityCompareQueryParams",
    "RealizedVolatilityData",
    "RealizedVolatilityQueryParams",
    "RealizedVolatilityModel",
    "atr",
    "cones",
    "realized_volatility",
    "realized_volatility_compare",
    "router",
]
