"""Signal contract schema builder and validator."""

from __future__ import annotations

from typing import Any

import pandas as pd

REQUIRED_SIGNAL_COLUMNS: tuple[str, ...] = (
    "date",
    "ticker",
    "raw_pred",
    "score",
    "rank",
    "zscore",
    "confidence",
    "model_version",
    "feature_set_version",
)


def validate_signal_contract(frame: pd.DataFrame) -> None:
    """Validate signal contract columns."""
    missing = [col for col in REQUIRED_SIGNAL_COLUMNS if col not in frame.columns]
    if missing:
        raise ValueError(f"signal_contract_missing_columns: {', '.join(missing)}")


def build_signal_contract(
    *,
    signal_rows: pd.DataFrame,
    as_of_date: str,
    model_version: str,
    feature_set_version: str,
) -> pd.DataFrame:
    """Build normalized signal frame with fixed schema."""
    if signal_rows.empty:
        out = pd.DataFrame(columns=list(REQUIRED_SIGNAL_COLUMNS))
        validate_signal_contract(out)
        return out

    work = signal_rows.copy()
    work["ticker"] = work.get("symbol", pd.Series(dtype=str)).astype(str).str.upper()
    raw = pd.to_numeric(
        work.get("predicted_return", work.get("score", 0.0)), errors="coerce"
    ).fillna(0.0)
    work["raw_pred"] = raw.astype(float)
    work["score"] = raw.astype(float)
    if "z_score" in work.columns:
        work["zscore"] = pd.to_numeric(work["z_score"], errors="coerce").fillna(0.0)
    else:
        std = float(raw.std(ddof=0))
        mean = float(raw.mean())
        work["zscore"] = 0.0 if std <= 0 else ((raw - mean) / (std + 1e-12))
    work["confidence"] = pd.to_numeric(
        work.get("confidence", 0.0), errors="coerce"
    ).fillna(0.0)
    work = work.sort_values(["score", "ticker"], ascending=[False, True]).reset_index(
        drop=True
    )
    work["rank"] = (work.index + 1).astype(int)
    work["date"] = str(as_of_date)
    work["model_version"] = str(model_version)
    work["feature_set_version"] = str(feature_set_version)

    out = work[list(REQUIRED_SIGNAL_COLUMNS)].copy()
    validate_signal_contract(out)
    return out


def infer_model_version(metrics_payload: dict[str, Any]) -> str:
    """Build compact model version token from metrics payload."""
    if not isinstance(metrics_payload, dict):
        return "unknown"
    meta = metrics_payload.get("model_meta", {})
    if isinstance(meta, dict):
        for key in ("model_hash", "artifact_hash", "version"):
            token = str(meta.get(key, "")).strip()
            if token:
                return token
    params = metrics_payload.get("params", {})
    if isinstance(params, dict):
        token = str(params.get("version", "")).strip()
        if token:
            return token
    return "unknown"

