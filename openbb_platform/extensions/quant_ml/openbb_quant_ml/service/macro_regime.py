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
