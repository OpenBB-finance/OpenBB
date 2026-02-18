"""Preset builders for macro tab composite workflows."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from openbb_quant_ml.macro_models import (
    MacroDataPoint,
    MacroEventItem,
    MacroPresetResponse,
    MacroPresetSeries,
    MacroSeriesMeta,
    MacroSeriesStats,
)
from openbb_quant_ml.service.macro_expression import evaluate_expression
from openbb_quant_ml.service.macro_transforms import compute_stats, infer_frequency_label, resample_series

Resolver = Callable[[str], pd.Series]


def _safe_float_or_none(value: Any) -> float | None:
    """Convert NaN/inf to None for JSON-safe payloads."""
    if value is None:
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(out):
        return None
    return out


def _series_to_points(series: pd.Series) -> list[MacroDataPoint]:
    clean = series.dropna().sort_index()
    return [MacroDataPoint(date=idx.date().isoformat(), value=float(value)) for idx, value in clean.items()]


def _stats_to_model(stats: dict[str, float | None]) -> MacroSeriesStats:
    return MacroSeriesStats(
        last=_safe_float_or_none(stats.get("last")),
        change_1m=_safe_float_or_none(stats.get("change_1m")),
        change_3m=_safe_float_or_none(stats.get("change_3m")),
        z=_safe_float_or_none(stats.get("z")),
        percentile_5y=_safe_float_or_none(stats.get("percentile_5y")),
    )


def _build_ratio_expr(adjust_units: bool, scale: float) -> str:
    if adjust_units:
        return f"((HG/16)/(GC*0.911458))*{float(scale)}"
    return f"(HG/GC)*{float(scale)}"


def _rolling_slope(series: pd.Series, window: int) -> pd.Series:
    window_safe = max(2, int(window))

    def _slope(raw_values: np.ndarray) -> float:
        y = np.asarray(raw_values, dtype=float)
        finite = np.isfinite(y)
        if finite.sum() < max(3, window_safe // 3):
            return np.nan
        x = np.arange(len(y), dtype=float)[finite]
        yv = y[finite]
        x_centered = x - float(x.mean())
        denom = float((x_centered**2).sum())
        if denom <= 0:
            return np.nan
        y_centered = yv - float(yv.mean())
        return float((x_centered * y_centered).sum() / denom)

    return series.rolling(window_safe, min_periods=max(3, window_safe // 2)).apply(_slope, raw=True)


def _detect_divergence_events(
    slope_ratio: pd.Series,
    slope_yield: pd.Series,
    corr: pd.Series | None,
    min_weeks: int,
) -> list[MacroEventItem]:
    if slope_ratio.empty or slope_yield.empty:
        return []

    min_weeks_safe = max(1, int(min_weeks))
    left, right = slope_ratio.align(slope_yield, join="outer")
    frame = pd.DataFrame({"slope_ratio": left, "slope_yield": right}).sort_index()
    if corr is not None:
        frame["corr"] = corr.reindex(frame.index)

    sign_ratio = np.sign(frame["slope_ratio"])
    sign_yield = np.sign(frame["slope_yield"])
    opposite = (sign_ratio * sign_yield) < 0

    events: list[MacroEventItem] = []
    run_start: pd.Timestamp | None = None
    run_end: pd.Timestamp | None = None
    run_len = 0

    def _emit_event() -> None:
        if run_start is None or run_end is None or run_len < min_weeks_safe:
            return
        row = frame.loc[run_end]
        sr = _safe_float_or_none(row["slope_ratio"])
        sy = _safe_float_or_none(row["slope_yield"])
        if sr is None or sy is None:
            return
        event_type = "ratio_up_yield_down" if sr > 0 and sy < 0 else "ratio_down_yield_up"
        details: dict[str, float | str] = {
            "duration_weeks": float(run_len),
            "slope_ratio_last": sr,
            "slope_yield_last": sy,
        }
        corr_value = _safe_float_or_none(row.get("corr"))
        if corr_value is not None:
            details["corr_last"] = corr_value
        events.append(
            MacroEventItem(
                date=pd.Timestamp(run_start).date().isoformat(),
                event_type=event_type,
                details=details,
            )
        )

    for idx, is_opposite in opposite.items():
        if bool(is_opposite):
            run_start = pd.Timestamp(idx) if run_start is None else run_start
            run_end = pd.Timestamp(idx)
            run_len += 1
            continue
        _emit_event()
        run_start = None
        run_end = None
        run_len = 0
    _emit_event()
    return events


def _to_preset_series(
    series_id: str,
    axis: str,
    series: pd.Series,
    title: str,
    source: str,
    units: str | None = None,
) -> MacroPresetSeries:
    stats = compute_stats(series)
    return MacroPresetSeries(
        id=series_id,
        axis=axis,  # type: ignore[arg-type]
        meta=MacroSeriesMeta(
            key=series_id,
            title=title,
            units=units,
            frequency=infer_frequency_label(series) if not series.empty else None,
            source=source,
            transform="level",
        ),
        data=_series_to_points(series),
        stats=_stats_to_model(stats),
    )


def get_copper_gold_preset_response(
    resolver: Resolver,
    *,
    start: date | None = None,
    end: date | None = None,
    freq: str = "W",
    fill: str = "ffill",
    scale: float = 1000.0,
    adjust_units: bool = True,
    yield_key: str = "FRED:DGS10",
    corr_window: int = 52,
    slope_window: int = 13,
    divergence_min_weeks: int = 4,
    include_corr: bool = True,
) -> MacroPresetResponse:
    inputs: dict[str, str | float | bool] = {
        "freq": str(freq),
        "fill": str(fill),
        "scale": float(scale),
        "adjust_units": bool(adjust_units),
        "yield_key": str(yield_key),
        "corr_window": float(corr_window),
        "slope_window": float(slope_window),
        "divergence_min_weeks": float(divergence_min_weeks),
        "include_corr": bool(include_corr),
    }
    ratio_expr = _build_ratio_expr(adjust_units=adjust_units, scale=scale)
    inputs["ratio_expr"] = ratio_expr

    try:
        ratio_raw = evaluate_expression(ratio_expr, resolver=resolver).series
        yield_raw = resolver(yield_key)
    except Exception as exc:  # noqa: BLE001
        return MacroPresetResponse(
            status="insufficient_data",
            message=str(exc),
            preset_id="copper_gold",
            inputs=inputs,
            series=[],
            events=[],
        )

    ratio_series = resample_series(ratio_raw, freq=freq, fill=fill, start=start, end=end)
    yield_series = resample_series(yield_raw, freq=freq, fill=fill, start=start, end=end)
    ratio_aligned, yield_aligned = ratio_series.align(yield_series, join="outer")
    ratio_aligned = ratio_aligned.sort_index().ffill()
    yield_aligned = yield_aligned.sort_index().ffill()

    if ratio_aligned.dropna().empty or yield_aligned.dropna().empty:
        return MacroPresetResponse(
            status="insufficient_data",
            message="No sufficient observations for copper/gold ratio or yield series.",
            preset_id="copper_gold",
            inputs=inputs,
            series=[],
            events=[],
        )

    corr_series: pd.Series | None = None
    if include_corr:
        corr_window_safe = max(2, min(int(corr_window), 520))
        min_periods = max(5, corr_window_safe // 4)
        corr_series = ratio_aligned.rolling(corr_window_safe, min_periods=min_periods).corr(yield_aligned)

    slope_window_safe = max(2, min(int(slope_window), 260))
    slope_ratio = _rolling_slope(ratio_aligned, slope_window_safe)
    slope_yield = _rolling_slope(yield_aligned, slope_window_safe)
    events = _detect_divergence_events(
        slope_ratio=slope_ratio,
        slope_yield=slope_yield,
        corr=corr_series,
        min_weeks=divergence_min_weeks,
    )

    series_payload = [
        _to_preset_series(
            series_id="copper_gold_ratio",
            axis="left",
            series=ratio_aligned,
            title="Copper/Gold Ratio",
            source="preset",
            units="ratio",
        ),
        _to_preset_series(
            series_id="dgs10",
            axis="right",
            series=yield_aligned,
            title="US 10Y Treasury Yield (DGS10)",
            source="FRED",
            units="percent",
        ),
    ]
    if include_corr and corr_series is not None:
        series_payload.append(
            _to_preset_series(
                series_id="rolling_corr",
                axis="bottom",
                series=corr_series,
                title=f"Rolling Corr (window={max(2, min(int(corr_window), 520))})",
                source="derived",
                units="corr",
            )
        )

    return MacroPresetResponse(
        status="ok",
        message=None,
        preset_id="copper_gold",
        inputs=inputs,
        series=series_payload,
        events=events,
    )
