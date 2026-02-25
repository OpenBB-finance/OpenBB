"""Step: evaluate candidate run with absolute + champion/challenger gates."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.service.runtime_pointer import get_promoted_model
from openbb_quant_ml.service.storage import get_run_dir, load_json, save_json


def _load_metrics_block(run_dir, model_name: str) -> dict[str, Any]:
    backtest_payload = load_json(run_dir / f"backtest_{model_name}.json", default={})
    if not isinstance(backtest_payload, dict) or not backtest_payload:
        backtest_payload = load_json(run_dir / "backtest.json", default={})

    metrics_payload = load_json(run_dir / f"metrics_{model_name}.json", default={})
    if not isinstance(metrics_payload, dict) or not metrics_payload:
        metrics_payload = load_json(run_dir / "metrics.json", default={})

    bt_metrics = (
        backtest_payload.get("metrics", {})
        if isinstance(backtest_payload.get("metrics", {}), dict)
        else {}
    )
    train_metrics = (
        metrics_payload.get("metrics", {})
        if isinstance(metrics_payload.get("metrics", {}), dict)
        else {}
    )
    return {
        "sharpe": float(bt_metrics.get("sharpe", 0.0) or 0.0),
        "max_drawdown": float(bt_metrics.get("max_drawdown", 0.0) or 0.0),
        "turnover": float(bt_metrics.get("turnover", 0.0) or 0.0),
        "val_ic": float(train_metrics.get("val_ic", train_metrics.get("train_ic", 0.0)) or 0.0),
    }


def run(config: dict[str, Any]) -> dict[str, Any]:
    run_id = str(config.get("run_id", "")).strip()
    if not run_id:
        return {"status": "skipped", "message": "run_id is not configured"}
    model_name = str(config.get("model_name", "lgbm_ranker"))

    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        return {"status": "skipped", "message": f"run not found: {run_id}", "run_id": run_id}

    candidate = _load_metrics_block(run_dir, model_name)
    thresholds = config.get("promote_thresholds", {})
    if not isinstance(thresholds, dict):
        thresholds = {}
    sharpe_min = float(thresholds.get("sharpe_min", 0.1))
    max_drawdown_min = float(thresholds.get("max_drawdown_min", -0.4))
    turnover_max = float(thresholds.get("turnover_max", 3.0))
    val_ic_min = float(thresholds.get("val_ic_min", -1.0))

    absolute_failures: list[str] = []
    if candidate["sharpe"] < sharpe_min:
        absolute_failures.append(f"sharpe<{sharpe_min}")
    if candidate["max_drawdown"] < max_drawdown_min:
        absolute_failures.append(f"max_drawdown<{max_drawdown_min}")
    if candidate["turnover"] > turnover_max:
        absolute_failures.append(f"turnover>{turnover_max}")
    if candidate["val_ic"] < val_ic_min:
        absolute_failures.append(f"val_ic<{val_ic_min}")

    incumbent_payload = get_promoted_model(model_name=model_name)
    incumbent_run_id = str(incumbent_payload.get("run_id") or "").strip()
    incumbent: dict[str, float] | None = None
    non_inferiority_failures: list[str] = []
    if incumbent_run_id and incumbent_run_id != run_id:
        incumbent_dir = get_run_dir(incumbent_run_id)
        if incumbent_dir.exists():
            incumbent = _load_metrics_block(incumbent_dir, model_name)
            tolerance_cfg = config.get("non_inferiority_tolerance", {})
            if not isinstance(tolerance_cfg, dict):
                tolerance_cfg = {}
            sharpe_tol = float(tolerance_cfg.get("sharpe", 0.10))
            val_ic_tol = float(tolerance_cfg.get("val_ic", 0.01))
            maxdd_tol = float(tolerance_cfg.get("max_drawdown", 0.03))
            turnover_tol = float(tolerance_cfg.get("turnover", 0.20))

            if candidate["sharpe"] < (incumbent["sharpe"] - sharpe_tol):
                non_inferiority_failures.append("sharpe_non_inferiority")
            if candidate["val_ic"] < (incumbent["val_ic"] - val_ic_tol):
                non_inferiority_failures.append("val_ic_non_inferiority")
            if candidate["max_drawdown"] < (incumbent["max_drawdown"] - maxdd_tol):
                non_inferiority_failures.append("max_drawdown_non_inferiority")
            if candidate["turnover"] > (incumbent["turnover"] + turnover_tol):
                non_inferiority_failures.append("turnover_non_inferiority")

    passed = not absolute_failures and not non_inferiority_failures
    report = {
        "status": "ok",
        "run_id": run_id,
        "model_name": model_name,
        "passed": bool(passed),
        "candidate_metrics": candidate,
        "incumbent_run_id": incumbent_run_id or None,
        "incumbent_metrics": incumbent,
        "absolute_failures": absolute_failures,
        "non_inferiority_failures": non_inferiority_failures,
    }
    save_json(run_dir / "evaluation_gate.json", report)
    return report
