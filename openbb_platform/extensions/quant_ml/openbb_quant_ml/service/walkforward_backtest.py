"""Asynchronous walk-forward backtest service."""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from openbb_quant_ml.models import (
    BacktestMetrics,
    WalkForwardBacktestRequest,
    WalkForwardBacktestStatusResponse,
    WalkForwardBacktestSubmitResponse,
)
from openbb_quant_ml.service.backtest import run_backtest
from openbb_quant_ml.service.constants import WALKFORWARD_JOBS_PATH
from openbb_quant_ml.service.storage import (
    get_run_dir,
    load_json,
    save_json,
    save_parquet_atomic,
)

_WF_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="quant-ml-wf")
_WF_FUTURES: dict[str, Future] = {}


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _load_jobs_payload() -> dict[str, Any]:
    payload = load_json(WALKFORWARD_JOBS_PATH, default={"jobs": {}})
    if not isinstance(payload, dict):
        return {"jobs": {}}
    jobs = payload.get("jobs")
    if not isinstance(jobs, dict):
        payload["jobs"] = {}
    return payload


def _save_jobs_payload(payload: dict[str, Any]) -> None:
    save_json(WALKFORWARD_JOBS_PATH, payload)


def _next_job_id() -> str:
    payload = _load_jobs_payload()
    jobs = payload.get("jobs", {})
    if not isinstance(jobs, dict):
        jobs = {}
    token = datetime.now(UTC).strftime("%y%m%d")
    prefix = f"wf-{token}-"
    highest = 0
    for job_id in jobs.keys():
        if not str(job_id).startswith(prefix):
            continue
        suffix = str(job_id).replace(prefix, "")
        try:
            highest = max(highest, int(suffix))
        except ValueError:
            continue
    return f"{prefix}{highest + 1:03d}"


def _upsert_job(job_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    payload = _load_jobs_payload()
    jobs = payload.setdefault("jobs", {})
    if not isinstance(jobs, dict):
        payload["jobs"] = {}
        jobs = payload["jobs"]
    row = jobs.get(job_id, {})
    if not isinstance(row, dict):
        row = {}
    row.update(patch)
    row["job_id"] = job_id
    row["updated_at"] = _now_iso()
    jobs[job_id] = row
    _save_jobs_payload(payload)
    return row


def _job_row(job_id: str) -> dict[str, Any] | None:
    payload = _load_jobs_payload()
    jobs = payload.get("jobs", {})
    if not isinstance(jobs, dict):
        return None
    row = jobs.get(job_id)
    return row if isinstance(row, dict) else None


def _rebalance_dates(index: pd.DatetimeIndex) -> list[pd.Timestamp]:
    if index.empty:
        return []
    frame = pd.DataFrame({"date": index})
    frame["bucket"] = frame["date"].dt.to_period("M")
    rows = frame.groupby("bucket")["date"].min().tolist()
    return [pd.Timestamp(item).tz_localize(None) for item in rows]


def _json_sanitize(value: Any) -> Any:
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


def _load_predictions(run_dir: Path, model_name: str) -> pd.DataFrame:
    candidates = [
        run_dir / f"predictions_{model_name}.parquet",
        run_dir / "predictions.parquet",
    ]
    for path in candidates:
        if not path.exists():
            continue
        frame = pd.read_parquet(path)
        if frame.empty:
            continue
        frame["date"] = pd.to_datetime(frame["date"]).dt.tz_localize(None)
        return frame.sort_values(["date", "symbol"]).reset_index(drop=True)
    raise ValueError("Prediction artifacts are missing.")


def _load_market_panels(run_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    market_path = run_dir / "market_data.parquet"
    if not market_path.exists():
        raise ValueError("Market data artifact is missing.")
    market = pd.read_parquet(market_path)
    if market.empty:
        raise ValueError("Market data artifact is empty.")
    market["date"] = pd.to_datetime(market["date"]).dt.tz_localize(None)
    close_panel = market.pivot(
        index="date", columns="symbol", values="close"
    ).sort_index()
    if "open" in market.columns:
        open_panel = market.pivot(
            index="date", columns="symbol", values="open"
        ).sort_index()
    else:
        open_panel = close_panel.copy()
    return open_panel, close_panel


def _build_walkforward_predictions(
    predictions: pd.DataFrame,
    trade_dates: pd.DatetimeIndex,
    *,
    start_date,
    end_date,
    min_history_days: int,
) -> tuple[pd.DataFrame, list[dict[str, str]]]:
    rebalances = [
        date_value
        for date_value in _rebalance_dates(trade_dates)
        if date_value.date() >= start_date and date_value.date() <= end_date
    ]
    if not rebalances:
        raise ValueError("No rebalance dates available in selected window.")

    windows: list[dict[str, str]] = []
    rows: list[dict[str, Any]] = []
    for rebalance_date in rebalances:
        train_cut = rebalance_date - pd.Timedelta(days=1)
        train_frame = predictions[predictions["date"] <= train_cut]
        if train_frame.empty:
            continue
        if train_frame["date"].nunique() < max(20, int(min_history_days // 3)):
            continue
        train_until = pd.Timestamp(train_frame["date"].max()).tz_localize(None)
        if train_until >= rebalance_date:
            train_until = rebalance_date - pd.Timedelta(days=1)
        if train_until < pd.Timestamp(start_date):
            continue
        latest_per_symbol = (
            train_frame.sort_values(["date", "symbol"])
            .groupby("symbol", as_index=False)
            .tail(1)
        )
        for _, row in latest_per_symbol.iterrows():
            rows.append(
                {
                    "date": rebalance_date,
                    "symbol": str(row["symbol"]),
                    "predicted_return": float(row["predicted_return"]),
                }
            )
        windows.append(
            {
                "rebalance_date": rebalance_date.date().isoformat(),
                "train_until": train_until.date().isoformat(),
            }
        )

    if not rows:
        raise ValueError("Walk-forward prediction set is empty.")
    output = pd.DataFrame(rows)
    output["date"] = pd.to_datetime(output["date"]).dt.tz_localize(None)
    output = output.sort_values(["date", "symbol"]).reset_index(drop=True)
    return output, windows


def _to_period_weights_frame(period_weights: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in period_weights:
        date_value = row.get("date")
        weights = row.get("weights", {})
        if not date_value or not isinstance(weights, dict):
            continue
        for symbol, weight in weights.items():
            rows.append(
                {
                    "date": str(date_value),
                    "symbol": str(symbol),
                    "weight": float(weight),
                }
            )
    return pd.DataFrame(rows)


def _run_walkforward_job(job_id: str, request_payload: dict[str, Any]) -> None:
    request = WalkForwardBacktestRequest(**request_payload)
    run_dir = get_run_dir(request.run_id)
    artifact_dir = run_dir / "walkforward" / job_id
    artifact_dir.mkdir(parents=True, exist_ok=True)

    _upsert_job(
        job_id, {"status": "running", "progress": 5, "artifact_root": str(artifact_dir)}
    )
    try:
        predictions = _load_predictions(run_dir, request.model_name)
        open_panel, close_panel = _load_market_panels(run_dir)
        _upsert_job(job_id, {"progress": 35})

        trade_dates = close_panel.index[
            (close_panel.index >= pd.Timestamp(request.start_date))
            & (close_panel.index <= pd.Timestamp(request.end_date))
        ]
        wf_predictions, train_windows = _build_walkforward_predictions(
            predictions,
            trade_dates=trade_dates,
            start_date=request.start_date,
            end_date=request.end_date,
            min_history_days=request.min_history_days,
        )
        _upsert_job(job_id, {"progress": 65, "train_windows": train_windows})

        result = run_backtest(
            predictions=wf_predictions,
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

        metrics_payload = _json_sanitize(result.metrics)
        save_json(artifact_dir / "metrics.json", metrics_payload)
        save_json(artifact_dir / "train_windows.json", train_windows)
        save_parquet_atomic(
            artifact_dir / "equity_curve.parquet",
            pd.DataFrame(result.equity_curve),
            index=False,
        )
        save_parquet_atomic(
            artifact_dir / "period_weights.parquet",
            _to_period_weights_frame(result.period_weights),
            index=False,
        )

        _upsert_job(
            job_id,
            {
                "status": "completed",
                "progress": 100,
                "artifact_root": str(artifact_dir),
                "metrics": metrics_payload,
                "train_windows": train_windows,
                "message": "walk-forward backtest completed",
            },
        )
    except Exception as exc:  # noqa: BLE001
        _upsert_job(
            job_id,
            {
                "status": "failed",
                "progress": 100,
                "artifact_root": str(artifact_dir),
                "message": str(exc),
            },
        )


def submit_walkforward_backtest(
    request: WalkForwardBacktestRequest,
) -> WalkForwardBacktestSubmitResponse:
    """Submit asynchronous walk-forward backtest job."""
    run_dir = get_run_dir(request.run_id)
    if not run_dir.exists():
        raise ValueError(f"Run not found: {request.run_id}")

    job_id = _next_job_id()
    created_at = _now_iso()
    _upsert_job(
        job_id,
        {
            "status": "queued",
            "progress": 0,
            "run_id": request.run_id,
            "model_name": request.model_name,
            "created_at": created_at,
            "request": request.model_dump(mode="json"),
            "message": "walk-forward job queued",
        },
    )
    future = _WF_EXECUTOR.submit(
        _run_walkforward_job,
        job_id,
        request.model_dump(mode="json"),
    )
    _WF_FUTURES[job_id] = future
    return WalkForwardBacktestSubmitResponse(
        job_id=job_id,
        status="queued",
        run_id=request.run_id,
        model_name=request.model_name,
        created_at=created_at,
    )


def get_walkforward_backtest_status(job_id: str) -> WalkForwardBacktestStatusResponse:
    """Get walk-forward job status."""
    row = _job_row(job_id)
    if row is None:
        return WalkForwardBacktestStatusResponse(
            job_id=job_id,
            status="not_found",
            run_id="",
            model_name="lgbm_ranker",
            message="walk-forward job not found",
        )

    metrics_payload = row.get("metrics")
    metrics = None
    if isinstance(metrics_payload, dict) and metrics_payload:
        metrics = BacktestMetrics(**_json_sanitize(metrics_payload))

    run_id = str(row.get("run_id", ""))
    model_name = str(row.get("model_name", "lgbm_ranker"))
    return WalkForwardBacktestStatusResponse(
        job_id=job_id,
        status=str(row.get("status", "queued")),  # type: ignore[arg-type]
        run_id=run_id,
        model_name=model_name,  # type: ignore[arg-type]
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
        artifact_root=row.get("artifact_root"),
        progress=int(row.get("progress", 0)),
        metrics=metrics,
        message=row.get("message"),
        train_windows=(
            row.get("train_windows", [])
            if isinstance(row.get("train_windows"), list)
            else []
        ),
    )


def get_walkforward_queue_depth() -> int:
    """Return number of queued/running walk-forward jobs."""
    payload = _load_jobs_payload()
    jobs = payload.get("jobs", {})
    if not isinstance(jobs, dict):
        return 0
    depth = 0
    for row in jobs.values():
        if not isinstance(row, dict):
            continue
        if str(row.get("status", "")).lower() in {"queued", "running"}:
            depth += 1
    return depth
