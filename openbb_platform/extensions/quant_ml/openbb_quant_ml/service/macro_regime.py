"""Macro regime score computation."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date

import numpy as np
import pandas as pd

from openbb_quant_ml.service.macro_constants import load_macro_config
from openbb_quant_ml.service.macro_expression import evaluate_expression
from openbb_quant_ml.service.macro_transforms import apply_transform, resample_series

SeriesResolver = Callable[[str], pd.Series]


def _sigmoid_score(value: pd.Series) -> pd.Series:
    clipped = value.clip(lower=-6, upper=6)
    return 100.0 / (1.0 + np.exp(-clipped))


def compute_regime_scores(
    resolver: SeriesResolver,
    start: date | None = None,
    end: date | None = None,
    freq: str = "W",
    fill: str = "ffill",
) -> pd.DataFrame:
    """Return dataframe with five regime scores (0..100)."""
    cfg = load_macro_config()
    weight_cfg = cfg.get("regime_weights", {}) or {}
    out: dict[str, pd.Series] = {}
    for axis in [
        "risk_on_score",
        "inflation_score",
        "growth_score",
        "liquidity_score",
        "credit_stress_score",
    ]:
        components = weight_cfg.get(axis, []) or []
        aggregate: pd.Series | None = None
        for component in components:
            key = str(component.get("key", "")).strip()
            transform = str(component.get("transform", "level")).strip().lower()
            weight = float(component.get("weight", 0.0))
            if not key:
                continue
            evaluated = evaluate_expression(key, resolver=resolver).series
            if transform:
                evaluated = apply_transform(evaluated, transform)  # type: ignore[arg-type]
            evaluated = resample_series(evaluated, freq=freq if freq in {"D", "W", "M", "Q"} else "W", fill=fill, start=start, end=end)
            weighted = evaluated * weight
            aggregate = weighted if aggregate is None else aggregate.add(weighted, fill_value=0.0)
        if aggregate is None or aggregate.empty:
            out[axis] = pd.Series(dtype=float)
        else:
            out[axis] = _sigmoid_score(aggregate)

    if not out:
        return pd.DataFrame()
    frame = pd.DataFrame(out).sort_index()
    frame = frame.dropna(how="all")
    return frame


def classify_regime_label(row: pd.Series | dict[str, float]) -> str:
    """Classify one 5-axis score row to a human-readable regime label."""
    risk_on = float(row.get("risk_on_score", 50.0))
    inflation = float(row.get("inflation_score", 50.0))
    growth = float(row.get("growth_score", 50.0))
    liquidity = float(row.get("liquidity_score", 50.0))
    credit_stress = float(row.get("credit_stress_score", 50.0))
    if risk_on >= 60.0 and growth >= 60.0:
        return "Risk-On / Bull"
    if risk_on < 40.0 and credit_stress > 60.0:
        return "Risk-Off / Crisis"
    if inflation > 70.0 and growth < 40.0:
        return "Stagflation"
    if liquidity < 40.0:
        return "Liquidity Crunch"
    return "Transitional"


def detect_regime_transitions(
    frame: pd.DataFrame,
    threshold: float = 10.0,
) -> pd.DataFrame:
    """Return axis-level transition rows where score delta exceeds threshold."""
    if frame.empty:
        return pd.DataFrame(
            columns=[
                "date",
                "axis",
                "from_score",
                "to_score",
                "delta",
                "direction",
                "severity",
            ]
        )
    axes = [
        "risk_on_score",
        "inflation_score",
        "growth_score",
        "liquidity_score",
        "credit_stress_score",
    ]
    rows: list[dict[str, float | str]] = []
    threshold_abs = float(abs(threshold))
    for axis in axes:
        if axis not in frame.columns:
            continue
        prev = frame[axis].shift(1)
        delta = frame[axis] - prev
        changed = delta.abs() >= threshold_abs
        for idx in frame.index[changed.fillna(False)]:
            from_score = float(prev.loc[idx]) if pd.notna(prev.loc[idx]) else 0.0
            to_score = float(frame.at[idx, axis]) if pd.notna(frame.at[idx, axis]) else 0.0
            delta_value = to_score - from_score
            rows.append(
                {
                    "date": pd.Timestamp(idx).date().isoformat(),
                    "axis": axis,
                    "from_score": from_score,
                    "to_score": to_score,
                    "delta": delta_value,
                    "direction": "rising" if delta_value >= 0 else "falling",
                    "severity": "major" if abs(delta_value) >= 20.0 else "minor",
                }
            )
    if not rows:
        return pd.DataFrame(
            columns=[
                "date",
                "axis",
                "from_score",
                "to_score",
                "delta",
                "direction",
                "severity",
            ]
        )
    out = pd.DataFrame(rows)
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out = out.sort_values(["date", "axis"]).reset_index(drop=True)
    out["date"] = out["date"].dt.date.astype(str)
    return out
