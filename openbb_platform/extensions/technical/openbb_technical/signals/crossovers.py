"""Moving-average crossover signal."""

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

from openbb_technical.helpers import validate_data

# Bare 'date' alias for function signatures so the static-package builder
# writes 'date' (which it imports from datetime) rather than 'dateType' which it does not.
date = dateType


router = Router(prefix="", description="Signal-style technical indicators.")


MaMode = Literal["sma", "ema", "wma", "hma", "zlma"]


class CrossoversQueryParams(QueryParams):
    """Query parameters for the moving-average crossover endpoint.

    Parameters
    ----------
    data : list[Data]
        Input price series containing ``target``.
    target : str, optional
        Column on which to compute the moving averages, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    fast_length : PositiveInt, optional
        Lookback for the fast moving average, by default 20.
    slow_length : PositiveInt, optional
        Lookback for the slow moving average. Must be strictly greater than
        ``fast_length``, by default 50.
    mamode : {"sma", "ema", "wma", "hma", "zlma"}, optional
        Moving-average flavour, by default ``"sma"``.
    """

    __category__ = "signal"
    __output_columns__ = (
        "date",
        "direction",
        "fast_value",
        "slow_value",
        "price",
        "distance",
    )

    data: list[Data] = Field(description="Input price series.")
    target: str = Field(
        default="close", description="Column on which to compute moving averages."
    )
    index: str = Field(default="date", description="Index column name in ``data``.")
    fast_length: PositiveInt = Field(
        default=20, description="Lookback for the fast moving average."
    )
    slow_length: PositiveInt = Field(
        default=50, description="Lookback for the slow moving average."
    )
    mamode: MaMode = Field(
        default="sma",
        description="Moving-average flavour. ``sma`` is the default; ``ema``, ``wma``, ``hma`` and ``zlma`` are also supported.",
    )

    @field_validator("slow_length")
    @classmethod
    def slow_must_exceed_fast(cls, v: int, info) -> int:
        """Enforce ``slow_length > fast_length``."""
        fast = info.data.get("fast_length")
        if fast is not None and v <= fast:
            raise ValueError("slow_length must be greater than fast_length.")
        return v


class CrossoverEvent(Data):
    """One row per moving-average crossover bar (sparse output).

    Parameters
    ----------
    date : date | str
        Date of the crossover bar.
    direction : {"bullish", "bearish"}
        ``"bullish"`` when the fast average crosses above the slow average;
        ``"bearish"`` when the fast average crosses below the slow average.
    fast_value : float
        Fast moving-average value at the crossover bar.
    slow_value : float
        Slow moving-average value at the crossover bar.
    price : float
        Target-column price at the crossover bar.
    distance : float
        Signed gap ``fast_value - slow_value``. Positive for bullish crossovers
        and negative for bearish crossovers.
    """

    date: datetime | dateType | str = Field(description="Date of the crossover bar.")
    direction: Literal["bullish", "bearish"] = Field(
        description="``bullish`` when fast crosses above slow, ``bearish`` when fast crosses below.",
    )
    fast_value: float = Field(
        description="Fast moving-average value at the crossover bar."
    )
    slow_value: float = Field(
        description="Slow moving-average value at the crossover bar."
    )
    price: float = Field(description="Target-column price at the crossover bar.")
    distance: float = Field(
        description="``fast_value - slow_value``. Positive for bullish, negative for bearish crossovers.",
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="20/50 SMA crossover events on daily SPY.",
            code=[
                "data = obb.equity.price.historical(symbol='SPY', start_date='2022-01-01', provider='yfinance').results",
                "events = obb.technical.crossovers(data=data, fast_length=20, slow_length=50)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def crossovers(
    data: list[Data],
    target: str = "close",
    index: str = "date",
    fast_length: int = 20,
    slow_length: int = 50,
    mamode: Literal["sma", "ema", "wma", "hma", "zlma"] = "sma",
) -> OBBject[list[Data]]:
    """Detect bullish and bearish moving-average crossover events.

    A crossover occurs when a fast moving average changes sign relative to a
    slow moving average. When the fast average rises through the slow average
    the cross is bullish ("golden cross" in the classical 50/200 case); the
    opposite cross is bearish ("death cross"). Both averages are computed on
    the same target column with the selected smoother — simple, exponential,
    weighted, Hull, or zero-lag — and the sign of their difference is checked
    bar by bar for a strict polarity flip. Bars where either series is in its
    warm-up window, or where the difference is exactly zero, are skipped so
    that only confirmed flips are emitted.

    Traders use crossovers as a trend-following entry or exit trigger: the
    fast-over-slow polarity proxies the dominant trend direction and the
    crossover bar marks the regime change. Output is sparse — one row per
    crossover — which makes it easy to align with price-action plots or to
    chain into a higher-level backtest.

    Parameters
    ----------
    data : list[Data]
        Input price series containing ``target``.
    target : str, optional
        Column on which to compute moving averages, by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    fast_length : PositiveInt, optional
        Lookback for the fast moving average, by default 20.
    slow_length : PositiveInt, optional
        Lookback for the slow moving average, by default 50.
    mamode : {"sma", "ema", "wma", "hma", "zlma"}, optional
        Moving-average flavour, by default ``"sma"``.

    Returns
    -------
    OBBject[list[CrossoverEvent]]
        Sparse list of crossover events with direction, both moving-average
        values, the target-column price, and the signed distance.
    """
    import numpy as np
    import pandas_ta as ta  # noqa: F401

    params = CrossoversQueryParams(
        data=data,
        target=target,
        index=index,
        fast_length=fast_length,
        slow_length=slow_length,
        mamode=mamode,
    )
    validate_data(params.data, [params.slow_length])
    df = basemodel_to_df(params.data, index=params.index)
    series = df[params.target]
    fast = getattr(series.to_frame(name=params.target).ta, params.mamode)(
        length=params.fast_length
    )
    slow = getattr(series.to_frame(name=params.target).ta, params.mamode)(
        length=params.slow_length
    )
    diff = (fast - slow).dropna()
    if diff.empty:
        return OBBject(results=[])
    sign = np.sign(diff)
    prev = sign.shift(1)
    flips = (sign != prev) & (sign != 0) & (prev != 0) & (sign * prev < 0)
    events: list[CrossoverEvent] = []
    for ts in diff.index[flips.fillna(False)]:
        d = float(diff.loc[ts])
        events.append(
            CrossoverEvent(
                date=ts,
                direction="bullish" if d > 0 else "bearish",
                fast_value=float(fast.loc[ts]),
                slow_value=float(slow.loc[ts]),
                price=float(series.loc[ts]),
                distance=d,
            )
        )
    # Per-endpoint Data subclass; return annotation uses base Data for
    # static-package compatibility (list invariance prevents subtype matching).
    return OBBject(results=events)  # ty: ignore[invalid-return-type]


__all__ = [
    "CrossoverEvent",
    "CrossoversQueryParams",
    "MaMode",
    "crossovers",
    "router",
]
