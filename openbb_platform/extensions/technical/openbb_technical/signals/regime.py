"""Market-regime classification."""

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
from pydantic import Field, PositiveFloat, PositiveInt

from openbb_technical.helpers import validate_data

# Bare 'date' alias for function signatures so the static-package builder
# writes 'date' (which it imports from datetime) rather than 'dateType' which it does not.
date = dateType


router = Router(prefix="", description="Market-regime classification.")


Regime = Literal["strong_trend", "weak_trend", "ranging", "transition"]


def _classify(
    adx: float | None,
    chop: float | None,
    adx_threshold: float,
    chop_threshold: float,
) -> Regime:
    """Map a single bar's ADX and Choppiness pair to a regime label."""
    if adx is None or chop is None:
        return "transition"
    if adx > adx_threshold and chop < chop_threshold:
        return "strong_trend"
    if adx > adx_threshold / 2.0:
        return "weak_trend"
    if chop > chop_threshold:
        return "ranging"
    return "transition"


class RegimeQueryParams(QueryParams):
    """Query parameters for the regime-classification endpoint.

    Parameters
    ----------
    data : list[Data]
        OHLC price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    adx_length : PositiveInt, optional
        ADX lookback window, by default 14.
    choppiness_length : PositiveInt, optional
        Choppiness Index lookback window, by default 14.
    adx_trend_threshold : PositiveFloat, optional
        ADX above this threshold marks a trending bar. Half this value is
        the cutoff for a weak trend, by default 25.0.
    choppiness_range_threshold : PositiveFloat, optional
        Choppiness above this threshold marks a ranging bar. The default
        61.8 is a common Fibonacci-derived cutoff.
    """

    __category__ = "signal"
    __output_columns__ = ("date", "adx", "choppiness", "regime", "regime_changed")

    data: list[Data] = Field(description="OHLC price series.")
    index: str = Field(default="date", description="Index column name in ``data``.")
    adx_length: PositiveInt = Field(default=14, description="ADX lookback window.")
    choppiness_length: PositiveInt = Field(
        default=14,
        description="Choppiness Index lookback window.",
    )
    adx_trend_threshold: PositiveFloat = Field(
        default=25.0,
        description=(
            "ADX above this threshold marks a trending bar. Half this value is "
            "the cutoff for a weak trend."
        ),
    )
    choppiness_range_threshold: PositiveFloat = Field(
        default=61.8,
        description=(
            "Choppiness above this threshold marks a ranging bar. The default "
            "61.8 is a common Fibonacci-derived cutoff."
        ),
    )


class RegimeData(Data):
    """One bar of regime labelling alongside its underlying readings.

    Parameters
    ----------
    date : date | str
        Observation date.
    adx : float, optional
        ADX reading at this bar. ``None`` during warm-up.
    choppiness : float, optional
        Choppiness Index reading at this bar. ``None`` during warm-up.
    regime : {"strong_trend", "weak_trend", "ranging", "transition"}
        Classified regime for this bar.
    regime_changed : bool
        ``True`` when this bar's regime differs from the previous bar's.
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    adx: float | None = Field(
        description="ADX reading at this bar. ``None`` during warm-up."
    )
    choppiness: float | None = Field(
        description="Choppiness Index reading at this bar. ``None`` during warm-up.",
    )
    regime: Regime = Field(description="Classified regime for this bar.")
    regime_changed: bool = Field(
        description="``True`` when this bar's regime differs from the previous bar's.",
    )


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Daily regime labelling on SPY.",
            code=[
                "data = obb.equity.price.historical(symbol='SPY', start_date='2022-01-01', provider='yfinance').results",
                "regime = obb.technical.regime(data=data)",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries")}),
    ],
)
def regime(
    data: list[Data],
    index: str = "date",
    adx_length: int = 14,
    choppiness_length: int = 14,
    adx_trend_threshold: float = 25.0,
    choppiness_range_threshold: float = 61.8,
) -> OBBject[list[Data]]:
    """Label each bar with a market regime from ADX and Choppiness Index pairs.

    A market regime summarises whether price is trending or chopping
    sideways. This endpoint combines two complementary indicators: ADX
    measures the absolute strength of a trend regardless of direction, and
    the Choppiness Index measures how much of the recent range has been
    retraced — high choppiness indicates a directionless market. Each bar
    is classified into one of four labels. ``strong_trend`` requires both
    high ADX and low choppiness. ``weak_trend`` is satisfied by moderate
    ADX (above half the trend threshold) when the strong-trend conditions
    are not met. ``ranging`` is reserved for bars with low ADX and high
    choppiness. Everything else, including warm-up bars where either input
    is unavailable, is labelled ``transition``.

    Traders use regime labels to gate strategy logic — trend-following
    rules run only in trending regimes; mean-reversion rules run only in
    ranging regimes — and to size positions based on the prevailing market
    character. The ``regime_changed`` flag is convenient for triggering
    one-shot logic on regime transitions.

    Parameters
    ----------
    data : list[Data]
        OHLC price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    adx_length : PositiveInt, optional
        ADX lookback window, by default 14.
    choppiness_length : PositiveInt, optional
        Choppiness Index lookback window, by default 14.
    adx_trend_threshold : PositiveFloat, optional
        ADX cutoff for a trending bar; half this value is the weak-trend
        cutoff, by default 25.0.
    choppiness_range_threshold : PositiveFloat, optional
        Choppiness cutoff for a ranging bar, by default 61.8.

    Returns
    -------
    OBBject[list[RegimeData]]
        Per-bar regime labels with the underlying ADX and Choppiness
        readings and a flag marking regime transitions.
    """
    import pandas as pd
    import pandas_ta as ta  # noqa: F401

    params = RegimeQueryParams(
        data=data,
        index=index,
        adx_length=adx_length,
        choppiness_length=choppiness_length,
        adx_trend_threshold=adx_trend_threshold,
        choppiness_range_threshold=choppiness_range_threshold,
    )
    validate_data(params.data, [params.adx_length, params.choppiness_length])
    df = basemodel_to_df(params.data, index=params.index)
    adx_df = df.ta.adx(length=params.adx_length)
    adx_series = adx_df[f"ADX_{params.adx_length}"]
    chop_series = df.ta.chop(length=params.choppiness_length).rename("choppiness")

    combined = pd.DataFrame(
        {
            "adx": adx_series,
            "choppiness": chop_series,
        }
    )
    out = combined.reset_index().rename(columns={params.index: "date"})

    results: list[RegimeData] = []
    prev_regime: Regime | None = None
    for row in out.to_dict(orient="records"):
        adx_val = row["adx"]
        chop_val = row["choppiness"]
        adx_clean = None if (adx_val is None or pd.isna(adx_val)) else float(adx_val)
        chop_clean = (
            None if (chop_val is None or pd.isna(chop_val)) else float(chop_val)
        )
        label = _classify(
            adx_clean,
            chop_clean,
            params.adx_trend_threshold,
            params.choppiness_range_threshold,
        )
        changed = prev_regime is not None and label != prev_regime
        results.append(
            RegimeData(
                date=row["date"],
                adx=adx_clean,
                choppiness=chop_clean,
                regime=label,
                regime_changed=changed,
            )
        )
        prev_regime = label
    # Per-endpoint Data subclass; return annotation uses base Data for
    # static-package compatibility (list invariance prevents subtype matching).
    return OBBject(results=results)  # ty: ignore[invalid-return-type]


__all__ = [
    "Regime",
    "RegimeData",
    "RegimeQueryParams",
    "regime",
    "router",
]
