"""Candlestick-pattern detection."""

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
from pydantic import Field

# Bare 'date' alias for function signatures so the static-package builder
# writes 'date' (which it imports from datetime) rather than 'dateType' which it does not.
date = dateType


router = Router(prefix="", description="Candlestick-pattern signals.")


SUPPORTED_PATTERNS: tuple[str, ...] = (
    "doji",
    "hammer",
    "engulfing",
    "marubozu",
    "spinning_top",
)


Direction = Literal["bullish", "bearish", "neutral"]


class CandlestickPatternsQueryParams(QueryParams):
    """Query parameters for the candlestick-patterns endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    patterns : list[str], optional
        Subset of patterns to scan for. ``None`` runs every entry in
        ``SUPPORTED_PATTERNS``.
    """

    __category__ = "signal"
    __output_columns__ = ("date", "pattern", "direction", "confidence")

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(default="date", description="Index column name in ``data``.")
    patterns: list[str] | None = Field(
        default=None,
        description=(
            "Subset of patterns to scan for. ``None`` runs every entry in "
            "``SUPPORTED_PATTERNS``."
        ),
    )


class PatternEvent(Data):
    """One row per confirmed pattern bar (sparse output).

    Parameters
    ----------
    date : date | str
        Date of the pattern bar.
    pattern : str
        Pattern name in lower-snake-case.
    direction : {"bullish", "bearish", "neutral"}
        Bias implied by the pattern.
    confidence : float
        Heuristic 0-1 score derived from body and shadow ratios. Higher means
        the bar matches the textbook pattern more cleanly.
    """

    date: datetime | dateType | str = Field(description="Date of the pattern bar.")
    pattern: str = Field(description="Pattern name, lower-snake-case.")
    direction: Direction = Field(
        description="Bias implied by the pattern: ``bullish``, ``bearish`` or ``neutral``.",
    )
    confidence: float = Field(
        description=(
            "Heuristic 0-1 score derived from body/shadow ratios. Higher "
            "means the bar matches the textbook pattern more cleanly."
        ),
    )


def _body_and_range(o: float, h: float, l: float, c: float) -> tuple[float, float]:
    """Return ``(body, range)`` for one OHLC bar."""
    body = abs(c - o)
    rng = h - l
    return body, rng


def _detect_doji(row) -> tuple[Direction, float] | None:
    """Detect a Doji: tiny body relative to total range, signalling indecision."""
    body, rng = _body_and_range(row["open"], row["high"], row["low"], row["close"])
    if rng <= 0:
        return None
    ratio = body / rng
    if ratio > 0.1:
        return None
    return "neutral", float(1.0 - ratio * 10.0)


def _detect_hammer(row) -> tuple[Direction, float] | None:
    """Detect a Hammer: small body in the upper half with a long lower shadow."""
    o, h, l, c = row["open"], row["high"], row["low"], row["close"]
    body, rng = _body_and_range(o, h, l, c)
    if rng <= 0 or body <= 0:
        return None
    upper = h - max(o, c)
    lower = min(o, c) - l
    if lower < 2.0 * body:
        return None
    if upper > body:
        return None
    body_mid = (o + c) / 2.0
    if (body_mid - l) / rng < 2.0 / 3.0:
        return None
    return "bullish", float(min(1.0, lower / (3.0 * body)))


def _detect_marubozu(row) -> tuple[Direction, float] | None:
    """Detect a Marubozu: full body with near-zero upper and lower shadows."""
    o, h, l, c = row["open"], row["high"], row["low"], row["close"]
    body, rng = _body_and_range(o, h, l, c)
    if rng <= 0 or body <= 0:
        return None
    upper = h - max(o, c)
    lower = min(o, c) - l
    if body / rng < 0.95:
        return None
    # Unreachable: ``rng = body + upper + lower``, so ``body/rng >= 0.95``
    # bounds the combined shadows at 5% — neither alone can exceed it.
    if upper / rng > 0.05 or lower / rng > 0.05:  # pragma: no cover
        return None
    direction: Direction = "bullish" if c > o else "bearish"
    return direction, float(body / rng)


def _detect_spinning_top(row) -> tuple[Direction, float] | None:
    """Detect a Spinning Top: small body with comparable upper and lower shadows."""
    o, h, l, c = row["open"], row["high"], row["low"], row["close"]
    body, rng = _body_and_range(o, h, l, c)
    if rng <= 0:
        return None
    upper = h - max(o, c)
    lower = min(o, c) - l
    if body / rng > 0.3 or body / rng < 0.05:
        return None
    if upper <= 0 or lower <= 0:
        return None
    larger = max(upper, lower)
    smaller = min(upper, lower)
    if smaller / larger < 0.5:
        return None
    return "neutral", float(smaller / larger)


def _detect_engulfing(row, prev) -> tuple[Direction, float] | None:
    """Detect an Engulfing bar: current real body fully engulfs the previous."""
    if prev is None:
        return None
    o, c = row["open"], row["close"]
    po, pc = prev["open"], prev["close"]
    body = abs(c - o)
    prev_body = abs(pc - po)
    if body <= 0 or prev_body <= 0:
        return None
    cur_top = max(o, c)
    cur_bot = min(o, c)
    prev_top = max(po, pc)
    prev_bot = min(po, pc)
    if not (cur_top >= prev_top and cur_bot <= prev_bot):
        return None
    if c > o and pc < po:
        return "bullish", float(min(1.0, body / (prev_body * 2.0)))
    if c < o and pc > po:
        return "bearish", float(min(1.0, body / (prev_body * 2.0)))
    return None


_DETECTORS = {
    "doji": _detect_doji,
    "hammer": _detect_hammer,
    "marubozu": _detect_marubozu,
    "spinning_top": _detect_spinning_top,
    "engulfing": _detect_engulfing,
}

_TWO_BAR = {"engulfing"}


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Scan all supported patterns on daily SPY.",
            code=[
                "data = obb.equity.price.historical(symbol='SPY', start_date='2022-01-01', provider='yfinance').results",
                "patterns = obb.technical.candlestick_patterns(data=data)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def candlestick_patterns(
    data: list[Data],
    index: str = "date",
    patterns: list[str] | None = None,
) -> OBBject[list[Data]]:
    """Scan OHLC bars for classical candlestick patterns and emit one row per match.

    Candlestick patterns encode multi-century intuitions about the short-term
    balance of buying and selling pressure in the shape of a single bar (or
    in some cases the pair of the current and previous bars). This endpoint
    walks an OHLC series bar by bar, applies a configurable subset of
    detectors, and emits one row per pattern that the bar matches. The five
    supported patterns are Doji (indecision), Hammer (bullish reversal off a
    low), Marubozu (strong directional bar with negligible shadows), Spinning
    Top (indecision with comparable shadows), and Engulfing (two-bar reversal
    where the current real body fully covers the previous one).

    Each match is accompanied by an implied direction — bullish, bearish, or
    neutral — and a heuristic 0-1 confidence score derived from the relative
    body and shadow geometry. The confidence score lets downstream code
    rank matches and discard borderline cases, while the sparse one-row-per-
    match shape composes naturally with chart overlays and rule-based
    strategies.

    Parameters
    ----------
    data : list[Data]
        OHLC price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    patterns : list[str], optional
        Subset of patterns to scan for. ``None`` runs every entry in
        ``SUPPORTED_PATTERNS``.

    Returns
    -------
    OBBject[list[PatternEvent]]
        Sparse list of pattern matches with date, pattern name, implied
        direction, and a 0-1 confidence score.
    """
    params = CandlestickPatternsQueryParams(
        data=data,
        index=index,
        patterns=patterns,
    )
    requested = params.patterns or list(SUPPORTED_PATTERNS)
    requested = [p for p in requested if p in SUPPORTED_PATTERNS]
    if not requested:
        return OBBject(results=[])

    df = basemodel_to_df(params.data, index=params.index)

    events: list[PatternEvent] = []
    prev_row = None
    for ts, row in df.iterrows():
        for name in requested:
            detector = _DETECTORS[name]
            hit = (
                detector(row, prev_row)  # ty: ignore[too-many-positional-arguments]
                if name in _TWO_BAR
                else detector(row)  # ty: ignore[missing-argument]
            )
            if hit is None:
                continue
            direction, confidence = hit
            events.append(
                PatternEvent(
                    date=ts,  # ty: ignore[invalid-argument-type]
                    pattern=name,
                    direction=direction,
                    confidence=float(max(0.0, min(1.0, confidence))),
                )
            )
        prev_row = row
    # Per-endpoint Data subclass; return annotation uses base Data for
    # static-package compatibility (list invariance prevents subtype matching).
    return OBBject(results=events)  # ty: ignore[invalid-return-type]


__all__ = [
    "CandlestickPatternsQueryParams",
    "Direction",
    "PatternEvent",
    "SUPPORTED_PATTERNS",
    "candlestick_patterns",
    "router",
]
