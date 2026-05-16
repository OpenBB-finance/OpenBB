"""Oscillator threshold signals."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Literal

from openbb_core.app.model.example import APIEx
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


router = Router(prefix="", description="Oscillator threshold signals.")


OscillatorIndicator = Literal["rsi", "mfi", "stoch", "williams_r", "cci"]


_DEFAULT_THRESHOLDS: dict[str, tuple[float, float]] = {
    "rsi": (70.0, 30.0),
    "mfi": (80.0, 20.0),
    "stoch": (80.0, 20.0),
    "williams_r": (-20.0, -80.0),
    "cci": (100.0, -100.0),
}


class OscillatorSignalsQueryParams(QueryParams):
    """Query parameters for the oscillator threshold-signals endpoint.

    Parameters
    ----------
    data : list[Data]
        Input OHLC(V) price series.
    target : str, optional
        Price column used for oscillators that take a single series
        (``rsi``, ``cci``), by default ``"close"``.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    indicator : {"rsi", "mfi", "stoch", "williams_r", "cci"}
        Which oscillator to evaluate against its threshold bands.
    length : PositiveInt, optional
        Lookback window for the oscillator, by default 14.
    overbought_threshold : float, optional
        Upper band. ``None`` resolves to the indicator default
        (rsi 70, mfi 80, stoch 80, williams_r -20, cci 100).
    oversold_threshold : float, optional
        Lower band. ``None`` resolves to the indicator default
        (rsi 30, mfi 20, stoch 20, williams_r -80, cci -100).
    """

    __category__ = "signal"
    __output_columns__ = (
        "date",
        "value",
        "regime",
        "crossed_into_overbought",
        "crossed_into_oversold",
        "crossed_out_of_overbought",
        "crossed_out_of_oversold",
    )

    data: list[Data] = Field(description="Input OHLC(V) price series.")
    target: str = Field(
        default="close",
        description="Price column used for oscillators that take a single series (rsi, cci).",
    )
    index: str = Field(default="date", description="Index column name in ``data``.")
    indicator: OscillatorIndicator = Field(
        description="Which oscillator to evaluate against its threshold bands.",
    )
    length: PositiveInt = Field(
        default=14, description="Lookback window for the oscillator."
    )
    overbought_threshold: float | None = Field(
        default=None,
        description=(
            "Upper band. ``None`` resolves to the indicator default "
            "(rsi 70, mfi 80, stoch 80, williams_r -20, cci 100)."
        ),
    )
    oversold_threshold: float | None = Field(
        default=None,
        description=(
            "Lower band. ``None`` resolves to the indicator default "
            "(rsi 30, mfi 20, stoch 20, williams_r -80, cci -100)."
        ),
    )


class OscillatorSignal(Data):
    """One row of the oscillator-signal series.

    Parameters
    ----------
    date : date | str
        Observation date.
    value : float
        Oscillator value on this bar.
    regime : {"overbought", "oversold", "neutral"}
        Region of the oscillator on this bar relative to the configured bands.
    crossed_into_overbought : bool
        ``True`` on the bar the regime first becomes overbought.
    crossed_into_oversold : bool
        ``True`` on the bar the regime first becomes oversold.
    crossed_out_of_overbought : bool
        ``True`` on the bar the regime leaves overbought (to neutral or
        oversold).
    crossed_out_of_oversold : bool
        ``True`` on the bar the regime leaves oversold (to neutral or
        overbought).
    """

    date: datetime | dateType | str = Field(description="Observation date.")
    value: float = Field(description="Oscillator value on this bar.")
    regime: Literal["overbought", "oversold", "neutral"] = Field(
        description="Region of the oscillator on this bar.",
    )
    crossed_into_overbought: bool = Field(
        description="True on the bar the regime first becomes overbought.",
    )
    crossed_into_oversold: bool = Field(
        description="True on the bar the regime first becomes oversold.",
    )
    crossed_out_of_overbought: bool = Field(
        description="True on the bar the regime leaves overbought (to neutral or oversold).",
    )
    crossed_out_of_oversold: bool = Field(
        description="True on the bar the regime leaves oversold (to neutral or overbought).",
    )


def _compute_oscillator(df, indicator: str, length: int, target: str):
    """Dispatch to pandas_ta and return a single-series oscillator."""
    import pandas_ta as ta  # noqa: F401

    if indicator == "rsi":
        return df.ta.rsi(close=df[target], length=length)
    if indicator == "mfi":
        return df.ta.mfi(length=length)
    if indicator == "stoch":
        out = df.ta.stoch(k=length)
        return out.iloc[:, 0]
    if indicator == "williams_r":
        return df.ta.willr(length=length)
    return df.ta.cci(length=length)


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "data": APIEx.mock_data("timeseries"),
                "indicator": "rsi",
                "length": 14,
            },
        ),
    ],
)
def oscillator_signals(
    params: OscillatorSignalsQueryParams,
) -> OBBject[list[OscillatorSignal]]:
    """Label every bar with its oscillator regime and emit crossing events."""
    import pandas as pd

    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)

    ob_default, os_default = _DEFAULT_THRESHOLDS[params.indicator]
    ob = (
        params.overbought_threshold
        if params.overbought_threshold is not None
        else ob_default
    )
    osd = (
        params.oversold_threshold
        if params.oversold_threshold is not None
        else os_default
    )

    raw = _compute_oscillator(df, params.indicator, params.length, params.target)
    series = pd.Series(raw, index=df.index, dtype="float64")

    regime = pd.Series("neutral", index=series.index, dtype="object")
    regime[series >= ob] = "overbought"
    regime[series <= osd] = "oversold"

    prev = regime.shift(1)
    crossed_into_overbought = (regime == "overbought") & (prev != "overbought")
    crossed_into_oversold = (regime == "oversold") & (prev != "oversold")
    crossed_out_of_overbought = (regime != "overbought") & (prev == "overbought")
    crossed_out_of_oversold = (regime != "oversold") & (prev == "oversold")

    for s in (
        crossed_into_overbought,
        crossed_into_oversold,
        crossed_out_of_overbought,
        crossed_out_of_oversold,
    ):
        s.iloc[0] = False

    value = series.fillna(0.0)

    out = (
        pd.DataFrame(
            {
                "value": value.astype(float),
                "regime": regime,
                "crossed_into_overbought": crossed_into_overbought.astype(bool),
                "crossed_into_oversold": crossed_into_oversold.astype(bool),
                "crossed_out_of_overbought": crossed_out_of_overbought.astype(bool),
                "crossed_out_of_oversold": crossed_out_of_oversold.astype(bool),
            }
        )
        .reset_index()
        .rename(columns={params.index: "date"})
    )

    return OBBject(
        results=[OscillatorSignal(**row) for row in out.to_dict(orient="records")]
    )


__all__ = [
    "OscillatorIndicator",
    "OscillatorSignal",
    "OscillatorSignalsQueryParams",
    "oscillator_signals",
    "router",
]
