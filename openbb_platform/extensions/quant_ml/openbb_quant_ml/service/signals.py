"""Signal generation helpers."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd


def generate_signals(
    predictions: pd.DataFrame,
    as_of_date: date | None,
    top_k: int,
    score_threshold: float,
    balanced_long_short: bool = False,
) -> tuple[str, pd.DataFrame]:
    """Generate cross-sectional signals from predictions."""
    if predictions.empty:
        raise ValueError("Prediction table is empty.")

    pred = predictions.copy()
    if "predicted_return" not in pred.columns:
        if "score" in pred.columns:
            pred["predicted_return"] = pd.to_numeric(pred["score"], errors="coerce").fillna(0.0)
        else:
            raise ValueError("predicted_return column is missing.")
    if "predicted_xgb" not in pred.columns:
        pred["predicted_xgb"] = pred["predicted_return"]
    if "predicted_lstm" not in pred.columns:
        pred["predicted_lstm"] = pred["predicted_return"]
    pred["date"] = pd.to_datetime(pred["date"]).dt.tz_localize(None)
    target_date = pd.Timestamp(as_of_date) if as_of_date else pred["date"].max()

    as_of = pred[pred["date"] == target_date].copy()
    if as_of.empty:
        raise ValueError(f"No prediction rows found for selected date: {target_date.date()}")

    mean_pred = as_of["predicted_return"].mean()
    std_pred = as_of["predicted_return"].std(ddof=0)
    std_pred = float(std_pred) if std_pred and not np.isnan(std_pred) else 1e-12
    as_of["z_score"] = (as_of["predicted_return"] - mean_pred) / (std_pred + 1e-12)

    def signal_side(z_score: float) -> str:
        if z_score >= 0.5:
            return "buy"
        if z_score <= -0.5:
            return "sell"
        return "hold"

    as_of["side"] = as_of["z_score"].map(signal_side)
    agreement = np.sign(as_of["predicted_xgb"]) == np.sign(as_of["predicted_lstm"])
    as_of["model_agreement"] = agreement.astype(float)
    abs_norm = as_of["predicted_return"].abs()
    abs_scale = abs_norm.max() if abs_norm.max() > 0 else 1.0
    as_of["pred_norm"] = abs_norm / abs_scale
    as_of["confidence"] = (0.6 * as_of["model_agreement"] + 0.4 * as_of["pred_norm"]).clip(0.0, 1.0)

    def reason_codes(row: pd.Series) -> list[str]:
        reasons: list[str] = []
        if row["z_score"] >= 0.5:
            reasons.append("zscore_high")
        elif row["z_score"] <= -0.5:
            reasons.append("zscore_low")
        else:
            reasons.append("zscore_neutral")
        if row["model_agreement"] > 0:
            reasons.append("models_agree")
        else:
            reasons.append("models_diverge")
        if abs(row["predicted_return"]) >= 0.002:
            reasons.append("magnitude_strong")
        return reasons

    as_of["reason_codes"] = as_of.apply(reason_codes, axis=1)
    filtered = as_of[as_of["z_score"].abs() >= score_threshold].copy()
    if filtered.empty:
        filtered = as_of.copy()

    filtered = filtered.sort_values("z_score", ascending=False)
    top_k = max(int(top_k), 1)
    if balanced_long_short and top_k > 1:
        long_count = max(1, top_k // 2)
        short_count = max(1, top_k - long_count)
        longs = filtered[filtered["z_score"] >= 0].head(long_count)
        shorts = filtered[filtered["z_score"] < 0].sort_values("z_score", ascending=True).head(short_count)
        combined = pd.concat([longs, shorts], ignore_index=False)
        if len(combined) < top_k:
            remaining = filtered.loc[~filtered.index.isin(combined.index)].head(top_k - len(combined))
            combined = pd.concat([combined, remaining], ignore_index=False)
        filtered = combined.sort_values("z_score", ascending=False).head(top_k).reset_index(drop=True)
    else:
        filtered = filtered.head(top_k).reset_index(drop=True)

    result = filtered[
        [
            "symbol",
            "side",
            "predicted_return",
            "confidence",
            "reason_codes",
            "z_score",
            "predicted_xgb",
            "predicted_lstm",
        ]
    ].copy()
    return target_date.date().isoformat(), result
