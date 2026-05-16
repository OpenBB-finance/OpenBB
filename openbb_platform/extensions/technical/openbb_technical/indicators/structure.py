"""Structure-family technical indicators."""

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
from pydantic import Field, PositiveInt

from openbb_technical.helpers import calculate_fib_levels

# Bare 'date' alias for function signatures so the static-package builder
# writes 'date' (which it imports from datetime) rather than 'dateType' which it does not.
date = dateType


router = Router(prefix="", description="Structure indicators.")


PivotMethod = Literal["classic", "fibonacci", "woodie", "camarilla", "demark"]
PivotAnchor = Literal["day", "week", "month"]

_PIVOT_METHOD_TAG = {
    "classic": "CLAS",
    "fibonacci": "FIBO",
    "woodie": "WOOD",
    "camarilla": "CAMA",
    "demark": "DEMA",
}

_PIVOT_ANCHOR_FREQ = {"day": "D", "week": "W", "month": "ME"}


class FibQueryParams(QueryParams):
    """Query parameters for the Fibonacci-retracement endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC(V) price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    close_column : {"close", "adj_close"}, optional
        Column used for high/low detection, by default ``"close"``.
    period : PositiveInt, optional
        Lookback in bars used to identify the swing high and swing low when
        ``start_date`` and ``end_date`` are not provided, by default 120.
    start_date : str, optional
        Explicit retracement start date. When set together with ``end_date``,
        the swing endpoints are taken from this fixed window instead of from
        the trailing ``period``, by default ``None``.
    end_date : str, optional
        Explicit retracement end date paired with ``start_date``,
        by default ``None``.
    """

    __category__ = "structure"
    __output_columns__ = ("level", "price")

    data: list[Data] = Field(description="OHLC(V) price series.")
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    close_column: Literal["close", "adj_close"] = Field(
        default="close",
        description="Column used for high/low detection.",
    )
    period: PositiveInt = Field(
        default=120, description="Lookback in bars for retracement."
    )
    start_date: str | None = Field(
        default=None, description="Explicit retracement start date."
    )
    end_date: str | None = Field(
        default=None, description="Explicit retracement end date."
    )


class FibData(Data):
    """One Fibonacci retracement level.

    Parameters
    ----------
    level : str
        Retracement percentage label, e.g. ``"38.2%"``.
    price : float
        Price at the retracement level, expressed in the same units as the
        input ``close_column``.
    """

    level: str = Field(description="Retracement percentage label, e.g. ``38.2%``.")
    price: float = Field(description="Price at the retracement level.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Fibonacci retracement on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "fib = obb.technical.fib(data=data, period=120)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def fib(params: FibQueryParams) -> OBBject[list[FibData]]:
    """Compute Fibonacci retracement levels between a swing high and swing low."""
    df = basemodel_to_df(params.data, index=params.index)
    df_fib, _, _, _, _, _ = calculate_fib_levels(
        data=df,
        close_col=params.close_column,
        limit=params.period,
        start_date=params.start_date,
        end_date=params.end_date,
    )
    out = df_fib.rename(columns={"Level": "level", "Price": "price"})
    return OBBject(results=[FibData(**row) for row in out.to_dict(orient="records")])


class DemarkQueryParams(QueryParams):
    """Query parameters for the DeMark sequential endpoint.

    Parameters
    ----------
    data : list[Data]
        Price series. Only the ``target`` column is consumed.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    target : str, optional
        Column on which the sequential counts are evaluated,
        by default ``"close"``.
    show_all : bool, optional
        When ``True`` show counts 1-13; when ``False`` show only counts 6-9,
        by default ``True``.
    asint : bool, optional
        Cast counts to integers and fill ``NaN`` with 0, by default ``True``.
    offset : int, optional
        Shift the output series by this many bars, by default 0.
    """

    __category__ = "structure"
    __output_columns__ = ("date", "up", "down")

    data: list[Data] = Field(description="Price series.")
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    target: str = Field(default="close", description="Column to evaluate.")
    show_all: bool = Field(
        default=True,
        description="When True show counts 1-13; False shows only 6-9.",
    )
    asint: bool = Field(
        default=True,
        description="Cast counts to integers and fill NaN with 0.",
    )
    offset: int = Field(default=0, description="Periods to offset the result.")


class DemarkData(Data):
    """One row of the DeMark sequential time series.

    Parameters
    ----------
    date : date | str
        Observation date.
    up : int | float, optional
        Upward (buy-setup/countdown) sequential count on this bar. ``None`` or
        ``0`` when no count is active.
    down : int | float, optional
        Downward (sell-setup/countdown) sequential count on this bar. ``None``
        or ``0`` when no count is active.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    up: int | float | None = Field(description="Upward sequential count.")
    down: int | float | None = Field(description="Downward sequential count.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="DeMark sequential on daily TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "demark = obb.technical.demark(data=data)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def demark(params: DemarkQueryParams) -> OBBject[list[DemarkData]]:
    """Compute Tom DeMark sequential up- and down-count exhaustion indicators."""
    import pandas_ta as ta

    df = basemodel_to_df(params.data, index=params.index)
    series = df[params.target]
    raw = ta.exhc(
        series, asint=params.asint, show_all=params.show_all, offset=params.offset
    )
    rename = {"EXHC_DNa": "down", "EXHC_UPa": "up", "EXHC_DN": "down", "EXHC_UP": "up"}
    out = (
        raw.rename(columns=rename).reset_index().rename(columns={params.index: "date"})
    )
    return OBBject(results=[DemarkData(**row) for row in out.to_dict(orient="records")])


class PivotPointsQueryParams(QueryParams):
    """Query parameters for the pivot-points endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    method : PivotMethod, optional
        Pivot-point family. ``camarilla`` is the only method that fills the
        r4/s4 outer bands, by default ``"classic"``.
    anchor : PivotAnchor, optional
        Resample anchor for the pivot calculation — daily, weekly, or
        month-end, by default ``"day"``.
    """

    __category__ = "structure"
    __output_columns__ = (
        "date",
        "pivot",
        "r1",
        "r2",
        "r3",
        "r4",
        "s1",
        "s2",
        "s3",
        "s4",
    )

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(
        default="date",
        description='Index column name in ``data``, by default ``"date"``.',
    )
    method: PivotMethod = Field(
        default="classic",
        description="Pivot-point family. ``camarilla`` is the only one that fills r4/s4.",
    )
    anchor: PivotAnchor = Field(
        default="day",
        description="Resample anchor for the pivot calculation.",
    )


class PivotPointsData(Data):
    """One row of the pivot-points table.

    Parameters
    ----------
    date : date | str
        Period start date of the resampled pivot.
    pivot : float, optional
        Central pivot price for the period.
    r1 : float, optional
        First resistance band above the pivot.
    r2 : float, optional
        Second resistance band above the pivot.
    r3 : float, optional
        Third resistance band above the pivot.
    r4 : float, optional
        Fourth resistance band; only populated when ``method='camarilla'``.
    s1 : float, optional
        First support band below the pivot.
    s2 : float, optional
        Second support band below the pivot.
    s3 : float, optional
        Third support band below the pivot.
    s4 : float, optional
        Fourth support band; only populated when ``method='camarilla'``.
    """

    date: datetime | dateType | str = Field(
        description="Period start date of the resampled pivot."
    )
    pivot: float | None = Field(description="Central pivot price.")
    r1: float | None = Field(
        default=None, description="First resistance band above the pivot."
    )
    r2: float | None = Field(
        default=None, description="Second resistance band above the pivot."
    )
    r3: float | None = Field(
        default=None, description="Third resistance band above the pivot."
    )
    r4: float | None = Field(default=None, description="Only populated for camarilla.")
    s1: float | None = Field(
        default=None, description="First support band below the pivot."
    )
    s2: float | None = Field(
        default=None, description="Second support band below the pivot."
    )
    s3: float | None = Field(
        default=None, description="Third support band below the pivot."
    )
    s4: float | None = Field(default=None, description="Only populated for camarilla.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Classic daily pivot points on TSLA.",
            code=[
                "data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').results",
                "pivots = obb.technical.pivot_points(data=data, method='classic', anchor='day')",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def pivot_points(params: PivotPointsQueryParams) -> OBBject[list[PivotPointsData]]:
    """Compute pivot-point support and resistance bands under multiple methods."""
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    df = basemodel_to_df(params.data, index=params.index)
    if params.index == "date":
        df.index = pd.to_datetime(df.index)
    freq = _PIVOT_ANCHOR_FREQ[params.anchor]
    pivots_df = df.ta.pivots(method=params.method, anchor=freq)
    tag = _PIVOT_METHOD_TAG[params.method]
    prefix = f"PIVOTS_{tag}_{freq}_"
    rename = {
        f"{prefix}P": "pivot",
        f"{prefix}R1": "r1",
        f"{prefix}R2": "r2",
        f"{prefix}R3": "r3",
        f"{prefix}R4": "r4",
        f"{prefix}S1": "s1",
        f"{prefix}S2": "s2",
        f"{prefix}S3": "s3",
        f"{prefix}S4": "s4",
    }
    out = pivots_df.rename(columns=rename)
    for col in ("pivot", "r1", "r2", "r3", "r4", "s1", "s2", "s3", "s4"):
        if col not in out.columns:
            out[col] = None
    if params.method != "camarilla":
        out["r4"] = None
        out["s4"] = None
    out = out[["pivot", "r1", "r2", "r3", "r4", "s1", "s2", "s3", "s4"]]
    out = (
        out.dropna(subset=["pivot"])
        .reset_index()
        .rename(columns={params.index: "date"})
    )
    out = out.where(pd.notna(out), None)
    return OBBject(
        results=[PivotPointsData(**row) for row in out.to_dict(orient="records")]
    )


__all__ = [
    "DemarkData",
    "DemarkQueryParams",
    "FibData",
    "FibQueryParams",
    "PivotAnchor",
    "PivotMethod",
    "PivotPointsData",
    "PivotPointsQueryParams",
    "demark",
    "fib",
    "pivot_points",
    "router",
]
