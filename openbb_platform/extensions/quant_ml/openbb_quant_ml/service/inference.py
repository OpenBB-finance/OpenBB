"""Incremental inference refresh for persisted ranker artifacts."""

from __future__ import annotations

import pickle
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from openbb_quant_ml.models import ModelName, TrainRequest
from openbb_quant_ml.service.data_loader import load_market_data
from openbb_quant_ml.service.feature_engineering import build_feature_dataset
from openbb_quant_ml.service.storage import get_run_dir, load_json, save_json
from openbb_quant_ml.service.universe import (
    get_default_symbols,
    get_symbols_for_universe,
)


class InferenceArtifactMissingError(RuntimeError):
    """Raised when inference-only artifacts are missing for a run."""


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        casted = float(value)
    except (TypeError, ValueError):
        return default
    if np.isnan(casted) or np.isinf(casted):
        return default
    return casted


def _load_training_request(run_dir: Path) -> TrainRequest:
    payload = load_json(run_dir / "config.json", default={})
    if not isinstance(payload, dict):
        raise ValueError("Training config artifact is invalid.")
    request_payload = payload.get("request", {})
    if not isinstance(request_payload, dict):
        raise ValueError("Training request payload is missing in config artifact.")
    return TrainRequest(**request_payload)


def _resolve_symbols(request: TrainRequest) -> list[str]:
    if request.symbols:
        return sorted(
            {
                str(symbol).strip().upper()
                for symbol in request.symbols
                if str(symbol).strip()
            }
        )
    if request.universe_id:
        return get_symbols_for_universe(request.universe_id)
    return get_default_symbols()


def _load_ranker_model_artifacts(run_dir: Path) -> tuple[Any, dict[str, Any]]:
    model_path = run_dir / "model_lgbm_ranker.pkl"
    meta_path = run_dir / "model_lgbm_ranker_meta.json"
    if not model_path.exists() or not meta_path.exists():
        raise InferenceArtifactMissingError(
            "Ranker inference artifacts are missing (model_lgbm_ranker.pkl/model_lgbm_ranker_meta.json)."
        )

    with model_path.open("rb") as file:
        model = pickle.load(file)  # noqa: S301

    metadata = load_json(meta_path, default={})
    if not isinstance(metadata, dict):
        raise InferenceArtifactMissingError(
            "Ranker model metadata artifact is invalid."
        )
    return model, metadata


def _score_latest_frame(
    latest_frame: pd.DataFrame,
    *,
    model: Any,
    metadata: dict[str, Any],
) -> pd.DataFrame:
    feature_columns = [
        str(column).strip()
        for column in metadata.get("feature_columns", [])
        if str(column).strip()
    ]
    if not feature_columns:
        raise InferenceArtifactMissingError(
            "feature_columns are missing in ranker metadata."
        )

    working = latest_frame.copy()
    for column in feature_columns:
        if column not in working.columns:
            working[column] = 0.0

    x_input = working[feature_columns].fillna(0.0).to_numpy(dtype=float)
    scores = np.asarray(model.predict(x_input), dtype=float).reshape(-1)
    if scores.shape[0] != len(working):
        raise ValueError("Inference output shape does not match latest feature frame.")

    label_return_map_raw = metadata.get("label_return_map", {})
    label_return_map: dict[int, float] = {}
    if isinstance(label_return_map_raw, dict):
        for key, value in label_return_map_raw.items():
            try:
                label_key = int(key)
            except (TypeError, ValueError):
                continue
            label_return_map[label_key] = _coerce_float(value, default=0.0)
    label_return_fallback = _coerce_float(
        metadata.get("label_return_fallback", 0.0),
        default=0.0,
    )

    score_series = pd.Series(scores, index=working.index, dtype=float)
    percentile = score_series.rank(method="first", pct=True)
    labels = np.floor(np.clip((percentile - 1e-12) * 5.0, 0.0, 4.999)).astype(int)
    predicted_return = labels.map(
        lambda label: float(label_return_map.get(int(label), label_return_fallback))
    )

    if "close" not in working.columns:
        working["close"] = np.nan
    if "daily_return" not in working.columns:
        working["daily_return"] = np.nan
    if "target_return" not in working.columns:
        working["target_return"] = np.nan

    scored = working[
        ["date", "symbol", "close", "daily_return", "target_return"]
    ].copy()
    scored["score"] = score_series.astype(float)
    scored["label"] = labels.astype(int)
    scored["predicted_return"] = predicted_return.astype(float)
    scored["predicted_xgb"] = scored["score"]
    scored["predicted_lstm"] = scored["score"]
    scored["date"] = pd.to_datetime(scored["date"]).dt.tz_localize(None)
    return scored.sort_values(["date", "symbol"]).reset_index(drop=True)


def _write_market_data_artifact(
    run_dir: Path, datasets: dict[str, pd.DataFrame]
) -> None:
    rows: list[pd.DataFrame] = []
    for symbol, frame in datasets.items():
        if frame.empty:
            continue
        local = frame.copy()
        if "open" not in local.columns:
            local["open"] = local.get("close")
        keep = ["date", "open", "close"]
        for column in keep:
            if column not in local.columns:
                local[column] = np.nan
        local = local[keep]
        local["symbol"] = symbol
        rows.append(local[["date", "symbol", "open", "close"]])

    if not rows:
        return

    market_long = pd.concat(rows, ignore_index=True)
    market_long["date"] = pd.to_datetime(market_long["date"]).dt.tz_localize(None)
    market_long = market_long.sort_values(["date", "symbol"])
    market_long = market_long.drop_duplicates(subset=["date", "symbol"], keep="last")
    market_long.to_parquet(run_dir / "market_data.parquet", index=False)


def _upsert_predictions(
    run_dir: Path, model_name: ModelName, scored_latest: pd.DataFrame
) -> pd.DataFrame:
    predictions_path = run_dir / f"predictions_{model_name}.parquet"
    existing = pd.DataFrame()
    if predictions_path.exists():
        existing = pd.read_parquet(predictions_path)
        if not existing.empty:
            existing["date"] = pd.to_datetime(existing["date"]).dt.tz_localize(None)

    merged = pd.concat([existing, scored_latest], ignore_index=True, sort=False)
    merged["date"] = pd.to_datetime(merged["date"]).dt.tz_localize(None)
    merged = merged.sort_values(["date", "symbol"])
    merged = merged.drop_duplicates(subset=["date", "symbol"], keep="last")
    merged.to_parquet(predictions_path, index=False)
    if model_name == "lgbm_ranker":
        merged.to_parquet(run_dir / "predictions.parquet", index=False)
    return merged


def refresh_latest_ranker_predictions(
    run_id: str,
    *,
    model_name: ModelName = "lgbm_ranker",
    lookback_years: int = 3,
) -> dict[str, Any]:
    """Refresh latest-day predictions for an already-trained ranker run."""
    resolved_run_id = str(run_id).strip()
    if not resolved_run_id:
        raise ValueError("run_id is required for inference refresh.")
    if model_name != "lgbm_ranker":
        raise ValueError(
            "infer_only mode currently supports model_name=lgbm_ranker only."
        )

    run_dir = get_run_dir(resolved_run_id)
    if not run_dir.exists():
        raise ValueError(f"Run directory not found: {resolved_run_id}")

    request = _load_training_request(run_dir)
    symbols = _resolve_symbols(request)
    if not symbols:
        raise ValueError("No symbols available for inference refresh.")

    lookback = max(1, int(lookback_years))
    lookback_start = date.today() - timedelta(days=365 * lookback)
    start_date = max(request.date_range.start_date, lookback_start)
    end_date = date.today()

    datasets, skipped = load_market_data(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
    )
    if not datasets:
        raise ValueError("No market datasets loaded for inference refresh.")

    feature_data, _, skipped_feature_symbols = build_feature_dataset(
        data_by_symbol=datasets,
        feature_config=request.feature_parameters,
        horizon_days=request.horizon_days,
        target_mode=request.target_mode,
        close_to_next_open_horizon_policy=request.close_to_next_open_horizon_policy,
        include_macro_features=request.include_macro_features,
        macro_feature_subset=request.macro_feature_subset,
    )
    if feature_data.empty:
        raise ValueError("Feature dataset is empty for inference refresh.")

    latest_timestamp = pd.Timestamp(feature_data["date"].max())
    if latest_timestamp.tzinfo is not None:
        latest_timestamp = latest_timestamp.tz_convert(None)
    latest_frame = feature_data[feature_data["date"] == latest_timestamp].copy()
    if latest_frame.empty:
        raise ValueError("No latest date feature rows found for inference refresh.")

    model, metadata = _load_ranker_model_artifacts(run_dir)
    scored_latest = _score_latest_frame(
        latest_frame,
        model=model,
        metadata=metadata,
    )
    merged_predictions = _upsert_predictions(run_dir, model_name, scored_latest)
    _write_market_data_artifact(run_dir, datasets)

    payload = {
        "status": "ok",
        "run_id": resolved_run_id,
        "model_name": model_name,
        "as_of_date": latest_timestamp.date().isoformat(),
        "lookback_years": lookback,
        "symbols_requested": len(symbols),
        "symbols_loaded": len(datasets),
        "symbols_skipped_data": len(skipped),
        "symbols_skipped_features": len(skipped_feature_symbols),
        "latest_rows_upserted": int(len(scored_latest)),
        "predictions_total_rows": int(len(merged_predictions)),
    }
    save_json(run_dir / "inference_latest.json", payload)
    return payload
