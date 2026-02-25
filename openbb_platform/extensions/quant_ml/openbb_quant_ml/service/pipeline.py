"""Pipeline orchestration for quant training, signals, and backtests."""

from __future__ import annotations

import pickle
import platform
import re
import sys
import time
import traceback
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
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
    RebalanceHistoryResponse,
    UniverseSnapshotResponse,
    UniverseExclusionItem,
    PortfolioRationale,
    PortfolioSymbolWeightItem,
    PredictionsLatestResponse,
    RebalanceHistoryItem,
    RunStatusResponse,
    SignalRequest,
    SignalResponse,
    TrainRequest,
    TrainResponse,
    UniverseResponse,
)
from openbb_quant_ml.service.artifact_store import (
    ARTIFACT_CONTRACT_VERSION,
    artifact_completeness,
    required_artifacts_ready,
    write_contract_manifest,
    write_json as write_artifact_json,
    write_parquet as write_artifact_parquet,
    write_text as write_artifact_text,
)
from openbb_quant_ml.service.asof_guard import build_asof_manifest
from openbb_quant_ml.service.backtest import run_backtest
from openbb_quant_ml.service.contract.data_contract import write_data_layer_meta
from openbb_quant_ml.service.constraints import (
    build_constraints_log,
    summarize_constraint_bindings,
)
from openbb_quant_ml.service.delisting import load_delisting_events
from openbb_quant_ml.service.delisting import validate_delisting_events_required
from openbb_quant_ml.service.cache_registry import (
    get_data_versions,
    get_feature_versions,
)
from openbb_quant_ml.service.dashboard_metrics import (
    get_performance_regime as get_dashboard_performance_regime,
    refresh_alerts_for_run,
)
from openbb_quant_ml.service.data_loader import (
    build_close_panel,
    build_price_panel,
    load_market_data,
)
from openbb_quant_ml.service.feature_engineering import build_feature_dataset
from openbb_quant_ml.service.modeling import (
    train_hybrid_models,
    tune_xgb_hyperparameters,
)
from openbb_quant_ml.service.pnl_attribution import build_pnl_attribution
from openbb_quant_ml.service.portfolio_policy import get_portfolio_policy
from openbb_quant_ml.service.ranker_modeling import (
    train_ranker_models,
    tune_ranker_hyperparameters,
)
from openbb_quant_ml.service.report_builder import build_report_html
from openbb_quant_ml.service.run_context import ensure_run_context
from openbb_quant_ml.service.run_registry import (
    append_log,
    create_run,
    get_run_state,
    get_run_state_dict,
    initialize_registry,
    update_run,
)
from openbb_quant_ml.service.signal_schema import (
    build_signal_contract,
    infer_model_version,
)
from openbb_quant_ml.service.signals import generate_signals
from openbb_quant_ml.service.stale_policy import (
    STALE_TIMEOUT_MINUTES,
    is_stale,
    latest_artifact_mtime,
)
from openbb_quant_ml.service.storage import (
    get_run_dir,
    list_run_artifacts,
    load_json,
    save_json,
    save_parquet_atomic,
)
from openbb_quant_ml.service.universe import (
    get_default_symbols,
    get_symbol_metadata_map,
    get_symbols_for_universe,
    get_universe_size_status,
    list_universe_ids,
    load_universe_config,
)
from openbb_quant_ml.service.universe_policy import get_universe_policy
from openbb_quant_ml.service.universe_engine import (
    build_universe_snapshot,
    load_latest_universe_exclusions,
    load_latest_universe_snapshot,
    universe_snapshot_dir,
)

DEFAULT_MODEL: ModelName = "lgbm_ranker"
SUPPORTED_MODELS: tuple[ModelName, ...] = ("xgb_lstm", "lgbm_ranker", "catboost_ranker")

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="quant-ml")
_FUTURES: dict[str, Future] = {}
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


def _mark_stage(
    run_id: str, *, progress: int, stage: str, log: str | None = None
) -> None:
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
    has_predictions = any(
        name.startswith("predictions") and name.endswith(".parquet") for name in files
    )
    has_metrics = any(
        name.startswith("metrics") and name.endswith(".json") for name in files
    )
    has_backtest = any(
        name.startswith("backtest") and name.endswith(".json") for name in files
    )
    return has_predictions or has_metrics or has_backtest


def _run_dir_timestamp_iso(run_id: str) -> str:
    run_dir = get_run_dir(run_id)
    stat = run_dir.stat()
    ts = datetime.fromtimestamp(stat.st_mtime, tz=UTC).replace(microsecond=0)
    return ts.isoformat()


def _run_stale_meta(run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    artifact_mtime = latest_artifact_mtime(get_run_dir(run_id))
    stale, stale_reason, idle_minutes = is_stale(
        payload.get("updated_at"),
        payload.get("last_heartbeat_at"),
        artifact_mtime,
        timeout_minutes=STALE_TIMEOUT_MINUTES,
    )
    return {
        "stale": stale,
        "stale_reason": stale_reason,
        "idle_minutes": idle_minutes,
        "artifact_mtime": (
            artifact_mtime.replace(microsecond=0).isoformat()
            if artifact_mtime is not None
            else None
        ),
    }


def _enrich_run_stale_fields(run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(payload)
    stale_meta = _run_stale_meta(run_id, enriched)
    enriched["run_idle_minutes"] = stale_meta["idle_minutes"]
    enriched["stale_timeout_minutes"] = STALE_TIMEOUT_MINUTES
    if str(enriched.get("status", "")).lower() == "running":
        enriched["stale_reason"] = stale_meta["stale_reason"]
    return enriched


def _recover_stale_running_run(run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("status") != "running":
        return _enrich_run_stale_fields(run_id, payload)
    stale_meta = _run_stale_meta(run_id, payload)
    if not stale_meta["stale"]:
        return _enrich_run_stale_fields(run_id, payload)
    if _run_has_completion_artifacts(run_id):
        return _enrich_run_stale_fields(run_id, payload)

    update_run(
        run_id,
        status="failed",
        stage="stale_run_timeout",
        progress=100,
        error="stale_run_timeout",
        stale_reason=str(stale_meta["stale_reason"] or "idle_timeout"),
    )
    append_log(
        run_id,
        f"Run failed automatically after {STALE_TIMEOUT_MINUTES} minutes without heartbeat/artifact progress.",
    )
    refreshed = get_run_state_dict(run_id)
    out = refreshed if refreshed else payload
    return _enrich_run_stale_fields(run_id, out)


def _normalize_run_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    status_raw = str(normalized.get("status", "")).strip()
    status_key = _STATUS_ALIASES.get(status_raw) or _STATUS_ALIASES.get(
        status_raw.lower()
    )
    if status_key is None:
        stage_text = str(normalized.get("stage", "")).lower()
        has_error = bool(normalized.get("error"))
        progress_value = int(normalized.get("progress", 0) or 0)
        if has_error or "fail" in stage_text:
            status_key = "failed"
        elif (
            "complete" in stage_text
            or "backtest_completed" in stage_text
            or progress_value >= 100
        ):
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


def _load_predictions(
    run_id: str, model_name: ModelName = DEFAULT_MODEL
) -> pd.DataFrame:
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
            if "score" not in frame.columns and "predicted_return" in frame.columns:
                frame["score"] = pd.to_numeric(
                    frame["predicted_return"], errors="coerce"
                ).fillna(0.0)
            return frame
    raise ValueError(f"Prediction artifacts not found for model: {model_name}")


def _load_metrics_payload(
    run_id: str, model_name: ModelName = DEFAULT_MODEL
) -> dict[str, Any]:
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


def _load_backtest_payload(
    run_id: str, model_name: ModelName = DEFAULT_MODEL
) -> dict[str, Any]:
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


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        casted = float(value)
    except (TypeError, ValueError):
        return default
    if np.isnan(casted) or np.isinf(casted):
        return default
    return casted


def _period_weights_to_frame(period_weights: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in period_weights:
        if not isinstance(row, dict):
            continue
        as_of = str(row.get("date", "")).strip()
        weights = row.get("weights", {})
        if not as_of or not isinstance(weights, dict):
            continue
        for symbol, weight in weights.items():
            rows.append(
                {
                    "date": as_of,
                    "ticker": str(symbol).strip().upper(),
                    "weight": _safe_float(weight, default=0.0),
                }
            )
    if not rows:
        return pd.DataFrame(columns=["date", "ticker", "weight"])
    return pd.DataFrame(rows)


def _derive_trade_plan_rows(
    period_weights: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    previous: dict[str, float] = {}
    for row in period_weights:
        if not isinstance(row, dict):
            continue
        as_of = str(row.get("date", "")).strip()
        weights = row.get("weights", {})
        if not as_of or not isinstance(weights, dict):
            continue
        current = {
            str(symbol).strip().upper(): _safe_float(weight, default=0.0)
            for symbol, weight in weights.items()
            if str(symbol).strip()
        }
        symbols = sorted(set(previous) | set(current))
        for symbol in symbols:
            before = _safe_float(previous.get(symbol, 0.0), default=0.0)
            after = _safe_float(current.get(symbol, 0.0), default=0.0)
            delta = after - before
            if abs(delta) <= 1e-12:
                continue
            rows.append(
                {
                    "date": as_of,
                    "ticker": symbol,
                    "action": "buy" if delta > 0 else "sell",
                    "weight_before": before,
                    "weight_after": after,
                    "weight_delta": delta,
                }
            )
        previous = current
    return rows


def _latest_sector_exposure_frame(
    rebalance_reports: list[dict[str, Any]],
) -> pd.DataFrame:
    if not rebalance_reports:
        return pd.DataFrame(columns=["sector", "weight"])
    latest = rebalance_reports[-1]
    rows = latest.get("sector_exposure_report", []) if isinstance(latest, dict) else []
    if not isinstance(rows, list):
        rows = []
    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(columns=["sector", "weight"])
    if "sector" not in frame.columns:
        frame["sector"] = frame.get("category", "other")
    frame["sector"] = frame["sector"].astype(str)
    frame["weight"] = pd.to_numeric(frame.get("weight"), errors="coerce").fillna(0.0)
    return frame[["sector", "weight"]]


def _group_ic(frame: pd.DataFrame, score_col: str = "predicted_return") -> float:
    values: list[float] = []
    for _, group in frame.groupby("date"):
        if len(group) < 3:
            continue
        values.append(_safe_spearman(group[score_col], group["target_return"]))
    return float(np.mean(values)) if values else 0.0


def _compute_baseline_metrics(
    predictions: pd.DataFrame, split_ratio: float
) -> dict[str, Any]:
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
    err = with_target["predicted_return"].to_numpy(dtype=float) - with_target[
        "target_return"
    ].to_numpy(dtype=float)
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


def _save_ranker_inference_artifacts(
    run_dir: Path,
    *,
    model: Any,
    feature_columns: list[str],
    backend: str,
    trained_until: str,
    mu_mapping: str,
    label_return_map: dict[int, float],
    label_return_fallback: float,
    model_name: ModelName = "lgbm_ranker",
) -> None:
    model_path = run_dir / f"model_{model_name}.pkl"
    meta_path = run_dir / f"model_{model_name}_meta.json"

    if backend == "catboost":
        try:
            model.save_model(str(run_dir / f"model_{model_name}.cbm"))
        except Exception:
            pass
    with model_path.open("wb") as file:
        pickle.dump(model, file)

    save_json(
        meta_path,
        {
            "backend": backend,
            "feature_columns": feature_columns,
            "trained_until": trained_until,
            "mu_mapping": mu_mapping,
            "label_return_map": {
                str(int(key)): float(value) for key, value in label_return_map.items()
            },
            "label_return_fallback": float(label_return_fallback),
        },
    )


def _resolve_selected_models(
    request: TrainRequest, symbol_count: int
) -> tuple[ModelName, ...]:
    if request.model_choice == "lgbm_only" or (
        symbol_count >= 1000 and request.model_choice == "dual"
    ):
        return ("lgbm_ranker",)
    if request.model_choice == "xgb_only":
        return ("xgb_lstm",)
    if request.model_choice == "catboost_only":
        return ("catboost_ranker",)
    selected = tuple(model for model in request.model_set if model in SUPPORTED_MODELS)
    return selected or SUPPORTED_MODELS


def _apply_quick_mode_bounds(request: TrainRequest) -> tuple[date, date]:
    start_date = request.date_range.start_date
    end_date = request.date_range.end_date
    if request.quick_mode:
        quick_start = end_date - timedelta(days=365 * 3)
        start_date = max(start_date, quick_start)
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
        adv = (
            (frame["close"].astype(float) * frame["volume"].astype(float))
            .tail(60)
            .mean()
        )
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
    drop_cols = [
        column for column in upper.columns if bool((upper[column] > 0.98).any())
    ]
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
            walk_forward_cfg.val_months = max(
                1, min(int(walk_forward_cfg.val_months), 1)
            )

        _mark_stage(
            run_id, progress=5, stage="loading_data", log="Loading market data."
        )
        load_log_bucket = {"value": -1}
        t_data = time.perf_counter()

        def _on_market_data_progress(
            processed: int, total: int, symbol: str, loaded: bool
        ) -> None:
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
            max_workers=(
                int(request.market_data_workers)
                if request.market_data_workers is not None
                else 6
            ),
        )
        if not datasets:
            raise ValueError("No valid market data was loaded for requested symbols.")
        if request.quick_mode:
            limit = int(request.top_liquid_n or min(500, len(datasets)))
            datasets = _sample_symbols_by_liquidity(datasets, limit=limit)
        if skipped_symbols:
            append_log(
                run_id,
                f"Skipped symbols (insufficient data): {', '.join(skipped_symbols)}",
            )
        _mark_elapsed("data_update_sec", t_data)

        _mark_stage(
            run_id,
            progress=36,
            stage="feature_engineering",
            log="Building feature dataset.",
        )
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
            feature_data, feature_columns, dropped = _apply_feature_pruning(
                feature_data, feature_columns
            )
            if dropped > 0:
                append_log(
                    run_id,
                    f"Feature pruning removed {dropped} highly correlated columns.",
                )
        _mark_stage(
            run_id,
            progress=45,
            stage="feature_engineering",
            log="Feature dataset built.",
        )
        _mark_elapsed("feature_engineering_sec", t_features)
        skipped_union = sorted(set(skipped_symbols + feature_skips))
        if feature_data.empty:
            raise ValueError("Feature dataset is empty.")
        if not feature_columns:
            raise ValueError("No feature columns were generated.")

        model_config_active = request.model_parameters.model_copy(deep=True)
        ranker_config_active_lgbm = request.ranker_config.model_copy(deep=True)
        ranker_config_active_catboost = request.ranker_config.model_copy(deep=True)
        if not request.early_stopping:
            ranker_config_active_lgbm.early_stopping_rounds = max(
                int(ranker_config_active_lgbm.n_estimators), 10
            )
            ranker_config_active_catboost.early_stopping_rounds = max(
                int(ranker_config_active_catboost.n_estimators), 10
            )

        hpo_cfg = request.hpo_config
        if bool(hpo_cfg.enabled):
            _mark_stage(
                run_id,
                progress=49,
                stage="hpo_tuning",
                log=(
                    f"HPO enabled (trials={int(hpo_cfg.n_trials)}, timeout={int(hpo_cfg.timeout_sec)}s, "
                    f"objective={hpo_cfg.objective_metric})."
                ),
            )
            hpo_trials = int(hpo_cfg.n_trials)
            if request.quick_mode:
                hpo_trials = max(5, min(hpo_trials, 10))

            if "xgb_lstm" in selected_models:
                tuned_model_config, hpo_summary_xgb = tune_xgb_hyperparameters(
                    feature_data=feature_data,
                    feature_columns=feature_columns,
                    config=model_config_active,
                    n_trials=hpo_trials,
                    timeout_sec=int(hpo_cfg.timeout_sec),
                    random_state=int(hpo_cfg.random_state),
                    objective_metric=str(hpo_cfg.objective_metric),
                )
                model_config_active = tuned_model_config
                save_json(run_dir / "hpo_summary_xgb_lstm.json", hpo_summary_xgb)
                append_log(
                    run_id,
                    f"HPO[xgb_lstm] status={hpo_summary_xgb.get('status')} best={hpo_summary_xgb.get('best_value')}",
                )

            if "lgbm_ranker" in selected_models:
                tuned_ranker_cfg_lgbm, hpo_summary_ranker = tune_ranker_hyperparameters(
                    feature_data=feature_data,
                    feature_columns=feature_columns,
                    walk_forward=walk_forward_cfg,
                    ranker_config=ranker_config_active_lgbm,
                    horizon_days=int(request.horizon_days),
                    n_trials=hpo_trials,
                    timeout_sec=int(hpo_cfg.timeout_sec),
                    random_state=int(hpo_cfg.random_state),
                    objective_metric=str(hpo_cfg.objective_metric),
                    backend="lightgbm",
                )
                ranker_config_active_lgbm = tuned_ranker_cfg_lgbm
                save_json(run_dir / "hpo_summary_lgbm_ranker.json", hpo_summary_ranker)
                append_log(
                    run_id,
                    f"HPO[lgbm_ranker] status={hpo_summary_ranker.get('status')} best={hpo_summary_ranker.get('best_value')}",
                )

            if "catboost_ranker" in selected_models:
                tuned_ranker_cfg_cat, hpo_summary_cat = tune_ranker_hyperparameters(
                    feature_data=feature_data,
                    feature_columns=feature_columns,
                    walk_forward=walk_forward_cfg,
                    ranker_config=ranker_config_active_catboost,
                    horizon_days=int(request.horizon_days),
                    n_trials=hpo_trials,
                    timeout_sec=int(hpo_cfg.timeout_sec),
                    random_state=int(hpo_cfg.random_state),
                    objective_metric=str(hpo_cfg.objective_metric),
                    backend="catboost",
                )
                ranker_config_active_catboost = tuned_ranker_cfg_cat
                save_json(run_dir / "hpo_summary_catboost_ranker.json", hpo_summary_cat)
                append_log(
                    run_id,
                    f"HPO[catboost_ranker] status={hpo_summary_cat.get('status')} best={hpo_summary_cat.get('best_value')}",
                )

            _mark_stage(
                run_id,
                progress=50,
                stage="training_prepare",
                log="HPO stage completed.",
            )

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
        save_json(
            run_dir / "config_used.json", request.model_dump(mode="json", by_alias=True)
        )
        data_versions_payload = get_data_versions()
        feature_versions_payload = get_feature_versions()
        save_json(
            run_dir / "data_versions.json",
            {
                "data": data_versions_payload,
                "features": feature_versions_payload,
            },
        )
        cutoff_iso = (
            pd.Timestamp(market_long["date"].max()).date().isoformat()
            if not market_long.empty
            else datetime.now(UTC).date().isoformat()
        )
        data_version = str(
            (data_versions_payload.get("data_version", "unknown"))
            if isinstance(data_versions_payload, dict)
            else "unknown"
        )
        feature_version = str(
            (feature_versions_payload.get("feature_version", "unknown"))
            if isinstance(feature_versions_payload, dict)
            else "unknown"
        )
        write_data_layer_meta(
            run_dir,
            layer="bronze",
            data_version=data_version,
            as_of_cutoff=cutoff_iso,
            quality_flags={"raw_market_data_rows": int(len(market_long))},
        )
        write_data_layer_meta(
            run_dir,
            layer="silver",
            data_version=data_version,
            as_of_cutoff=cutoff_iso,
            quality_flags={"symbols": int(len(datasets))},
        )
        write_data_layer_meta(
            run_dir,
            layer="gold",
            data_version=feature_version,
            as_of_cutoff=cutoff_iso,
            quality_flags={
                "feature_rows": int(len(feature_data)),
                "feature_columns": int(len(feature_columns)),
            },
        )
        for layer in ("bronze", "silver", "gold"):
            write_artifact_json(
                run_id,
                f"{layer}_layer_meta.json",
                load_json(run_dir / f"{layer}_layer_meta.json", default={}),
            )
        save_json(
            run_dir / "environment_fingerprint.json",
            {
                "python": sys.version,
                "python_executable": sys.executable,
                "platform": platform.platform(),
                "machine": platform.machine(),
                "created_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
            },
        )
        write_artifact_json(
            run_id,
            "environment_fingerprint.json",
            load_json(run_dir / "environment_fingerprint.json", default={}),
        )
        repro_command = (
            "PYTHONPATH=openbb_platform/extensions/quant_ml "
            "python -m openbb_quant_ml.jobs.cli weekly "
            "--config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs.yaml"
        )
        (run_dir / "repro_command.txt").write_text(repro_command, encoding="utf-8")
        write_artifact_text(run_id, "repro_command.txt", repro_command)
        _mark_stage(
            run_id,
            progress=52,
            stage="training_prepare",
            log="Saved market panel artifact.",
        )

        performance_rows: list[dict[str, Any]] = []
        model_windows: dict[str, tuple[int, int]] = {}
        if len(selected_models) == 1:
            model_windows[selected_models[0]] = (55, 92)
        else:
            # Keep fixed windows for stable UX when both models are requested.
            if "xgb_lstm" in selected_models:
                model_windows["xgb_lstm"] = (55, 71)
            if "lgbm_ranker" in selected_models:
                model_windows["lgbm_ranker"] = (72, 92)
            if "catboost_ranker" in selected_models:
                model_windows["catboost_ranker"] = (72, 92)

        if "xgb_lstm" in selected_models:
            xgb_start, xgb_end = model_windows.get("xgb_lstm", (55, 92))
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
                config=model_config_active,
                progress_callback=_xgb_progress,
            )
            _mark_elapsed("train_xgb_lstm_sec", t_train_xgb)
            update_run(run_id, progress=xgb_end, stage="training_xgb_lstm")
            baseline_pred = baseline_output.predictions.copy()
            baseline_pred["date"] = pd.to_datetime(
                baseline_pred["date"]
            ).dt.tz_localize(None)
            baseline_pred.to_parquet(
                run_dir / "predictions_xgb_lstm.parquet", index=False
            )

            baseline_ic = _compute_baseline_metrics(
                predictions=baseline_pred,
                split_ratio=model_config_active.train_val_split,
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

            baseline_output.xgb_model.save_model(
                str(run_dir / "model_xgb_xgb_lstm.json")
            )
            if baseline_output.lstm_bundle is not None:
                import torch

                torch.save(
                    _serialize_lstm_bundle(baseline_output.lstm_bundle),
                    run_dir / "model_lstm_xgb_lstm.pt",
                )

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
            _mark_stage(
                run_id,
                progress=ranker_start,
                stage="training_ranker",
                log="Training ranker model.",
            )
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
                ranker_config=ranker_config_active_lgbm,
                theta_grid=request.signal_config.theta_grid,
                horizon_days=int(request.horizon_days),
                progress_callback=_ranker_progress,
                backend="lightgbm",
            )
            _mark_elapsed("train_ranker_sec", t_train_ranker)
            update_run(run_id, progress=ranker_end, stage="training_ranker")
            ranker_pred = ranker_output.predictions.copy()
            ranker_pred["date"] = pd.to_datetime(ranker_pred["date"]).dt.tz_localize(
                None
            )
            ranker_pred.to_parquet(
                run_dir / "predictions_lgbm_ranker.parquet", index=False
            )

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
            trained_until = (
                pd.Timestamp(ranker_pred["date"].max()).date().isoformat()
                if not ranker_pred.empty
                else date.today().isoformat()
            )
            _save_ranker_inference_artifacts(
                run_dir,
                model=ranker_output.inference_model,
                feature_columns=ranker_output.feature_names,
                backend=ranker_output.inference_backend,
                trained_until=trained_until,
                mu_mapping=request.mu_mapping,
                label_return_map=ranker_output.label_return_map,
                label_return_fallback=ranker_output.label_return_fallback,
                model_name="lgbm_ranker",
            )

            ndcg_obj = ranker_output.metrics.get("ndcg", {})
            performance_rows.append(
                {
                    "model_name": "lgbm_ranker",
                    "train_ic": ranker_output.metrics.get("train_ic"),
                    "val_ic": ranker_output.metrics.get("val_ic"),
                    "ndcg": (
                        ndcg_obj.get("ndcg_10") if isinstance(ndcg_obj, dict) else None
                    ),
                    "hit_rate": ranker_output.metrics.get("hit_rate"),
                    "best_theta": ranker_output.metrics.get("best_theta"),
                }
            )

        if "catboost_ranker" in selected_models:
            ranker_start, ranker_end = model_windows.get("catboost_ranker", (50, 92))
            _mark_stage(
                run_id,
                progress=ranker_start,
                stage="training_ranker",
                log="Training CatBoost ranker model.",
            )
            t_train_catboost = time.perf_counter()
            catboost_log_progress = {"value": -1}

            def _catboost_progress(local_ratio: float, message: str) -> None:
                clipped = float(max(0.0, min(1.0, local_ratio)))
                progress = ranker_start + int((ranker_end - ranker_start) * clipped)
                update_run(run_id, progress=progress, stage="training_ranker")
                if progress - catboost_log_progress["value"] >= 5 or clipped >= 1.0:
                    append_log(run_id, f"[catboost_ranker] {message} ({progress}%)")
                    catboost_log_progress["value"] = progress

            catboost_output = train_ranker_models(
                feature_data=feature_data,
                feature_columns=feature_columns,
                walk_forward=walk_forward_cfg,
                ranker_config=ranker_config_active_catboost,
                theta_grid=request.signal_config.theta_grid,
                horizon_days=int(request.horizon_days),
                progress_callback=_catboost_progress,
                backend="catboost",
            )
            _mark_elapsed("train_ranker_sec", t_train_catboost)
            update_run(run_id, progress=ranker_end, stage="training_ranker")
            catboost_pred = catboost_output.predictions.copy()
            catboost_pred["date"] = pd.to_datetime(catboost_pred["date"]).dt.tz_localize(
                None
            )
            catboost_pred.to_parquet(
                run_dir / "predictions_catboost_ranker.parquet", index=False
            )

            catboost_metrics_payload: dict[str, Any] = {
                "model_name": "catboost_ranker",
                "metrics": catboost_output.metrics,
                "feature_importance": catboost_output.feature_importance,
                "model_meta": catboost_output.model_meta,
                "feature_columns": catboost_output.feature_names,
                "symbols_requested": symbols,
                "symbols_trained": sorted(list(datasets.keys())),
                "symbols_skipped": skipped_union,
                "target_mode": request.target_mode,
                "horizon_days": request.horizon_days,
            }
            save_json(run_dir / "metrics_catboost_ranker.json", catboost_metrics_payload)
            trained_until = (
                pd.Timestamp(catboost_pred["date"].max()).date().isoformat()
                if not catboost_pred.empty
                else date.today().isoformat()
            )
            _save_ranker_inference_artifacts(
                run_dir,
                model=catboost_output.inference_model,
                feature_columns=catboost_output.feature_names,
                backend=catboost_output.inference_backend,
                trained_until=trained_until,
                mu_mapping=request.mu_mapping,
                label_return_map=catboost_output.label_return_map,
                label_return_fallback=catboost_output.label_return_fallback,
                model_name="catboost_ranker",
            )

            ndcg_obj_cb = catboost_output.metrics.get("ndcg", {})
            performance_rows.append(
                {
                    "model_name": "catboost_ranker",
                    "train_ic": catboost_output.metrics.get("train_ic"),
                    "val_ic": catboost_output.metrics.get("val_ic"),
                    "ndcg": (
                        ndcg_obj_cb.get("ndcg_10")
                        if isinstance(ndcg_obj_cb, dict)
                        else None
                    ),
                    "hit_rate": catboost_output.metrics.get("hit_rate"),
                    "best_theta": catboost_output.metrics.get("best_theta"),
                }
            )

        _mark_stage(
            run_id,
            progress=95,
            stage="finalizing",
            log="Saving model performance summary.",
        )
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
        update_run(
            run_id, status="completed", progress=100, stage="completed", error=None
        )
        append_log(run_id, "Training job completed.")
    except Exception as exc:  # noqa: BLE001
        if time_profile:
            time_profile["total_training_sec"] = float(sum(time_profile.values()))
            save_json(run_dir / "time_profile.json", time_profile)
        update_run(
            run_id, status="failed", progress=100, stage="failed", error=str(exc)
        )
        append_log(run_id, f"Error: {exc}")
        append_log(run_id, traceback.format_exc(limit=3))


def submit_training(
    request: TrainRequest,
    *,
    run_id_scheme: str = "compact_v1",
    timezone: str = "Asia/Seoul",
) -> TrainResponse:
    """Queue a training job."""
    resolved_symbols = _resolve_symbols_for_training_request(request)
    resolved_request = request.model_copy(deep=True)
    resolved_request.symbols = resolved_symbols

    initialize_registry()
    state = create_run(run_id_scheme=run_id_scheme, timezone=timezone)
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
    run_dir = get_run_dir(run_id)
    run_context = ensure_run_context(run_dir, run_id) if run_dir.exists() else {}
    contract_manifest = load_json(
        run_dir / "artifacts" / "artifact_contract.json", default={}
    )
    if not isinstance(contract_manifest, dict):
        contract_manifest = {}
    payload = get_run_state_dict(run_id)
    if payload:
        payload = _recover_stale_running_run(run_id, payload)
        payload = _normalize_run_payload(payload)
        payload = _enrich_run_stale_fields(run_id, payload)
        payload["run_uid"] = (
            str(payload.get("run_uid", "")).strip()
            or str(run_context.get("run_uid", "")).strip()
            or None
        )
        payload["artifact_contract_version"] = (
            str(contract_manifest.get("artifact_contract_version", "") or "") or None
        )
        payload["required_artifacts_ready"] = bool(
            contract_manifest.get("required_artifacts_ready", False)
        )
        return RunStatusResponse(**payload)

    files = _run_artifact_files(run_id)
    if files:
        has_backtest = any(
            name.startswith("backtest") and name.endswith(".json") for name in files
        )
        has_predictions = any(
            name.startswith("predictions") and name.endswith(".parquet")
            for name in files
        )
        has_metrics = any(
            name.startswith("metrics") and name.endswith(".json") for name in files
        )
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
            run_uid=(str(run_context.get("run_uid", "")).strip() or None),
            status=status,  # type: ignore[arg-type]
            progress=progress,
            stage=stage,
            created_at=restored_at,
            updated_at=restored_at,
            last_heartbeat_at=restored_at,
            run_idle_minutes=0.0,
            stale_timeout_minutes=STALE_TIMEOUT_MINUTES,
            stale_reason=None,
            logs_tail=[
                log_message,
            ],
            error=None,
            artifact_contract_version=str(
                contract_manifest.get("artifact_contract_version", "") or ""
            )
            or None,
            required_artifacts_ready=bool(
                contract_manifest.get("required_artifacts_ready", False)
            ),
        )

    raise ValueError(f"Run not found: {run_id}")


def _ensure_run_completed(
    run_id: str, *, allow_artifact_fallback: bool = False
) -> None:
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
    metrics_payload = load_json(_metrics_path(request.run_id, model_name), default={})
    model_version = infer_model_version(
        metrics_payload if isinstance(metrics_payload, dict) else {}
    )
    feature_versions = get_feature_versions()
    feature_set_version = str(
        (
            feature_versions.get("feature_version")
            if isinstance(feature_versions, dict)
            else ""
        )
        or "unknown"
    )
    contract_signals = build_signal_contract(
        signal_rows=signal_df,
        as_of_date=as_of_iso,
        model_version=model_version,
        feature_set_version=feature_set_version,
    )
    write_artifact_parquet(request.run_id, "signals.parquet", contract_signals)
    latest_market_date = None
    market_path = run_dir / "market_data.parquet"
    if market_path.exists():
        market_long = pd.read_parquet(market_path, columns=["date"])
        if not market_long.empty:
            latest_market_date = (
                pd.Timestamp(pd.to_datetime(market_long["date"]).max())
                .date()
                .isoformat()
            )
    staleness_days = 0
    if latest_market_date:
        staleness_days = max(
            0,
            (
                pd.Timestamp(latest_market_date).date() - pd.Timestamp(as_of_iso).date()
            ).days,
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
    run_context = ensure_run_context(run_dir, request.run_id)
    market_path = run_dir / "market_data.parquet"
    if not market_path.exists():
        raise ValueError("Market data artifact is missing.")
    market_long = pd.read_parquet(market_path)
    market_long = market_long.assign(
        date=pd.to_datetime(market_long["date"]).dt.tz_localize(None)
    )
    close_panel = market_long.pivot(
        index="date", columns="symbol", values="close"
    ).sort_index()
    if "open" in market_long.columns:
        open_panel = market_long.pivot(
            index="date", columns="symbol", values="open"
        ).sort_index()
    else:
        open_panel = close_panel.copy()

    config_payload = load_json(run_dir / "config.json", default={})
    request_payload = (
        config_payload.get("request", {}) if isinstance(config_payload, dict) else {}
    )
    requested_universe_id = (
        str(request_payload.get("universe_id", "default")).strip() or "default"
    )
    universe_policy = get_universe_policy()

    predictions_for_backtest = predictions.copy()
    if "score" not in predictions_for_backtest.columns:
        predictions_for_backtest["score"] = pd.to_numeric(
            predictions_for_backtest.get("predicted_return"),
            errors="coerce",
        ).fillna(0.0)
    predictions_for_backtest["predicted_return"] = pd.to_numeric(
        predictions_for_backtest["score"], errors="coerce"
    ).fillna(0.0)

    pred_wide = predictions_for_backtest.pivot(
        index="date", columns="symbol", values="score"
    ).sort_index()
    window_mask = (close_panel.index.date >= request.start_date) & (
        close_panel.index.date <= request.end_date
    )
    trade_dates = close_panel.index[window_mask]
    rebalance_dates = [
        rebalance_date
        for rebalance_date in pd.Series(trade_dates, index=trade_dates)
        .groupby(trade_dates.to_period("M"))
        .first()
        .tolist()
        if rebalance_date in pred_wide.index
    ]
    if not rebalance_dates:
        overlap = [item for item in pred_wide.index if item in trade_dates]
        if overlap:
            rebalance_dates = [overlap[0]]

    rebalance_context: dict[str, dict[str, Any]] = {}
    for rebalance_date in rebalance_dates:
        snapshot = build_universe_snapshot(
            run_id=request.run_id,
            universe_id=requested_universe_id,
            as_of_date=pd.Timestamp(rebalance_date).date(),
            portfolio_mode=request.portfolio_mode,
            market_long=market_long,
        )
        rebalance_context[str(snapshot["as_of_date"])] = snapshot

    asof_manifest = build_asof_manifest(
        rebalance_dates=[pd.Timestamp(item).date() for item in rebalance_dates],
        fundamentals_lag_days=int(
            universe_policy.get("asof_policy", {}).get("fundamentals_lag_days", 60)
        ),
    )
    save_json(run_dir / "asof_inputs_manifest.json", asof_manifest)
    write_artifact_json(request.run_id, "asof_inputs_manifest.json", asof_manifest)

    delisting_events = load_delisting_events(run_dir)
    strict_delisting = bool(
        universe_policy.get("institutional_mode", {}).get(
            "delisting_require_event", False
        )
    )
    if strict_delisting:
        validate_delisting_events_required(
            close_panel=close_panel,
            events=delisting_events,
            end_date=pd.Timestamp(request.end_date),
        )

    result = run_backtest(
        predictions=predictions_for_backtest[
            ["date", "symbol", "predicted_return", "score"]
        ],
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
        rebalance_universe_context=rebalance_context,
        delisting_events=delisting_events,
    )

    report_by_date = {
        str(item.get("date")): item
        for item in result.rebalance_reports
        if isinstance(item, dict)
    }
    for history_row in result.rebalance_history_summary:
        report_date = str(history_row.get("date", "")).strip()
        if not report_date:
            continue
        try:
            as_of = date.fromisoformat(report_date)
        except ValueError:
            continue
        snap_dir = universe_snapshot_dir(run_dir, as_of)
        snap_dir.mkdir(parents=True, exist_ok=True)
        report = report_by_date.get(report_date, {})
        for filename, key in (
            ("position_sizing_log.parquet", "position_sizing_log"),
            ("liquidity_constraint_report.parquet", "liquidity_constraint_report"),
            ("risk_contribution_report.parquet", "risk_contribution_report"),
            ("sector_exposure_report.parquet", "sector_exposure_report"),
            ("country_exposure_report.parquet", "country_exposure_report"),
        ):
            rows = report.get(key, [])
            if not isinstance(rows, list):
                rows = []
            save_parquet_atomic(
                snap_dir / filename,
                pd.DataFrame(rows),
                index=False,
            )

    payload = {
        "run_id": request.run_id,
        "run_uid": str(run_context.get("run_uid", "")).strip() or None,
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
        "effective_constraints": result.effective_constraints,
        "cash_weight": result.cash_weight,
        "cost_bps": request.cost_bps,
        "slippage_bps": request.slippage_bps,
        "entry_price": request.entry_price,
        "exit_price": request.exit_price,
        "portfolio_mode": request.portfolio_mode,
        "mu_mapping": request.mu_mapping,
        "regime_policy": request.regime_policy,
        "rebalance_history_summary": result.rebalance_history_summary,
        "constraint_violations": result.constraint_violations,
        "liquidity_clip_ratio": result.liquidity_clip_ratio,
        "risk_contribution_max": result.risk_contribution_max,
        "universe_stage_counts": result.universe_stage_counts,
    }

    weights_final_frame = _period_weights_to_frame(result.period_weights)
    weights_target_frame = weights_final_frame.copy()
    constraints_log_frame = build_constraints_log(
        rebalance_reports=result.rebalance_reports,
        constraint_violations=result.constraint_violations,
    )
    constraints_summary = summarize_constraint_bindings(constraints_log_frame)
    trades_frame = pd.DataFrame(_derive_trade_plan_rows(result.period_weights))
    if trades_frame.empty:
        trades_frame = pd.DataFrame(
            columns=[
                "date",
                "ticker",
                "action",
                "weight_before",
                "weight_after",
                "weight_delta",
            ]
        )
    costs_frame = build_pnl_attribution(result.cost_breakdown)
    returns_daily_frame = pd.DataFrame(result.equity_curve)
    if returns_daily_frame.empty:
        returns_daily_frame = pd.DataFrame(
            columns=["date", "equity", "daily_return", "gross_return", "trading_cost"]
        )
    sector_exposure_frame = _latest_sector_exposure_frame(result.rebalance_reports)

    latest_snapshot = load_latest_universe_snapshot(request.run_id) or {}
    u2_symbols = latest_snapshot.get("u2_symbols", [])
    symbol_metrics = latest_snapshot.get("symbol_metrics", {})
    universe_rows: list[dict[str, Any]] = []
    if isinstance(u2_symbols, list):
        for symbol in u2_symbols:
            key = str(symbol).strip().upper()
            metrics = (
                symbol_metrics.get(key, {}) if isinstance(symbol_metrics, dict) else {}
            )
            universe_rows.append(
                {
                    "ticker": key,
                    "sector_l1": str(metrics.get("sector_l1", "other")),
                    "country": str(metrics.get("country", "US")).upper(),
                    "adv20_usd": _safe_float(metrics.get("adv20_usd"), default=0.0),
                }
            )
    universe_frame = pd.DataFrame(universe_rows)
    if universe_frame.empty:
        universe_frame = pd.DataFrame(
            columns=["ticker", "sector_l1", "country", "adv20_usd"]
        )
    exclusions_path = run_dir / "exclusions.parquet"
    exclusions_frame = (
        pd.read_parquet(exclusions_path)
        if exclusions_path.exists()
        else pd.DataFrame(
            columns=[
                "run_id",
                "rebalance_date",
                "ticker",
                "stage",
                "reason_code",
                "company_id",
                "raw_value",
            ]
        )
    )

    metrics_payload = load_json(_metrics_path(request.run_id, model_name), default={})
    model_version = infer_model_version(
        metrics_payload if isinstance(metrics_payload, dict) else {}
    )
    feature_versions = get_feature_versions()
    feature_set_version = str(
        (
            feature_versions.get("feature_version")
            if isinstance(feature_versions, dict)
            else ""
        )
        or "unknown"
    )
    latest_pred_date = (
        pd.Timestamp(predictions_for_backtest["date"].max()).date().isoformat()
    )
    signal_rows = predictions_for_backtest[
        predictions_for_backtest["date"] == predictions_for_backtest["date"].max()
    ][["symbol", "score"]].copy()
    signal_rows["predicted_return"] = signal_rows["score"]
    signal_rows["confidence"] = 0.5
    signal_rows["z_score"] = 0.0
    contract_signals = build_signal_contract(
        signal_rows=signal_rows,
        as_of_date=latest_pred_date,
        model_version=model_version,
        feature_set_version=feature_set_version,
    )

    write_artifact_parquet(request.run_id, "universe.parquet", universe_frame)
    write_artifact_parquet(request.run_id, "exclusions.parquet", exclusions_frame)
    write_artifact_parquet(request.run_id, "signals.parquet", contract_signals)
    write_artifact_parquet(
        request.run_id, "weights_target.parquet", weights_target_frame
    )
    write_artifact_parquet(request.run_id, "weights_final.parquet", weights_final_frame)
    write_artifact_parquet(
        request.run_id, "constraints_log.parquet", constraints_log_frame
    )
    write_artifact_parquet(request.run_id, "trades.parquet", trades_frame)
    write_artifact_parquet(request.run_id, "costs.parquet", costs_frame)
    write_artifact_parquet(request.run_id, "returns_daily.parquet", returns_daily_frame)
    write_artifact_parquet(
        request.run_id,
        "risk_summary.parquet",
        pd.DataFrame(
            [
                {
                    "run_id": request.run_id,
                    "model_name": model_name,
                    "volatility": _safe_float(
                        result.metrics.get("volatility"), default=0.0
                    ),
                    "max_drawdown": _safe_float(
                        result.metrics.get("max_drawdown"), default=0.0
                    ),
                    "cvar_95": _safe_float(
                        result.metrics.get("cvar_95"), default=0.0
                    ),
                    "risk_contribution_max": _safe_float(
                        result.risk_contribution_max, default=0.0
                    ),
                    "invalid_rebalance_count": int(
                        sum(
                            1
                            for item in result.constraint_violations
                            if str(item.get("type", "")).strip() == "invalid"
                        )
                    ),
                }
            ]
        ),
    )
    write_artifact_parquet(
        request.run_id, "exposures_sector.parquet", sector_exposure_frame
    )
    write_artifact_text(
        request.run_id,
        "report.html",
        build_report_html(
            {
                "run_id": request.run_id,
                "run_uid": run_context.get("run_uid"),
                "model_name": model_name,
                "metrics": result.metrics,
            }
        ),
    )
    contract_manifest = write_contract_manifest(request.run_id)

    payload = _json_sanitize(payload)
    payload["weights_target_available"] = bool(not weights_target_frame.empty)
    payload["weights_final_available"] = bool(not weights_final_frame.empty)
    payload["constraint_binding_summary"] = constraints_summary
    payload["artifact_contract_version"] = ARTIFACT_CONTRACT_VERSION
    payload["required_artifacts_ready"] = bool(
        contract_manifest.get("required_artifacts_ready", False)
    )
    save_json(_backtest_path(request.run_id, model_name), payload)
    if model_name == DEFAULT_MODEL:
        save_json(run_dir / "backtest.json", payload)
    try:
        refresh_alerts_for_run(run_id=request.run_id, model_name=model_name)
    except Exception:  # noqa: BLE001
        # Alerts are non-blocking post-processing outputs.
        pass

    return BacktestResponse(**payload)


def get_summary(
    run_id: str, model_name: ModelName = DEFAULT_MODEL
) -> ArtifactSummaryResponse:
    """Read artifact summary for a run."""
    model_name = _normalize_model_name(model_name)
    run_dir = get_run_dir(run_id)
    metrics = _load_metrics_payload(run_id, model_name=model_name)
    response = ArtifactSummaryResponse(
        run_id=run_id,
        model_name=model_name,
        model_meta=metrics.get("model_meta", {}),
        latest_validation_error=metrics.get("metrics", {}).get(
            "latest_validation_error"
        ),
        feature_importance=metrics.get("feature_importance", []),
        params=load_json(run_dir / "config.json", default={}),
        available_artifacts=list_run_artifacts(run_id),
    )
    return ArtifactSummaryResponse(**_json_sanitize(response.model_dump(mode="json")))


def get_universe() -> UniverseResponse:
    """Return active universe config."""
    payload = load_universe_config()
    return UniverseResponse(
        version=payload.get("version", "v1"), assets=payload.get("assets", [])
    )


def _extract_backtest_metric(backtest: dict[str, Any], key: str) -> float | None:
    metrics = backtest.get("metrics", {})
    value = metrics.get(key) if isinstance(metrics, dict) else None
    if value is None:
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if np.isnan(out) or np.isinf(out):
        return None
    return out


def get_model_performance(run_id: str) -> ModelPerformanceResponse:
    """Return model comparison metrics."""

    def _optional_metric(value: Any) -> float | None:
        out = _safe_float(value, default=float("nan"))
        if np.isnan(out) or np.isinf(out):
            return None
        return out

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
            train_ic=_optional_metric(
                metrics.get("train_ic") if isinstance(metrics, dict) else None
            ),
            val_ic=_optional_metric(
                metrics.get("val_ic") if isinstance(metrics, dict) else None
            ),
            ndcg=_optional_metric(ndcg_score),
            sharpe=_extract_backtest_metric(backtest_payload, "sharpe"),
            max_dd=_extract_backtest_metric(backtest_payload, "max_drawdown"),
            turnover=_extract_backtest_metric(backtest_payload, "turnover"),
            hit_rate=_optional_metric(
                metrics.get("hit_rate") if isinstance(metrics, dict) else None
            ),
            regime_performance=backtest_payload.get("regime_performance", {}),
        )
        models.append(item)

    if not models:
        raise ValueError(f"No model metrics found for run: {run_id}")
    response = ModelPerformanceResponse(run_id=run_id, models=models)
    return ModelPerformanceResponse(**_json_sanitize(response.model_dump(mode="json")))


def get_model_ic(
    run_id: str, model_name: ModelName = DEFAULT_MODEL, window: int = 6
) -> ModelICResponse:
    """Return IC time-series for a model."""
    model_name = _normalize_model_name(model_name)
    predictions = _load_predictions(run_id, model_name=model_name).dropna(
        subset=["target_return"]
    )
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
    frame["rolling_ic"] = (
        frame["ic"].rolling(window=max(window, 1), min_periods=1).mean()
    )
    points = [
        ModelICPoint(
            date=row["date"], ic=float(row["ic"]), rolling_ic=float(row["rolling_ic"])
        )
        for _, row in frame.iterrows()
    ]
    return ModelICResponse(
        run_id=run_id, model_name=model_name, window=max(window, 1), points=points
    )


def _load_close_panel(run_id: str) -> pd.DataFrame:
    market_path = get_run_dir(run_id) / "market_data.parquet"
    if not market_path.exists():
        return pd.DataFrame()
    market_long = pd.read_parquet(market_path)
    panel = (
        market_long.assign(
            date=pd.to_datetime(market_long["date"]).dt.tz_localize(None)
        )
        .pivot(index="date", columns="symbol", values="close")
        .sort_index()
    )
    return panel


def _signal_regime_snapshot(run_id: str) -> tuple[dict[str, str], str]:
    close_panel = _load_close_panel(run_id)
    if close_panel.empty:
        return {}, "long_only"
    benchmark_symbol = (
        "SPY" if "SPY" in close_panel.columns else str(close_panel.columns[0])
    )
    benchmark = close_panel[benchmark_symbol].dropna().astype(float)
    benchmark.index = pd.to_datetime(benchmark.index).tz_localize(None)
    if benchmark.empty:
        return {}, "long_only"

    ret = (
        benchmark.pct_change(fill_method=None)
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )
    ma200 = benchmark.rolling(200, min_periods=20).mean()
    distance = benchmark / (ma200 + 1e-12) - 1.0
    trend = (
        "bull"
        if float(distance.iloc[-1]) > 0.01
        else "bear" if float(distance.iloc[-1]) < -0.01 else "sideways"
    )
    vol20 = ret.rolling(20, min_periods=5).std(ddof=0) * np.sqrt(252)
    low_q = float(vol20.quantile(0.33))
    high_q = float(vol20.quantile(0.66))
    latest_vol = float(vol20.iloc[-1]) if not np.isnan(float(vol20.iloc[-1])) else 0.0
    vol_regime = (
        "low" if latest_vol <= low_q else "high" if latest_vol >= high_q else "mid"
    )

    recommended_mode = (
        "long_short"
        if trend == "bull" and vol_regime in {"low", "mid"}
        else "long_only"
    )
    return {"trend_regime": trend, "vol_regime": vol_regime}, recommended_mode


def get_model_regime(
    run_id: str, model_name: ModelName = DEFAULT_MODEL
) -> ModelRegimeResponse:
    """Return legacy regime payload mapped from dashboard regime metrics."""
    model_name = _normalize_model_name(model_name)
    try:
        regime_payload = get_dashboard_performance_regime(
            run_id=run_id, model_name=model_name
        )
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


def get_feature_importance(
    run_id: str, model_name: ModelName = DEFAULT_MODEL
) -> FeatureImportanceResponse:
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
    latest = latest.sort_values("predicted_return", ascending=False).head(
        max(int(top_k), 1)
    )
    rows = latest[
        [
            "symbol",
            "predicted_return",
            "target_return",
            "z_score",
            "side",
            "predicted_xgb",
            "predicted_lstm",
        ]
    ].to_dict(orient="records")
    response = PredictionsLatestResponse(
        run_id=run_id,
        model_name=model_name,
        as_of_date=latest_date,
        predictions=_json_sanitize(rows),
    )
    return PredictionsLatestResponse(**_json_sanitize(response.model_dump(mode="json")))


def _collapse_small_categories(
    weights: dict[str, float], cutoff: float = 0.01
) -> dict[str, float]:
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


def get_portfolio_current(
    run_id: str, model_name: ModelName = DEFAULT_MODEL
) -> PortfolioCurrentResponse:
    """Return latest rebalance portfolio and rationale."""
    _ensure_run_completed(run_id, allow_artifact_fallback=True)
    model_name = _normalize_model_name(model_name)
    policy = get_portfolio_policy()
    policy_max_weight = float(policy.get("single_name_max_abs_weight", 0.10))
    cash_symbol = str(policy.get("cash_symbol", "CASH")).strip().upper() or "CASH"
    cash_category = (
        str(policy.get("cash_category", "cash_proxy")).strip() or "cash_proxy"
    )

    try:
        backtest_payload = _load_backtest_payload(run_id, model_name=model_name)
    except ValueError as exc:
        raise ValueError("Run backtest first for selected model.") from exc

    period_weights = backtest_payload.get("period_weights", [])
    history_rows = backtest_payload.get("rebalance_history_summary", [])
    constraints = backtest_payload.get(
        "constraints",
        {
            "max_weight": policy_max_weight,
            "long_only": True,
            "risk_aversion": 3.0,
            "lookback_days": 126,
        },
    )
    effective_constraints = backtest_payload.get("effective_constraints", {})
    cost_bps = float(backtest_payload.get("cost_bps", 10.0))
    requested_max_weight = _safe_float(
        constraints.get("max_weight"), default=policy_max_weight
    )
    applied_max_weight = _safe_float(
        effective_constraints.get("max_weight"), default=requested_max_weight
    )

    if not period_weights:
        rationale = PortfolioRationale(
            summary_lines=[
                "백테스트 결과에 저장된 리밸런싱 비중이 아직 없습니다.",
                "현재는 자산군 비중을 계산할 수 없어 포트폴리오를 비워서 표시합니다.",
                "먼저 Run Backtest를 실행하면 최신 리밸런싱 비중과 설명이 생성됩니다.",
            ],
            constraints_applied={
                "max_weight_requested": requested_max_weight,
                "max_weight_applied": applied_max_weight,
                "max_weight": applied_max_weight,
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
            asset_class_weights_l1=[],
            rationale=rationale,
            last_rebalance_trades=None,
            last_rebalance_turnover=0.0,
        )

    latest = period_weights[-1]
    as_of_date = str(latest.get("date"))
    raw_weights: dict[str, float] = {}
    for symbol, weight in dict(latest.get("weights", {})).items():
        symbol_key = str(symbol).strip().upper()
        if not symbol_key:
            continue
        safe_weight = _safe_float(weight, default=0.0)
        if safe_weight > 0:
            raw_weights[symbol_key] = safe_weight
    total_weight = float(sum(raw_weights.values()))
    if total_weight <= 0:
        total_weight = 1.0

    symbol_metadata = get_symbol_metadata_map()

    symbol_items: list[PortfolioSymbolWeightItem] = []
    category_weights_l2: dict[str, float] = {}
    category_weights_l1: dict[str, float] = {}
    for symbol, weight in sorted(
        raw_weights.items(), key=lambda pair: pair[1], reverse=True
    ):
        normalized = _safe_float(weight / total_weight, default=0.0)
        if symbol == cash_symbol:
            metadata = {
                "name": "Cash Buffer",
                "market": "CASH",
                "sector_l1": "cash",
                "category_l2": cash_category,
                "category": cash_category,
            }
        else:
            metadata = symbol_metadata.get(symbol, {})
        category_l2 = (
            str(
                metadata.get("category_l2") or metadata.get("category") or "other"
            ).strip()
            or "other"
        )
        sector_l1 = str(metadata.get("sector_l1") or "other").strip() or "other"
        name = str(metadata.get("name", "")).strip() or None
        market = str(metadata.get("market", "")).strip() or None

        symbol_items.append(
            PortfolioSymbolWeightItem(
                symbol=symbol,
                weight=normalized,
                category=category_l2,
                name=name,
                market=market,
                sector_l1=sector_l1,
                category_l2=category_l2,
            ),
        )
        category_weights_l2[category_l2] = (
            category_weights_l2.get(category_l2, 0.0) + normalized
        )
        category_weights_l1[sector_l1] = (
            category_weights_l1.get(sector_l1, 0.0) + normalized
        )

    category_weights_l2 = _collapse_small_categories(category_weights_l2, cutoff=0.01)
    category_weights_l1 = _collapse_small_categories(category_weights_l1, cutoff=0.01)
    asset_items = [
        AssetClassWeightItem(category=category, weight=value)
        for category, value in sorted(
            category_weights_l2.items(), key=lambda pair: pair[1], reverse=True
        )
    ]
    asset_items_l1 = [
        AssetClassWeightItem(category=category, weight=value)
        for category, value in sorted(
            category_weights_l1.items(), key=lambda pair: pair[1], reverse=True
        )
    ]

    top_categories = asset_items[:2]
    top_symbols = symbol_items[:3]
    top_cat_text = (
        ", ".join(
            f"{item.category} {_round_pct(item.weight)}" for item in top_categories
        )
        or "구성 없음"
    )
    top_cat_total = sum(item.weight for item in top_categories)
    top_symbol_text = (
        ", ".join(
            f"{(item.name + f'({item.symbol})') if item.name else item.symbol} {_round_pct(item.weight)}"
            for item in top_symbols
        )
        or "구성 없음"
    )
    top_category_name = top_categories[0].category if top_categories else "other"

    summary_lines = [
        f"최신 리밸런싱({as_of_date}) 기준 상위 자산군은 {top_cat_text}이며 합계는 {_round_pct(top_cat_total)}입니다.",
        f"상위 비중 종목({top_symbol_text})이 {top_category_name}에 집중되어 해당 자산군 비중이 확대되었습니다.",
        (
            f"요청 상한 {_round_pct(requested_max_weight)} 대비 정책 하드캡 적용 상한은 "
            f"{_round_pct(applied_max_weight)}입니다."
        ),
    ]
    rationale = PortfolioRationale(
        summary_lines=summary_lines,
        constraints_applied={
            "max_weight_requested": requested_max_weight,
            "max_weight_applied": applied_max_weight,
            "max_weight": applied_max_weight,
            "long_only": bool(constraints.get("long_only", True)),
            "risk_aversion": float(constraints.get("risk_aversion", 3.0)),
            "lookback_days": float(constraints.get("lookback_days", 126)),
            "cost_bps": cost_bps,
        },
    )
    last_rebalance = None
    if isinstance(history_rows, list) and history_rows:
        try:
            last_rebalance = RebalanceHistoryItem(**history_rows[-1])
        except Exception:  # noqa: BLE001
            last_rebalance = None

    response = PortfolioCurrentResponse(
        run_id=run_id,
        model_name=model_name,
        as_of_date=as_of_date,
        total_weight=_safe_float(
            sum(item.weight for item in symbol_items), default=0.0
        ),
        symbol_weights=symbol_items,
        asset_class_weights=asset_items,
        asset_class_weights_l1=asset_items_l1,
        rationale=rationale,
        last_rebalance_trades=last_rebalance,
        last_rebalance_turnover=(
            _safe_float(last_rebalance.turnover, default=0.0)
            if last_rebalance is not None
            else 0.0
        ),
    )
    return PortfolioCurrentResponse(**_json_sanitize(response.model_dump(mode="json")))


def get_rebalance_history(
    run_id: str, model_name: ModelName = DEFAULT_MODEL
) -> RebalanceHistoryResponse:
    """Return rebalance add/sell timeline for a backtest artifact."""
    _ensure_run_completed(run_id, allow_artifact_fallback=True)
    model_name = _normalize_model_name(model_name)
    payload = _load_backtest_payload(run_id, model_name=model_name)
    rows = payload.get("rebalance_history_summary", [])
    items: list[RebalanceHistoryItem] = []
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            try:
                items.append(RebalanceHistoryItem(**row))
            except Exception:  # noqa: BLE001
                continue
    response = RebalanceHistoryResponse(
        run_id=run_id,
        model_name=model_name,
        items=items,
    )
    return RebalanceHistoryResponse(**_json_sanitize(response.model_dump(mode="json")))


def get_universe_snapshot(run_id: str) -> UniverseSnapshotResponse:
    """Return latest persisted U0/U1/U2 snapshot for a run."""
    _ensure_run_completed(run_id, allow_artifact_fallback=True)
    snapshot = load_latest_universe_snapshot(run_id)
    if not snapshot:
        raise ValueError("Universe snapshot is unavailable. Run backtest first.")
    response = UniverseSnapshotResponse(
        run_id=run_id,
        as_of_date=str(snapshot.get("as_of_date", "")),
        universe_id=str(snapshot.get("universe_id", "default")),
        stage_counts={
            key: int(value)
            for key, value in dict(snapshot.get("stage_counts", {})).items()
        },
        u0_symbols=[str(item) for item in snapshot.get("u0_symbols", [])],
        u1_symbols=[str(item) for item in snapshot.get("u1_symbols", [])],
        u2_symbols=[str(item) for item in snapshot.get("u2_symbols", [])],
        excluded=[
            UniverseExclusionItem(**row)
            for row in load_latest_universe_exclusions(run_id)
        ],
    )
    return UniverseSnapshotResponse(**_json_sanitize(response.model_dump(mode="json")))


def get_universe_exclusions(run_id: str) -> list[UniverseExclusionItem]:
    """Return latest universe exclusion rows for one run."""
    _ensure_run_completed(run_id, allow_artifact_fallback=True)
    rows = load_latest_universe_exclusions(run_id)
    return [
        UniverseExclusionItem(**_json_sanitize(row))
        for row in rows
        if isinstance(row, dict)
    ]
