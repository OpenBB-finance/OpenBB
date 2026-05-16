"""Price/indicator divergence detection."""

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

from openbb_technical.helpers import validate_data

# Bare 'date' alias for function signatures so the static-package builder
# writes 'date' (which it imports from datetime) rather than 'dateType' which it does not.
date = dateType


router = Router(prefix="", description="Price/indicator divergence signals.")


Indicator = Literal["rsi", "macd", "stoch", "cci"]
DivergenceKind = Literal[
    "regular_bullish",
    "hidden_bullish",
    "regular_bearish",
    "hidden_bearish",
]


class DivergencesQueryParams(QueryParams):
    """Query parameters for the divergence-detection endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    indicator : {"rsi", "macd", "stoch", "cci"}
        Oscillator paired with price for divergence detection.
    indicator_length : PositiveInt, optional
        Lookback length used inside the oscillator, by default 14.
    target : str, optional
        Price column used for swing detection, by default ``"close"``.
    lookback : PositiveInt, optional
        Number of recent bars in which to search for swing pairs, by
        default 60.
    min_swing_distance : PositiveInt, optional
        Minimum number of bars separating two swing points. Also doubles as
        the half-window for local-extreme detection, by default 5.
    """

    __category__ = "signal"
    __output_columns__ = (
        "confirmation_date",
        "prior_swing_date",
        "kind",
        "price_at_prior",
        "price_at_confirmation",
        "indicator_at_prior",
        "indicator_at_confirmation",
        "strength",
    )

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(default="date", description="Index column name in ``data``.")
    indicator: Indicator = Field(
        description="Oscillator paired with price for divergence detection.",
    )
    indicator_length: PositiveInt = Field(
        default=14,
        description="Lookback length used inside the oscillator.",
    )
    target: str = Field(default="close", description="Price column used for swings.")
    lookback: PositiveInt = Field(
        default=60,
        description="Number of recent bars in which to search for swing pairs.",
    )
    min_swing_distance: PositiveInt = Field(
        default=5,
        description=(
            "Minimum number of bars separating two swing points. Also doubles "
            "as the half-window for local-extreme detection."
        ),
    )


class DivergenceEvent(Data):
    """One row per confirmed price/indicator divergence.

    Parameters
    ----------
    confirmation_date : date | str
        Bar of the later (confirming) swing.
    prior_swing_date : date | str
        Bar of the earlier swing in the pair.
    kind : {"regular_bullish", "hidden_bullish", "regular_bearish", "hidden_bearish"}
        ``regular_*`` flags reversal signals; ``hidden_*`` flags
        trend-continuation signals.
    price_at_prior : float
        Target-column price at ``prior_swing_date``.
    price_at_confirmation : float
        Target-column price at ``confirmation_date``.
    indicator_at_prior : float
        Oscillator value at ``prior_swing_date``.
    indicator_at_confirmation : float
        Oscillator value at ``confirmation_date``.
    strength : float
        0-1 score combining the relative price and indicator displacements.
        Higher means a wider, more emphatic divergence.
    """

    confirmation_date: datetime | dateType | str = Field(
        description="Bar of the later (confirming) swing.",
    )
    prior_swing_date: datetime | dateType | str = Field(
        description="Bar of the earlier swing in the pair.",
    )
    kind: DivergenceKind = Field(
        description=(
            "``regular_bullish`` / ``regular_bearish`` flag reversal signals; "
            "``hidden_*`` flag trend-continuation signals."
        ),
    )
    price_at_prior: float = Field(
        description="Target-column price at ``prior_swing_date``."
    )
    price_at_confirmation: float = Field(
        description="Target-column price at ``confirmation_date``.",
    )
    indicator_at_prior: float = Field(
        description="Oscillator value at ``prior_swing_date``.",
    )
    indicator_at_confirmation: float = Field(
        description="Oscillator value at ``confirmation_date``.",
    )
    strength: float = Field(
        description=(
            "0-1 score combining the relative price and indicator displacements. "
            "Higher means a wider, more emphatic divergence."
        ),
    )


def _compute_indicator(df, indicator: Indicator, length: int, target: str):
    """Return a single 1-D oscillator series aligned to ``df``'s index."""
    import pandas_ta as ta  # noqa: F401

    series = df[target]
    if indicator == "rsi":
        return series.to_frame(name=target).ta.rsi(length=length, close=target)
    if indicator == "cci":
        return df.ta.cci(length=length)
    if indicator == "stoch":
        result = df.ta.stoch(k=length, d=3, smooth_k=3)
        return result.iloc[:, 0]
    macd = series.to_frame(name=target).ta.macd(
        fast=12, slow=26, signal=9, close=target
    )
    return macd.iloc[:, 1]


def _local_extrema(values, distance: int) -> tuple[list[int], list[int]]:
    """Return positional indices of strict local maxima and minima."""
    n = len(values)
    highs: list[int] = []
    lows: list[int] = []
    for i in range(distance, n - distance):
        v = values[i]
        window = values[i - distance : i + distance + 1]
        if v == max(window) and sum(1 for w in window if w == v) == 1:
            highs.append(i)
        if v == min(window) and sum(1 for w in window if w == v) == 1:
            lows.append(i)
    return highs, lows


def _classify_pair(
    prior_price: float,
    later_price: float,
    prior_ind: float,
    later_ind: float,
    is_high: bool,
) -> DivergenceKind | None:
    """Classify a swing pair as one of the four divergence flavours."""
    if is_high:
        if later_price > prior_price and later_ind < prior_ind:
            return "regular_bearish"
        if later_price < prior_price and later_ind > prior_ind:
            return "hidden_bearish"
        return None
    if later_price < prior_price and later_ind > prior_ind:
        return "regular_bullish"
    if later_price > prior_price and later_ind < prior_ind:
        return "hidden_bullish"
    return None


def _strength(
    prior_price: float,
    later_price: float,
    prior_ind: float,
    later_ind: float,
) -> float:
    """Return a normalised composite of price and indicator displacement."""
    price_scale = max(abs(prior_price), abs(later_price), 1e-12)
    ind_scale = max(abs(prior_ind), abs(later_ind), 1e-12)
    price_delta = abs(later_price - prior_price) / price_scale
    ind_delta = abs(later_ind - prior_ind) / ind_scale
    return float(max(0.0, min(1.0, (price_delta + ind_delta) / 2.0)))


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="RSI divergences on daily SPY.",
            code=[
                "data = obb.equity.price.historical(symbol='SPY', start_date='2022-01-01', provider='yfinance').results",
                "events = obb.technical.divergences(data=data, indicator='rsi')",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries"), "indicator": "rsi"}),
    ],
)
def divergences(params: DivergencesQueryParams) -> OBBject[list[DivergenceEvent]]:
    """Detect regular and hidden divergences between price swings and an oscillator."""
    validate_data(params.data, [params.indicator_length, params.min_swing_distance])
    df = basemodel_to_df(params.data, index=params.index)
    ind_series = _compute_indicator(
        df, params.indicator, params.indicator_length, params.target
    )

    window = df.tail(params.lookback)
    ind_window = ind_series.reindex(window.index)

    prices = window[params.target].tolist()
    inds = ind_window.tolist()
    timestamps = list(window.index)

    import math

    valid_idx = [i for i, v in enumerate(inds) if not math.isnan(v)]
    if len(valid_idx) <= 2 * params.min_swing_distance:
        return OBBject(results=[])

    valid_set = set(valid_idx)
    price_highs, price_lows = _local_extrema(prices, params.min_swing_distance)
    price_highs = [i for i in price_highs if i in valid_set]
    price_lows = [i for i in price_lows if i in valid_set]

    events: list[DivergenceEvent] = []

    def _emit_pairs(swing_indices: list[int], is_high: bool) -> None:
        for a, b in zip(swing_indices, swing_indices[1:]):
            # Unreachable: ``_local_extrema`` enforces gap > distance for
            # any two strict extrema returned for the same kind, and
            # ``distance`` is ``min_swing_distance``. Kept as a defensive
            # guard for future callers that bypass ``_local_extrema``.
            if b - a < params.min_swing_distance:  # pragma: no cover
                continue
            kind = _classify_pair(
                prior_price=prices[a],
                later_price=prices[b],
                prior_ind=inds[a],
                later_ind=inds[b],
                is_high=is_high,
            )
            if kind is None:
                continue
            events.append(
                DivergenceEvent(
                    confirmation_date=timestamps[b],
                    prior_swing_date=timestamps[a],
                    kind=kind,
                    price_at_prior=float(prices[a]),
                    price_at_confirmation=float(prices[b]),
                    indicator_at_prior=float(inds[a]),
                    indicator_at_confirmation=float(inds[b]),
                    strength=_strength(prices[a], prices[b], inds[a], inds[b]),
                )
            )

    _emit_pairs(price_highs, is_high=True)
    _emit_pairs(price_lows, is_high=False)
    events.sort(key=lambda e: (e.confirmation_date, e.kind))
    return OBBject(results=events)


__all__ = [
    "DivergenceEvent",
    "DivergenceKind",
    "DivergencesQueryParams",
    "Indicator",
    "divergences",
    "router",
]
