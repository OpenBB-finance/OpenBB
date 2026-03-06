"""HMM-based macro regime classifier."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

try:
    from hmmlearn.hmm import GaussianHMM
except Exception:  # noqa: BLE001
    GaussianHMM = None

REGIME_LABELS = (
    "Risk-On / Bull",
    "Risk-Off / Crisis",
    "Stagflation",
    "Liquidity Crunch",
    "Transitional",
)


def _auto_label_state(mean_row: np.ndarray, axes: list[str]) -> str:
    score = {axis: float(mean_row[idx]) for idx, axis in enumerate(axes)}
    risk_on = score.get("risk_on_score", 50.0)
    growth = score.get("growth_score", 50.0)
    inflation = score.get("inflation_score", 50.0)
    liquidity = score.get("liquidity_score", 50.0)
    credit_stress = score.get("credit_stress_score", 50.0)
    if risk_on >= 60.0 and growth >= 60.0:
        return "Risk-On / Bull"
    if risk_on < 40.0 and credit_stress > 60.0:
        return "Risk-Off / Crisis"
    if inflation > 70.0 and growth < 40.0:
        return "Stagflation"
    if liquidity < 40.0:
        return "Liquidity Crunch"
    return "Transitional"


def fit_hmm_regime(
    scores: pd.DataFrame,
    n_states: int = 4,
    n_iter: int = 200,
    random_state: int = 42,
) -> dict[str, Any] | None:
    """Fit Gaussian HMM on score frame and return state sequence + metadata."""
    if GaussianHMM is None:
        return None
    if scores.empty:
        return None
    frame = scores.copy().dropna(how="any")
    if frame.empty:
        return None
    n_components = max(2, min(int(n_states), 8))
    model = GaussianHMM(
        n_components=n_components,
        covariance_type="full",
        n_iter=max(10, int(n_iter)),
        random_state=int(random_state),
    )
    X = frame.to_numpy(dtype=float)
    model.fit(X)
    state_seq = model.predict(X)
    proba_seq = model.predict_proba(X)
    axes = list(frame.columns)
    state_meta: dict[int, dict[str, Any]] = {}
    for state_idx in range(n_components):
        mean_row = np.asarray(model.means_[state_idx], dtype=float)
        label = _auto_label_state(mean_row, axes)
        state_meta[state_idx] = {
            "label": label,
            "means": {axis: float(mean_row[i]) for i, axis in enumerate(axes)},
        }

    return {
        "index": frame.index,
        "states": state_seq,
        "probabilities": proba_seq,
        "state_meta": state_meta,
    }
