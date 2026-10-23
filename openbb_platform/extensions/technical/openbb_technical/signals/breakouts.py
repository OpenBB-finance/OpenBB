"""Channel-breakout signals."""

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
from pydantic import Field, PositiveFloat, PositiveInt

from openbb_technical.helpers import validate_data

# Bare 'date' alias for function signatures so the static-package builder
# writes 'date' (which it imports from datetime) rather than 'dateType' which it does not.
date = dateType


router = Router(prefix="", description="Channel-breakout signals.")


BreakoutMethod = Literal["donchian", "bollinger"]


class BreakoutsQueryParams(QueryParams):
    """Query parameters for the channel-breakouts endpoint.

    Parameters
    ----------
    data : list[Data]
        Input OHLC price series.
    index : str, optional
        Index column name in ``data``, by default ``"date"``.
    method : {"donchian", "bollinger"}, optional
        Channel definition. ``donchian`` uses the rolling high/low envelope;
        ``bollinger`` uses the rolling mean plus or minus ``band_std``
        standard deviations. Default is ``"donchian"``.
    length : PositiveInt, optional
        Lookback window for the channel, by default 20.
    band_std : PositiveFloat, optional
        Bollinger band multiplier. Ignored for ``donchian``. ``None``
        resolves to 2.0 when ``method='bollinger'``.
    """

    __category__ = "signal"
    __output_columns__ = (
        "date",
        "direction",
        "price",
        "band",
        "magnitude",
        "bars_in_range",
    )

    data: list[Data] = Field(description="Input OHLC price series.")
    index: str = Field(default="date", description="Index column name in ``data``.")
    method: BreakoutMethod = Field(
        default="donchian",
        description=(
            "Channel definition: Donchian (rolling high/low) or Bollinger "
            "(mean +/- ``band_std`` * stdev)."
        ),
    )
    length: PositiveInt = Field(
        default=20, description="Lookback window for the channel."
    )
    band_std: PositiveFloat | None = Field(
        default=None,
        description=(
            "Bollinger band multiplier. Ignored for ``donchian``. ``None`` "
            "resolves to 2.0 when ``method='bollinger'``."
        ),
    )


class BreakoutEvent(Data):
    """One row per breakout bar.

    Parameters
    ----------
    date : date | str
        Bar on which the breakout occurred.
    direction : {"upside", "downside"}
        Which band was crossed.
    price : float
        Close price on the breakout bar.
    band : float
        Previous bar's band level that was breached.
    magnitude : float
        Signed distance ``price - band``. Positive for upside breakouts;
        negative for downside breakouts.
    bars_in_range : int
        Bars elapsed since the most recent breakout in either direction.
    """

    date: datetime | dateType | str = Field(
        description="Bar on which the breakout occurred."
    )
    direction: Literal["upside", "downside"] = Field(
        description="Which band was crossed.",
    )
    price: float = Field(description="Close price on the breakout bar.")
    band: float = Field(description="Previous bar's band level that was breached.")
    magnitude: float = Field(
        description="Signed distance: ``price - band``. Positive for upside, negative for downside.",
    )
    bars_in_range: int = Field(
        description="Bars since the most recent breakout (in either direction).",
    )


def _channel_bands(df, method: str, length: int, band_std: float | None):
    """Return ``(upper_band, lower_band)`` Series aligned to ``df.index``."""
    import pandas_ta as ta  # noqa: F401

    if method == "donchian":
        dc = df.ta.donchian(lower_length=length, upper_length=length)
        upper = dc[f"DCU_{length}_{length}"]
        lower = dc[f"DCL_{length}_{length}"]
        return upper, lower
    std = band_std if band_std is not None else 2.0
    bb = df.ta.bbands(length=length, std=std)
    bbu_col = next(c for c in bb.columns if c.startswith("BBU_"))
    bbl_col = next(c for c in bb.columns if c.startswith("BBL_"))
    return bb[bbu_col], bb[bbl_col]


@router.command(
    methods=["POST"],
    examples=[
        APIEx(
            parameters={
                "data": APIEx.mock_data("timeseries"),
                "method": "donchian",
                "length": 20,
            },
        ),
    ],
)
def breakouts(params: BreakoutsQueryParams) -> OBBject[list[BreakoutEvent]]:
    """Detect channel breakouts where price closes beyond a rolling envelope."""
    validate_data(params.data, [params.length])
    df = basemodel_to_df(params.data, index=params.index)

    upper, lower = _channel_bands(df, params.method, params.length, params.band_std)
    prev_upper = upper.shift(1)
    prev_lower = lower.shift(1)
    close = df["close"].astype(float)

    up_break = close > prev_upper
    dn_break = close < prev_lower

    events: list[dict] = []
    last_event_pos: int | None = None
    dates = df.index.tolist()

    for i, dt in enumerate(dates):
        is_up = bool(up_break.iloc[i])
        is_dn = bool(dn_break.iloc[i])
        if not is_up and not is_dn:
            continue
        direction = "upside" if is_up else "downside"
        band = float(prev_upper.iloc[i] if is_up else prev_lower.iloc[i])
        price = float(close.iloc[i])
        magnitude = price - band
        bars_in_range = i if last_event_pos is None else i - last_event_pos
        events.append(
            {
                "date": dt,
                "direction": direction,
                "price": price,
                "band": band,
                "magnitude": magnitude,
                "bars_in_range": int(bars_in_range),
            }
        )
        last_event_pos = i

    return OBBject(results=[BreakoutEvent(**row) for row in events])


__all__ = [
    "BreakoutEvent",
    "BreakoutMethod",
    "BreakoutsQueryParams",
    "breakouts",
    "router",
]
