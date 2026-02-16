"""Pipeline orchestration for quant training, signals, and backtests."""

from __future__ import annotations

import traceback
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
import re
import time
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from openbb_quant_ml.models import (
    ArtifactSummaryResponse,
    AssetClassWeightItem,
    BacktestRequest,
    BacktestResponse,
    FeatureImportanceResponse,
    ModelICPoint,
    ModelICResponse,
    ModelName,
    ModelPerformanceItem,
    ModelPerformanceResponse,
    ModelRegimeResponse,
    PortfolioCurrentResponse,
    PortfolioRationale,
    PortfolioSymbolWeightItem,
    PredictionsLatestResponse,
    RunStatusResponse,
    SignalRequest,
    SignalResponse,
    TrainRequest,
    TrainResponse,
    UniverseResponse,
)
from openbb_quant_ml.service.backtest import run_backtest
from openbb_quant_ml.service.cache_registry import get_data_versions, get_feature_versions
from openbb_quant_ml.service.data_loader import build_close_panel, build_price_panel, load_market_data
from openbb_quant_ml.service.dashboard_metrics import (
    get_performance_regime as get_dashboard_performance_regime,
    refresh_alerts_for_run,
)
from openbb_quant_ml.service.feature_engineering import build_feature_dataset
from openbb_quant_ml.service.modeling import train_hybrid_models
from openbb_quant_ml.service.ranker_modeling import train_ranker_models
from openbb_quant_ml.service.run_registry import (
    append_log,
    create_run,
    get_run_state,
    get_run_state_dict,
    initialize_registry,
    update_run,
)
from openbb_quant_ml.service.signals import generate_signals
from openbb_quant_ml.service.storage import get_run_dir, list_run_artifacts, load_json, save_json
from openbb_quant_ml.service.universe import (
    get_default_symbols,
    get_symbols_for_universe,
    get_universe_size_status,
    list_universe_ids,
    load_universe_config,
)

DEFAULT_MODEL: ModelName = "lgbm_ranker"
SUPPORTED_MODELS: tuple[ModelName, ...] = ("xgb_lstm", "lgbm_ranker")

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="quant-ml")
_FUTURES: dict[str, Future] = {}
STALE_RUN_TIMEOUT_MINUTES = 15
_STAGE_SAFE_PATTERN = re.compile(r"^[A-Za-z0-9_.:/ -]+$")
_STATUS_ALIASES: dict[str, str] = {
    "queued": "queued",
    "running": "running",
    "completed": "completed",
    "failed": "failed",
    "대기": "queued",
    "진행": "running",
    "진행중": "running",
    "실행중": "running",
    "완료": "completed",
    "실패": "failed",
}


def _save_run_config(run_id: str, request: TrainRequest) -> None:
    run_dir = get_run_dir(run_id)
    payload = {
        "run_id": run_id,
        "request": request.model_dump(mode="json", by_alias=True),
    }
    save_json(run_dir / "config.json", payload)


def _mark_stage(run_id: str, *, progress: int, stage: str, log: str | None = None) -> None:
    update_run(run_id, progress=progress, stage=stage)
    if log:
        append_log(run_id, log)


def _normalize_model_name(model_name: str | None) -> ModelName:
    if model_name in SUPPORTED_MODELS:
        return model_name
    return DEFAULT_MODEL


def _run_dir_has_artifacts(run_id: str) -> bool:
    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        return False
    return any(path.is_file() for path in run_dir.iterdir())


def _run_artifact_files(run_id: str) -> set[str]:
    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        return set()
    return {path.name for path in run_dir.iterdir() if path.is_file()}


def _run_has_completion_artifacts(run_id: str) -> bool:
    files = _run_artifact_files(run_id)
    if not files:
        return False
    has_predictions = any(name.startswith("predictions") and name.endswith(".parquet") for name in files)
    has_metrics = any(name.startswith("metrics") and name.endswith(".json") for name in files)
    has_backtest = any(name.startswith("backtest") and name.endswith(".json") for name in files)
    return has_predictions or has_metrics or has_backtest


def _run_dir_timestamp_iso(run_id: str) -> str:
    run_dir = get_run_dir(run_id)
    stat = run_dir.stat()
    ts = datetime.fromtimestamp(stat.st_mtime, tz=UTC).replace(microsecond=0)
    return ts.isoformat()


def _parse_iso_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    except ValueError:
        return None


def _recover_stale_running_run(run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("status") != "running":
        return payload
    updated_at = _parse_iso_timestamp(str(payload.get("updated_at", "")))
    if updated_at is None:
        return payload
    age_minutes = (datetime.now(UTC) - updated_at).total_seconds() / 60.0
    if age_minutes < STALE_RUN_TIMEOUT_MINUTES:
        return payload
    if _run_has_completion_artifacts(run_id):
        return payload

    update_run(
        run_id,
        status="failed",
        stage="stale_run_timeout",
        progress=100,
        error="stale_run_timeout",
    )
    append_log(
        run_id,
        f"Run failed automatically after {STALE_RUN_TIMEOUT_MINUTES} minutes without artifact progress.",
    )
    refreshed = get_run_state_dict(run_id)
    return refreshed if refreshed else payload


def _normalize_run_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    status_raw = str(normalized.get("status", "")).strip()
    status_key = _STATUS_ALIASES.get(status_raw) or _STATUS_ALIASES.get(status_raw.lower())
    if status_key is None:
        stage_text = str(normalized.get("stage", "")).lower()
        has_error = bool(normalized.get("error"))
        progress_value = int(normalized.get("progress", 0) or 0)
        if has_error or "fail" in stage_text:
            status_key = "failed"
        elif "complete" in stage_text or "backtest_completed" in stage_text:
            status_key = "completed"
        elif progress_value >= 100:
            status_key = "completed"
        elif progress_value <= 0:
            status_key = "queued"
        else:
            status_key = "running"
    normalized["status"] = status_key

    stage_raw = str(normalized.get("stage", "")).strip()
    if not stage_raw or _STAGE_SAFE_PATTERN.match(stage_raw) is None:
        if status_key == "completed":
            normalized["stage"] = "completed"
        elif status_key == "failed":
            normalized["stage"] = "failed"
        elif status_key == "running":
            normalized["stage"] = "running"
        else:
            normalized["stage"] = "queued"
    return normalized


def _predictions_path(run_id: str, model_name: ModelName) -> Path:
    return get_run_dir(run_id) / f"predictions_{model_name}.parquet"


def _metrics_path(run_id: str, model_name: ModelName) -> Path:
    return get_run_dir(run_id) / f"metrics_{model_name}.json"


def _backtest_path(run_id: str, model_name: ModelName) -> Path:
    return get_run_dir(run_id) / f"backtest_{model_name}.json"


def _signals_path(run_id: str, model_name: ModelName) -> Path:
    return get_run_dir(run_id) / f"signals_{model_name}.parquet"


def _load_predictions(run_id: str, model_name: ModelName = DEFAULT_MODEL) -> pd.DataFrame:
    run_dir = get_run_dir(run_id)
    candidates = [run_dir / f"predictions_{model_name}.parquet"]
    if model_name == DEFAULT_MODEL:
        candidates.append(run_dir / "predictions.parquet")
    if model_name == "xgb_lstm":
        candidates.append(run_dir / "predictions.parquet")

    for candidate in candidates:
        if candidate.exists():
            frame = pd.read_parquet(candidate)
            frame["date"] = pd.to_datetime(frame["date"]).dt.tz_localize(None)
            return frame
    raise ValueError(f"Prediction artifacts not found for model: {model_name}")


def _load_metrics_payload(run_id: str, model_name: ModelName = DEFAULT_MODEL) -> dict[str, Any]:
    run_dir = get_run_dir(run_id)
    candidates = [run_dir / f"metrics_{model_name}.json"]
    if model_name == DEFAULT_MODEL:
        candidates.append(run_dir / "metrics.json")
    if model_name == "xgb_lstm":
        candidates.append(run_dir / "metrics.json")

    for candidate in candidates:
        payload = load_json(candidate, default={})
        if payload:
            return payload
    raise ValueError(f"Metrics artifacts not found for model: {model_name}")


def _load_backtest_payload(run_id: str, model_name: ModelName = DEFAULT_MODEL) -> dict[str, Any]:
    run_dir = get_run_dir(run_id)
    candidates = [run_dir / f"backtest_{model_name}.json"]
    if model_name == DEFAULT_MODEL:
        candidates.append(run_dir / "backtest.json")
    if model_name == "xgb_lstm":
        candidates.append(run_dir / "backtest.json")

    for candidate in candidates:
        payload = load_json(candidate, default={})
        if payload:
            return payload
    raise ValueError(f"Backtest artifact not found for model: {model_name}")


def _safe_spearman(x: pd.Series, y: pd.Series) -> float:
    aligned = pd.concat([x, y], axis=1).replace([np.inf, -np.inf], np.nan).dropna()
    if aligned.shape[0] < 3:
        return 0.0
    xv = aligned.iloc[:, 0]
    yv = aligned.iloc[:, 1]
    if xv.nunique(dropna=True) <= 1 or yv.nunique(dropna=True) <= 1:
        return 0.0
    corr = spearmanr(xv, yv, nan_policy="omit").correlation
    if corr is None or np.isnan(corr):
        return 0.0
    return float(corr)


def _json_sanitize(value: Any) -> Any:
    """Recursively coerce NaN/Inf numerics into JSON-safe values."""
    if isinstance(value, dict):
        return {key: _json_sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_sanitize(item) for item in value]
    if isinstance(value, tuple):
        return [_json_sanitize(item) for item in value]
    if isinstance(value, (float, np.floating)):
        casted = float(value)
        if np.isnan(casted) or np.isinf(casted):
            return 0.0
        return casted
    return value


def _group_ic(frame: pd.DataFrame, score_col: str = "predicted_return") -> float:
    values: list[float] = []
    for _, group in frame.groupby("date"):
        if len(group) < 3:
            continue
        values.append(_safe_spearman(group[score_col], group["target_return"]))
    return float(np.mean(values)) if values else 0.0


def _compute_baseline_metrics(predictions: pd.DataFrame, split_ratio: float) -> dict[str, Any]:
    with_target = predictions.dropna(subset=["target_return"]).copy()
    if with_target.empty:
        return {"train_ic": 0.0, "val_ic": 0.0, "hit_rate": 0.0, "mse": 0.0, "mae": 0.0}

    unique_dates = sorted(with_target["date"].unique())
    cut_idx = max(1, min(len(unique_dates) - 1, int(len(unique_dates) * split_ratio)))
    cut_date = unique_dates[cut_idx - 1]
    train_df = with_target[with_target["date"] <= cut_date]
    val_df = with_target[with_target["date"] > cut_date]

    hit_rate = float(
        (
            np.sign(with_target["predicted_return"].to_numpy(dtype=float))
            == np.sign(with_target["target_return"].to_numpy(dtype=float))
        ).mean()
    )
    err = with_target["predicted_return"].to_numpy(dtype=float) - with_target["target_return"].to_numpy(dtype=float)
    mse = float(np.mean(np.square(err))) if err.size > 0 else 0.0
    mae = float(np.mean(np.abs(err))) if err.size > 0 else 0.0
    return {
        "train_ic": _group_ic(train_df, "predicted_return"),
        "val_ic": _group_ic(val_df, "predicted_return") if not val_df.empty else 0.0,
        "hit_rate": hit_rate,
        "mse": mse,
        "mae": mae,
    }


def _serialize_lstm_bundle(bundle: Any) -> dict[str, Any]:
    return {
        "state_dict": bundle.state_dict,
        "scaler_mean": bundle.scaler_mean,
        "scaler_scale": bundle.scaler_scale,
        "feature_columns": bundle.feature_columns,
        "seq_len": bundle.seq_len,
        "hidden_size": bundle.hidden_size,
        "num_layers": bundle.num_layers,
        "dropout": bundle.dropout,
        "validation_mse": bundle.validation_mse,
    }


def _save_default_compat_artifacts(
    run_dir: Path,
    predictions: pd.DataFrame,
    metrics_payload: dict[str, Any],
) -> None:
    predictions.to_parquet(run_dir / "predictions.parquet", index=False)
    save_json(run_dir / "metrics.json", metrics_payload)


def _resolve_selected_models(request: TrainRequest, symbol_count: int) -> tuple[ModelName, ...]:
    if request.model_choice == "lgbm_only" or (symbol_count >= 1000 and request.model_choice == "dual"):
        return ("lgbm_ranker",)
    if request.model_choice == "xgb_only":
        return ("xgb_lstm",)
    selected = tuple(model for model in request.model_set if model in SUPPORTED_MODELS)
    return selected or SUPPORTED_MODELS


def _apply_quick_mode_bounds(request: TrainRequest) -> tuple[date, date]:
    start_date = request.date_range.start_date
    end_date = request.date_range.end_date
    if request.quick_mode:
        quick_start = end_date - timedelta(days=365 * 3)
        if quick_start > start_date:
            start_date = quick_start
    return start_date, end_date


def _resolve_symbols_for_training_request(request: TrainRequest) -> list[str]:
    """Resolve training symbols with strict universe-id policy."""
    if request.symbols:
        symbols_from_request = [
            str(symbol) for symbol in request.symbols if str(symbol).strip()
        ]
        if symbols_from_request:
            return symbols_from_request

    if request.universe_id is not None:
        universe_key = str(request.universe_id).strip()
        available = ", ".join(list_universe_ids())
        if not universe_key:
            raise ValueError(
                "invalid_or_empty_universe_id: <empty>; "
                f"available_universe_id: {available}; "
                "hint: populate openbb_quant_ml/universe/<universe_id>.csv "
                "or run refresh_universes"
            )

        symbols = get_symbols_for_universe(universe_key)
        if not symbols:
            raise ValueError(
                f"invalid_or_empty_universe_id: {universe_key}; "
                f"available_universe_id: {available}; "
                f"hint: populate openbb_quant_ml/universe/{universe_key}.csv "
                "or run refresh_universes"
            )

        actual_count, minimum_required, meets_minimum = get_universe_size_status(
            universe_key, symbols
        )
        if not meets_minimum:
            raise ValueError(
                f"invalid_or_undersized_universe_id: {universe_key}; "
                f"actual_count: {actual_count}; "
                f"minimum_required: {minimum_required}; "
                "hint: run refresh_universes --all --no-validate"
            )
        return symbols

    return get_default_symbols()


def _sample_symbols_by_liquidity(
    datasets: dict[str, pd.DataFrame],
    limit: int,
) -> dict[str, pd.DataFrame]:
    if len(datasets) <= limit:
        return datasets
    ranked: list[tuple[str, float]] = []
    for symbol, frame in datasets.items():
        if frame.empty or "close" not in frame.columns or "volume" not in frame.columns:
            continue
        adv = (frame["close"].astype(float) * frame["volume"].astype(float)).tail(60).mean()
        ranked.append((symbol, float(adv) if np.isfinite(float(adv)) else 0.0))
    ranked = sorted(ranked, key=lambda item: item[1], reverse=True)
    selected = {symbol for symbol, _ in ranked[: max(1, int(limit))]}
    return {symbol: frame for symbol, frame in datasets.items() if symbol in selected}


def _apply_feature_pruning(
    frame: pd.DataFrame,
    feature_columns: list[str],
) -> tuple[pd.DataFrame, list[str], int]:
    if frame.empty or not feature_columns:
        return frame, feature_columns, 0
    sample = frame[feature_columns].copy()
    corr = sample.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    drop_cols = [column for column in upper.columns if bool((upper[column] > 0.98).any())]
    if not drop_cols:
        return frame, feature_columns, 0
    pruned = frame.drop(columns=drop_cols, errors="ignore")
    out_cols = [col for col in feature_columns if col not in set(drop_cols)]
    return pruned, out_cols, len(drop_cols)


def _run_training_job(run_id: str, request: TrainRequest) -> None:
    run_dir = get_run_dir(run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    time_profile: dict[str, float] = {}

    def _mark_elapsed(key: str, started_at: float) -> None:
        time_profile[key] = float(time.perf_counter() - started_at)

    try:
        update_run(run_id, status="running", progress=2, stage="initializing")
        append_log(run_id, "Training job started.")

        symbols = _resolve_symbols_for_training_request(request)
        start_date, end_date = _apply_quick_mode_bounds(request)
        selected_models = _resolve_selected_models(request, len(symbols))
        walk_forward_cfg = request.walk_forward_config.model_copy(deep=True)
        if request.quick_mode or request.walk_forward_compact:
            walk_forward_cfg.step_months = max(2, int(walk_forward_cfg.step_months))
            walk_forward_cfg.train_months = min(int(walk_forward_cfg.train_months), 24)
            walk_forward_cfg.val_months = max(1, min(int(walk_forward_cfg.val_months), 1))

        _mark_stage(run_id, progress=5, stage="loading_data", log="Loading market data.")
        load_log_bucket = {"value": -1}
        t_data = time.perf_counter()

        def _on_market_data_progress(processed: int, total: int, symbol: str, loaded: bool) -> None:
            total_safe = max(int(total), 1)
            fraction = float(processed) / float(total_safe)
            progress = 5 + int(30 * fraction)
            update_run(run_id, progress=max(6, min(progress, 35)), stage="loading_data")

            bucket = int(fraction * 10)
            if bucket != load_log_bucket["value"]:
                load_log_bucket["value"] = bucket
                append_log(
                    run_id,
                    f"Market data {processed}/{total_safe}: {symbol} ({'ok' if loaded else 'skip'})",
                )

        datasets, skipped_symbols = load_market_data(
            symbols,
            start_date,
            end_date,
            progress_callback=_on_market_data_progress,
        )
        if not datasets:
            raise ValueError("No valid market data was loaded for requested symbols.")
        if request.quick_mode:
            limit = int(request.top_liquid_n or min(500, len(datasets)))
            datasets = _sample_symbols_by_liquidity(datasets, limit=limit)
        if skipped_symbols:
            append_log(run_id, f"Skipped symbols (insufficient data): {', '.join(skipped_symbols)}")
        _mark_elapsed("data_update_sec", t_data)

        _mark_stage(run_id, progress=36, stage="feature_engineering", log="Building feature dataset.")
        t_features = time.perf_counter()
        feature_data, feature_columns, feature_skips = build_feature_dataset(
            data_by_symbol=datasets,
            feature_config=request.feature_parameters,
            horizon_days=request.horizon_days,
            target_mode=request.target_mode,
            close_to_next_open_horizon_policy=request.close_to_next_open_horizon_policy,
            include_macro_features=request.include_macro_features,
            macro_feature_subset=request.macro_feature_subset,
        )
        if request.feature_pruning:
            feature_data, feature_columns, dropped = _apply_feature_pruning(feature_data, feature_columns)
            if dropped > 0:
                append_log(run_id, f"Feature pruning removed {dropped} highly correlated columns.")
        _mark_stage(run_id, progress=45, stage="feature_engineering", log="Feature dataset built.")
        _mark_elapsed("feature_engineering_sec", t_features)
        skipped_union = sorted(set(skipped_symbols + feature_skips))
        if feature_data.empty:
            raise ValueError("Feature dataset is empty.")
        if not feature_columns:
            raise ValueError("No feature columns were generated.")

        close_panel = build_close_panel(datasets)
        open_panel = build_price_panel(datasets, "open")
        close_long = (
            close_panel.reset_index()
            .melt(id_vars=["date"], var_name="symbol", value_name="close")
            .dropna(subset=["close"])
        )
        open_long = (
            open_panel.reset_index()
            .melt(id_vars=["date"], var_name="symbol", value_name="open")
            .dropna(subset=["open"])
        )
        market_long = close_long.merge(open_long, on=["date", "symbol"], how="left")
        market_long.to_parquet(run_dir / "market_data.parquet", index=False)
        save_json(run_dir / "config_used.json", request.model_dump(mode="json", by_alias=True))
        save_json(
            run_dir / "data_versions.json",
            {
                "data": get_data_versions(),
                "features": get_feature_versions(),
            },
        )
        _mark_stage(run_id, progress=48, stage="training_prepare", log="Saved market panel artifact.")

        performance_rows: list[dict[str, Any]] = []
        model_windows: dict[str, tuple[int, int]] = {}
        if len(selected_models) == 1:
            model_windows[selected_models[0]] = (50, 92)
        else:
            # Keep fixed windows for stable UX when both models are requested.
            if "xgb_lstm" in selected_models:
                model_windows["xgb_lstm"] = (50, 71)
            if "lgbm_ranker" in selected_models:
                model_windows["lgbm_ranker"] = (72, 92)

        if "xgb_lstm" in selected_models:
            xgb_start, xgb_end = model_windows.get("xgb_lstm", (50, 92))
            _mark_stage(
                run_id,
                progress=xgb_start,
                stage="training_xgb_lstm",
                log="Training baseline hybrid model (XGBoost + LSTM).",
            )
            t_train_xgb = time.perf_counter()
            xgb_log_progress = {"value": -1}

            def _xgb_progress(local_ratio: float, message: str) -> None:
                clipped = float(max(0.0, min(1.0, local_ratio)))
                progress = xgb_start + int((xgb_end - xgb_start) * clipped)
                update_run(run_id, progress=progress, stage="training_xgb_lstm")
                if progress - xgb_log_progress["value"] >= 8 or clipped >= 1.0:
                    append_log(run_id, f"[xgb_lstm] {message} ({progress}%)")
                    xgb_log_progress["value"] = progress

            baseline_output = train_hybrid_models(
                feature_data=feature_data,
                feature_columns=feature_columns,
                config=request.model_parameters,
                progress_callback=_xgb_progress,
            )
            _mark_elapsed("train_xgb_lstm_sec", t_train_xgb)
            update_run(run_id, progress=xgb_end, stage="training_xgb_lstm")
            baseline_pred = baseline_output.predictions.copy()
            baseline_pred["date"] = pd.to_datetime(baseline_pred["date"]).dt.tz_localize(None)
            baseline_pred.to_parquet(run_dir / "predictions_xgb_lstm.parquet", index=False)

            baseline_ic = _compute_baseline_metrics(
                predictions=baseline_pred,
                split_ratio=request.model_parameters.train_val_split,
            )

            metrics_payload: dict[str, Any] = {
                "model_name": "xgb_lstm",
                "metrics": {
                    **baseline_output.metrics,
                    **baseline_ic,
                },
                "feature_importance": baseline_output.feature_importance,
                "model_meta": baseline_output.model_meta,
                "feature_columns": feature_columns,
                "symbols_requested": symbols,
                "symbols_trained": sorted(list(datasets.keys())),
                "symbols_skipped": skipped_union,
                "target_mode": request.target_mode,
                "horizon_days": request.horizon_days,
            }
            save_json(run_dir / "metrics_xgb_lstm.json", metrics_payload)

            baseline_output.xgb_model.save_model(str(run_dir / "model_xgb_xgb_lstm.json"))
            if baseline_output.lstm_bundle is not None:
                import torch

                torch.save(_serialize_lstm_bundle(baseline_output.lstm_bundle), run_dir / "model_lstm_xgb_lstm.pt")

            performance_rows.append(
                {
                    "model_name": "xgb_lstm",
                    "train_ic": baseline_ic.get("train_ic"),
                    "val_ic": baseline_ic.get("val_ic"),
                    "ndcg": None,
                    "hit_rate": baseline_ic.get("hit_rate"),
                }
            )

        if "lgbm_ranker" in selected_models:
            ranker_start, ranker_end = model_windows.get("lgbm_ranker", (50, 92))
            _mark_stage(run_id, progress=ranker_start, stage="training_ranker", log="Training ranker model.")
            t_train_ranker = time.perf_counter()
            ranker_log_progress = {"value": -1}

            def _ranker_progress(local_ratio: float, message: str) -> None:
                clipped = float(max(0.0, min(1.0, local_ratio)))
                progress = ranker_start + int((ranker_end - ranker_start) * clipped)
                update_run(run_id, progress=progress, stage="training_ranker")
                if progress - ranker_log_progress["value"] >= 5 or clipped >= 1.0:
                    append_log(run_id, f"[lgbm_ranker] {message} ({progress}%)")
                    ranker_log_progress["value"] = progress

            ranker_output = train_ranker_models(
                feature_data=feature_data,
                feature_columns=feature_columns,
                walk_forward=walk_forward_cfg,
                ranker_config=request.ranker_config,
                theta_grid=request.signal_config.theta_grid,
                horizon_months=max(1, request.horizon_days // 21 or 1),
                progress_callback=_ranker_progress,
            )
            _mark_elapsed("train_ranker_sec", t_train_ranker)
            update_run(run_id, progress=ranker_end, stage="training_ranker")
            ranker_pred = ranker_output.predictions.copy()
            ranker_pred["date"] = pd.to_datetime(ranker_pred["date"]).dt.tz_localize(None)
            ranker_pred.to_parquet(run_dir / "predictions_lgbm_ranker.parquet", index=False)

            ranker_metrics_payload: dict[str, Any] = {
                "model_name": "lgbm_ranker",
                "metrics": ranker_output.metrics,
                "feature_importance": ranker_output.feature_importance,
                "model_meta": ranker_output.model_meta,
                "feature_columns": ranker_output.feature_names,
                "symbols_requested": symbols,
                "symbols_trained": sorted(list(datasets.keys())),
                "symbols_skipped": skipped_union,
                "target_mode": request.target_mode,
                "horizon_days": request.horizon_days,
            }
            save_json(run_dir / "metrics_lgbm_ranker.json", ranker_metrics_payload)
            _save_default_compat_artifacts(run_dir, ranker_pred, ranker_metrics_payload)

            ndcg_obj = ranker_output.metrics.get("ndcg", {})
            performance_rows.append(
                {
                    "model_name": "lgbm_ranker",
                    "train_ic": ranker_output.metrics.get("train_ic"),
                    "val_ic": ranker_output.metrics.get("val_ic"),
                    "ndcg": ndcg_obj.get("ndcg_10") if isinstance(ndcg_obj, dict) else None,
                    "hit_rate": ranker_output.metrics.get("hit_rate"),
                    "best_theta": ranker_output.metrics.get("best_theta"),
                }
            )

        _mark_stage(run_id, progress=95, stage="finalizing", log="Saving model performance summary.")
        save_json(
            run_dir / "model_performance.json",
            {
                "run_id": run_id,
                "models": performance_rows,
            },
        )
        time_profile["total_training_sec"] = float(sum(time_profile.values()))
        save_json(run_dir / "time_profile.json", time_profile)

        update_run(run_id, progress=99, stage="finalizing")
        update_run(run_id, status="completed", progress=100, stage="completed", error=None)
        append_log(run_id, "Training job completed.")
    except Exception as exc:  # noqa: BLE001
        if time_profile:
            time_profile["total_training_sec"] = float(sum(time_profile.values()))
            save_json(run_dir / "time_profile.json", time_profile)
        update_run(run_id, status="failed", progress=100, stage="failed", error=str(exc))
        append_log(run_id, f"Error: {exc}")
        append_log(run_id, traceback.format_exc(limit=3))


def submit_training(request: TrainRequest) -> TrainResponse:
    """Queue a training job."""
    resolved_symbols = _resolve_symbols_for_training_request(request)
    resolved_request = request.model_copy(deep=True)
    resolved_request.symbols = resolved_symbols

    initialize_registry()
    state = create_run()
    _save_run_config(state.run_id, resolved_request)
    future = _EXECUTOR.submit(_run_training_job, state.run_id, resolved_request)
    _FUTURES[state.run_id] = future
    return TrainResponse(
        run_id=state.run_id,
        status=state.status,  # type: ignore[arg-type]
        artifact_root=state.artifact_root,
        created_at=state.created_at,
    )


def get_run(run_id: str) -> RunStatusResponse:
    """Read current run status."""
    payload = get_run_state_dict(run_id)
    if payload:
        payload = _recover_stale_running_run(run_id, payload)
        payload = _normalize_run_payload(payload)
        return RunStatusResponse(**payload)

    files = _run_artifact_files(run_id)
    if files:
        has_backtest = any(name.startswith("backtest") and name.endswith(".json") for name in files)
        has_predictions = any(name.startswith("predictions") and name.endswith(".parquet") for name in files)
        has_metrics = any(name.startswith("metrics") and name.endswith(".json") for name in files)
        has_models = any(name.startswith("model_") for name in files)
        has_market_data = "market_data.parquet" in files
        has_config = "config.json" in files

        status = "queued"
        progress = 0
        stage = "initialized"
        log_message = "Run metadata was reconstructed from run artifacts."

        if has_backtest:
            status = "completed"
            progress = 100
            stage = "backtest_completed"
            log_message = "Loaded completed run with backtest artifacts."
        elif has_predictions or has_metrics:
            status = "completed"
            progress = 95
            stage = "training_completed"
            log_message = "Loaded completed run with training artifacts."
        elif has_models or has_market_data:
            status = "running"
            progress = 60
            stage = "training_artifacts_detected"
            log_message = "Detected partial training artifacts without registry state."
        elif has_config:
            status = "queued"
            progress = 5
            stage = "configured"
            log_message = "Run configuration exists; waiting for training artifacts."

        restored_at = _run_dir_timestamp_iso(run_id)
        return RunStatusResponse(
            run_id=run_id,
            status=status,  # type: ignore[arg-type]
            progress=progress,
            stage=stage,
            created_at=restored_at,
            updated_at=restored_at,
            logs_tail=[
                log_message,
            ],
            error=None,
        )

    raise ValueError(f"Run not found: {run_id}")


def _ensure_run_completed(run_id: str, *, allow_artifact_fallback: bool = False) -> None:
    state = get_run_state(run_id)
    if state:
        if state.status != "completed":
            raise ValueError(f"Run is not completed: {state.status}")
        return
    if allow_artifact_fallback and _run_has_completion_artifacts(run_id):
        return
    raise ValueError(f"Run not found: {run_id}")


def build_signals(request: SignalRequest) -> SignalResponse:
    """Build signals from a completed run."""
    _ensure_run_completed(request.run_id, allow_artifact_fallback=True)
    model_name = _normalize_model_name(request.model_name)
    predictions = _load_predictions(request.run_id, model_name=model_name)
    as_of_iso, signal_df = generate_signals(
        predictions=predictions,
        as_of_date=request.as_of_date,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        balanced_long_short=request.balanced_long_short,
    )
    run_dir = get_run_dir(request.run_id)
    signal_df.to_parquet(_signals_path(request.run_id, model_name), index=False)
    if model_name == DEFAULT_MODEL:
        signal_df.to_parquet(run_dir / "signals.parquet", index=False)
    latest_market_date = None
    market_path = run_dir / "market_data.parquet"
    if market_path.exists():
        market_long = pd.read_parquet(market_path, columns=["date"])
        if not market_long.empty:
            latest_market_date = pd.Timestamp(pd.to_datetime(market_long["date"]).max()).date().isoformat()
    staleness_days = 0
    if latest_market_date:
        staleness_days = max(
            0,
            (pd.Timestamp(latest_market_date).date() - pd.Timestamp(as_of_iso).date()).days,
        )
    regime_snapshot, recommended_mode = _signal_regime_snapshot(request.run_id)
    return SignalResponse(
        run_id=request.run_id,
        model_name=model_name,
        as_of_date=as_of_iso,
        latest_market_date=latest_market_date,
        staleness_days=staleness_days,
        recommended_portfolio_mode=recommended_mode,  # type: ignore[arg-type]
        regime_snapshot=regime_snapshot,
        signals=signal_df.to_dict(orient="records"),  # type: ignore[arg-type]
    )


def run_backtest_for_run(request: BacktestRequest) -> BacktestResponse:
    """Run backtest from a completed run."""
    _ensure_run_completed(request.run_id, allow_artifact_fallback=True)
    model_name = _normalize_model_name(request.model_name)
    predictions = _load_predictions(request.run_id, model_name=model_name)

    run_dir = get_run_dir(request.run_id)
    market_path = run_dir / "market_data.parquet"
    if not market_path.exists():
        raise ValueError("Market data artifact is missing.")
    market_long = pd.read_parquet(market_path)
    market_long = market_long.assign(date=pd.to_datetime(market_long["date"]).dt.tz_localize(None))
    close_panel = market_long.pivot(index="date", columns="symbol", values="close").sort_index()
    if "open" in market_long.columns:
        open_panel = market_long.pivot(index="date", columns="symbol", values="open").sort_index()
    else:
        open_panel = close_panel.copy()

    result = run_backtest(
        predictions=predictions[["date", "symbol", "predicted_return"]],
        open_panel=open_panel,
        close_panel=close_panel,
        start_date=request.start_date,
        end_date=request.end_date,
        constraints=request.constraints,
        cost_bps=request.cost_bps,
        slippage_bps=request.slippage_bps,
        entry_price=request.entry_price,
        exit_price=request.exit_price,
        portfolio_mode=request.portfolio_mode,
        regime_policy=request.regime_policy,
    )

    payload = {
        "run_id": request.run_id,
        "model_name": model_name,
        "start_date": request.start_date.isoformat(),
        "end_date": request.end_date.isoformat(),
        "base_index": result.base_index,
        "benchmark_symbol": result.benchmark_symbol,
        "metrics": result.metrics,
        "equity_curve": result.equity_curve,
        "benchmark_curve": result.benchmark_curve,
        "period_weights": result.period_weights,
        "cost_breakdown": result.cost_breakdown,
        "consistency_checks": result.consistency_checks,
        "regime_mode_by_period": result.regime_mode_by_period,
        "constraints": request.constraints.model_dump(mode="json"),
        "cost_bps": request.cost_bps,
        "slippage_bps": request.slippage_bps,
        "entry_price": request.entry_price,
        "exit_price": request.exit_price,
        "portfolio_mode": request.portfolio_mode,
        "mu_mapping": request.mu_mapping,
        "regime_policy": request.regime_policy,
    }
    payload = _json_sanitize(payload)
    save_json(_backtest_path(request.run_id, model_name), payload)
    if model_name == DEFAULT_MODEL:
        save_json(run_dir / "backtest.json", payload)
    try:
        refresh_alerts_for_run(run_id=request.run_id, model_name=model_name)
    except Exception:  # noqa: BLE001
        # Alerts are non-blocking post-processing outputs.
        pass

    return BacktestResponse(**payload)


def get_summary(run_id: str, model_name: ModelName = DEFAULT_MODEL) -> ArtifactSummaryResponse:
    """Read artifact summary for a run."""
    model_name = _normalize_model_name(model_name)
    run_dir = get_run_dir(run_id)
    metrics = _load_metrics_payload(run_id, model_name=model_name)
    return ArtifactSummaryResponse(
        run_id=run_id,
        model_name=model_name,
        model_meta=metrics.get("model_meta", {}),
        latest_validation_error=metrics.get("metrics", {}).get("latest_validation_error"),
        feature_importance=metrics.get("feature_importance", []),
        params=load_json(run_dir / "config.json", default={}),
        available_artifacts=list_run_artifacts(run_id),
    )


def get_universe() -> UniverseResponse:
    """Return active universe config."""
    payload = load_universe_config()
    return UniverseResponse(version=payload.get("version", "v1"), assets=payload.get("assets", []))


def _extract_backtest_metric(backtest: dict[str, Any], key: str) -> float | None:
    metrics = backtest.get("metrics", {})
    value = metrics.get(key) if isinstance(metrics, dict) else None
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_model_performance(run_id: str) -> ModelPerformanceResponse:
    """Return model comparison metrics."""
    models: list[ModelPerformanceItem] = []
    for model_name in SUPPORTED_MODELS:
        try:
            metrics_payload = _load_metrics_payload(run_id, model_name=model_name)
        except ValueError:
            continue

        metrics = metrics_payload.get("metrics", {})
        backtest_payload = load_json(_backtest_path(run_id, model_name), default={})
        ndcg_obj = metrics.get("ndcg") if isinstance(metrics, dict) else None
        ndcg_score = ndcg_obj.get("ndcg_10") if isinstance(ndcg_obj, dict) else None

        item = ModelPerformanceItem(
            model_name=model_name,
            train_ic=metrics.get("train_ic") if isinstance(metrics, dict) else None,
            val_ic=metrics.get("val_ic") if isinstance(metrics, dict) else None,
            ndcg=ndcg_score,
            sharpe=_extract_backtest_metric(backtest_payload, "sharpe"),
            max_dd=_extract_backtest_metric(backtest_payload, "max_drawdown"),
            turnover=_extract_backtest_metric(backtest_payload, "turnover"),
            hit_rate=metrics.get("hit_rate") if isinstance(metrics, dict) else None,
            regime_performance=backtest_payload.get("regime_performance", {}),
        )
        models.append(item)

    if not models:
        raise ValueError(f"No model metrics found for run: {run_id}")
    return ModelPerformanceResponse(run_id=run_id, models=models)


def get_model_ic(run_id: str, model_name: ModelName = DEFAULT_MODEL, window: int = 6) -> ModelICResponse:
    """Return IC time-series for a model."""
    model_name = _normalize_model_name(model_name)
    predictions = _load_predictions(run_id, model_name=model_name).dropna(subset=["target_return"])
    if predictions.empty:
        raise ValueError("No prediction rows with target_return were found.")

    rows: list[dict[str, Any]] = []
    for date_value, group in predictions.groupby("date"):
        if len(group) < 3:
            continue
        rows.append(
            {
                "date": pd.Timestamp(date_value).date().isoformat(),
                "ic": _safe_spearman(group["predicted_return"], group["target_return"]),
            }
        )
    if not rows:
        raise ValueError("Insufficient grouped rows to compute IC.")

    frame = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    frame["rolling_ic"] = frame["ic"].rolling(window=max(window, 1), min_periods=1).mean()
    points = [
        ModelICPoint(date=row["date"], ic=float(row["ic"]), rolling_ic=float(row["rolling_ic"]))
        for _, row in frame.iterrows()
    ]
    return ModelICResponse(run_id=run_id, model_name=model_name, window=max(window, 1), points=points)


def _load_close_panel(run_id: str) -> pd.DataFrame:
    market_path = get_run_dir(run_id) / "market_data.parquet"
    if not market_path.exists():
        return pd.DataFrame()
    market_long = pd.read_parquet(market_path)
    panel = (
        market_long.assign(date=pd.to_datetime(market_long["date"]).dt.tz_localize(None))
        .pivot(index="date", columns="symbol", values="close")
        .sort_index()
    )
    return panel


def _signal_regime_snapshot(run_id: str) -> tuple[dict[str, str], str]:
    close_panel = _load_close_panel(run_id)
    if close_panel.empty:
        return {}, "long_only"
    benchmark_symbol = "SPY" if "SPY" in close_panel.columns else str(close_panel.columns[0])
    benchmark = close_panel[benchmark_symbol].dropna().astype(float)
    benchmark.index = pd.to_datetime(benchmark.index).tz_localize(None)
    if benchmark.empty:
        return {}, "long_only"

    ret = benchmark.pct_change(fill_method=None).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    ma200 = benchmark.rolling(200, min_periods=20).mean()
    distance = benchmark / (ma200 + 1e-12) - 1.0
    trend = "bull" if float(distance.iloc[-1]) > 0.01 else "bear" if float(distance.iloc[-1]) < -0.01 else "sideways"
    vol20 = ret.rolling(20, min_periods=5).std(ddof=0) * np.sqrt(252)
    low_q = float(vol20.quantile(0.33))
    high_q = float(vol20.quantile(0.66))
    latest_vol = float(vol20.iloc[-1]) if not np.isnan(float(vol20.iloc[-1])) else 0.0
    vol_regime = "low" if latest_vol <= low_q else "high" if latest_vol >= high_q else "mid"

    recommended_mode = "long_short" if trend == "bull" and vol_regime in {"low", "mid"} else "long_only"
    return {"trend_regime": trend, "vol_regime": vol_regime}, recommended_mode


def get_model_regime(run_id: str, model_name: ModelName = DEFAULT_MODEL) -> ModelRegimeResponse:
    """Return legacy regime payload mapped from dashboard regime metrics."""
    model_name = _normalize_model_name(model_name)
    try:
        regime_payload = get_dashboard_performance_regime(run_id=run_id, model_name=model_name)
    except Exception:
        return ModelRegimeResponse(run_id=run_id, model_name=model_name, regimes={})
    if regime_payload.status != "ok":
        return ModelRegimeResponse(run_id=run_id, model_name=model_name, regimes={})

    regimes: dict[str, dict[str, float | int]] = {}
    for key, value in regime_payload.trend_regime_perf.items():
        regimes[f"trend:{key}"] = {
            "count": int(value.get("count", 0)),
            "mean_return": float(value.get("mean_return", 0.0)),
            "sharpe": float(value.get("sharpe", 0.0)),
            "ic": float(value.get("ic", 0.0)),
            "turnover": float(value.get("turnover", 0.0)),
        }
    for key, value in regime_payload.vol_regime_perf.items():
        regimes[f"vol:{key}"] = {
            "count": int(value.get("count", 0)),
            "mean_return": float(value.get("mean_return", 0.0)),
            "sharpe": float(value.get("sharpe", 0.0)),
            "ic": float(value.get("ic", 0.0)),
            "turnover": float(value.get("turnover", 0.0)),
        }
    for key, value in regime_payload.liquidity_regime_perf.items():
        regimes[f"liquidity:{key}"] = {
            "count": int(value.get("count", 0)),
            "mean_return": float(value.get("mean_return", 0.0)),
            "sharpe": float(value.get("sharpe", 0.0)),
            "ic": float(value.get("ic", 0.0)),
            "turnover": float(value.get("turnover", 0.0)),
        }
    return ModelRegimeResponse(run_id=run_id, model_name=model_name, regimes=regimes)


def get_feature_importance(run_id: str, model_name: ModelName = DEFAULT_MODEL) -> FeatureImportanceResponse:
    """Return feature importance payload for a model."""
    model_name = _normalize_model_name(model_name)
    metrics_payload = _load_metrics_payload(run_id, model_name=model_name)
    return FeatureImportanceResponse(
        run_id=run_id,
        model_name=model_name,
        items=metrics_payload.get("feature_importance", []),
    )


def get_predictions_latest(
    run_id: str,
    model_name: ModelName = DEFAULT_MODEL,
    top_k: int = 20,
) -> PredictionsLatestResponse:
    """Return latest prediction table for a model."""
    model_name = _normalize_model_name(model_name)
    predictions = _load_predictions(run_id, model_name=model_name)
    if predictions.empty:
        raise ValueError("Prediction table is empty.")

    latest_date = pd.Timestamp(predictions["date"].max()).date().isoformat()
    latest = predictions[predictions["date"] == predictions["date"].max()].copy()
    score = latest["predicted_return"]
    std = float(score.std(ddof=0))
    if std <= 0 or np.isnan(std):
        latest["z_score"] = 0.0
    else:
        latest["z_score"] = (score - float(score.mean())) / (std + 1e-12)
    latest["side"] = np.where(
        latest["z_score"] >= 0.5,
        "buy",
        np.where(latest["z_score"] <= -0.5, "sell", "hold"),
    )
    latest = latest.sort_values("predicted_return", ascending=False).head(max(int(top_k), 1))
    rows = latest[
        ["symbol", "predicted_return", "target_return", "z_score", "side", "predicted_xgb", "predicted_lstm"]
    ].to_dict(orient="records")
    return PredictionsLatestResponse(
        run_id=run_id,
        model_name=model_name,
        as_of_date=latest_date,
        predictions=rows,
    )


def _collapse_small_categories(weights: dict[str, float], cutoff: float = 0.01) -> dict[str, float]:
    collapsed: dict[str, float] = {}
    other_total = 0.0
    for category, value in weights.items():
        if value < cutoff:
            other_total += value
        else:
            collapsed[category] = value
    if other_total > 0:
        collapsed["other"] = collapsed.get("other", 0.0) + other_total
    return collapsed


def _round_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def get_portfolio_current(run_id: str, model_name: ModelName = DEFAULT_MODEL) -> PortfolioCurrentResponse:
    """Return latest rebalance portfolio and rationale."""
    _ensure_run_completed(run_id, allow_artifact_fallback=True)
    model_name = _normalize_model_name(model_name)

    try:
        backtest_payload = _load_backtest_payload(run_id, model_name=model_name)
    except ValueError as exc:
        raise ValueError("Run backtest first for selected model.") from exc

    period_weights = backtest_payload.get("period_weights", [])
    constraints = backtest_payload.get(
        "constraints",
        {"max_weight": 0.2, "long_only": True, "risk_aversion": 3.0, "lookback_days": 126},
    )
    cost_bps = float(backtest_payload.get("cost_bps", 10.0))

    if not period_weights:
        rationale = PortfolioRationale(
            summary_lines=[
                "백테스트 결과에 저장된 리밸런싱 비중이 아직 없습니다.",
                "현재는 자산군 비중을 계산할 수 없어 포트폴리오를 비워서 표시합니다.",
                "먼저 Run Backtest를 실행하면 최신 리밸런싱 비중과 설명이 생성됩니다.",
            ],
            constraints_applied={
                "max_weight": float(constraints.get("max_weight", 0.2)),
                "long_only": bool(constraints.get("long_only", True)),
                "risk_aversion": float(constraints.get("risk_aversion", 3.0)),
                "lookback_days": float(constraints.get("lookback_days", 126)),
                "cost_bps": cost_bps,
            },
        )
        return PortfolioCurrentResponse(
            run_id=run_id,
            model_name=model_name,
            as_of_date=None,
            total_weight=0.0,
            symbol_weights=[],
            asset_class_weights=[],
            rationale=rationale,
        )

    latest = period_weights[-1]
    as_of_date = str(latest.get("date"))
    raw_weights: dict[str, float] = {
        str(symbol): max(float(weight), 0.0)
        for symbol, weight in dict(latest.get("weights", {})).items()
    }
    total_weight = float(sum(raw_weights.values()))
    if total_weight <= 0:
        total_weight = 1.0

    universe_payload = load_universe_config()
    category_map = {item.get("symbol"): item.get("category", "other") for item in universe_payload.get("assets", [])}

    symbol_items: list[PortfolioSymbolWeightItem] = []
    category_weights: dict[str, float] = {}
    for symbol, weight in sorted(raw_weights.items(), key=lambda pair: pair[1], reverse=True):
        normalized = float(weight / total_weight)
        category = str(category_map.get(symbol, "other"))
        symbol_items.append(
            PortfolioSymbolWeightItem(symbol=symbol, weight=normalized, category=category),
        )
        category_weights[category] = category_weights.get(category, 0.0) + normalized

    category_weights = _collapse_small_categories(category_weights, cutoff=0.01)
    asset_items = [
        AssetClassWeightItem(category=category, weight=value)
        for category, value in sorted(category_weights.items(), key=lambda pair: pair[1], reverse=True)
    ]

    top_categories = asset_items[:2]
    top_symbols = symbol_items[:3]
    top_cat_text = ", ".join(f"{item.category} {_round_pct(item.weight)}" for item in top_categories) or "구성 없음"
    top_cat_total = sum(item.weight for item in top_categories)
    top_symbol_text = ", ".join(f"{item.symbol} {_round_pct(item.weight)}" for item in top_symbols) or "구성 없음"
    top_category_name = top_categories[0].category if top_categories else "other"

    summary_lines = [
        f"최신 리밸런싱({as_of_date}) 기준 상위 자산군은 {top_cat_text}이며 합계는 {_round_pct(top_cat_total)}입니다.",
        f"상위 비중 종목({top_symbol_text})이 {top_category_name}에 집중되어 해당 자산군 비중이 확대되었습니다.",
        "리스크 제약(max_weight, long_only, risk_aversion, cost_bps)을 적용해 과도한 편중을 제한했습니다.",
    ]
    rationale = PortfolioRationale(
        summary_lines=summary_lines,
        constraints_applied={
            "max_weight": float(constraints.get("max_weight", 0.2)),
            "long_only": bool(constraints.get("long_only", True)),
            "risk_aversion": float(constraints.get("risk_aversion", 3.0)),
            "lookback_days": float(constraints.get("lookback_days", 126)),
            "cost_bps": cost_bps,
        },
    )
    return PortfolioCurrentResponse(
        run_id=run_id,
        model_name=model_name,
        as_of_date=as_of_date,
        total_weight=float(sum(item.weight for item in symbol_items)),
        symbol_weights=symbol_items,
        asset_class_weights=asset_items,
        rationale=rationale,
    )
