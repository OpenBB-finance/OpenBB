"""Step: promote model candidate using configurable thresholds."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.service.runtime_pointer import get_promoted_model, set_promoted_model_pointer
from openbb_quant_ml.service.storage import get_run_dir, load_json


def _load_metric_bundle(run_dir, model_name: str) -> dict[str, float]:
    backtest_payload = load_json(run_dir / f"backtest_{model_name}.json", default={})
    if not isinstance(backtest_payload, dict) or not backtest_payload:
        backtest_payload = load_json(run_dir / "backtest.json", default={})
    metrics_payload = load_json(run_dir / f"metrics_{model_name}.json", default={})
    if not isinstance(metrics_payload, dict) or not metrics_payload:
        metrics_payload = load_json(run_dir / "metrics.json", default={})

    metrics_block = (
        backtest_payload.get("metrics", {})
        if isinstance(backtest_payload.get("metrics", {}), dict)
        else {}
    )
    train_metric_block = (
        metrics_payload.get("metrics", {})
        if isinstance(metrics_payload.get("metrics", {}), dict)
        else {}
    )
    return {
        "sharpe": float(metrics_block.get("sharpe", 0.0) or 0.0),
        "max_drawdown": float(metrics_block.get("max_drawdown", 0.0) or 0.0),
        "turnover": float(metrics_block.get("turnover", 0.0) or 0.0),
        "val_ic": float(
            train_metric_block.get("val_ic", train_metric_block.get("train_ic", 0.0)) or 0.0
        ),
    }


def run(config: dict[str, Any]) -> dict[str, Any]:
    run_id = config.get("run_id")
    if not run_id:
        return {"status": "skipped", "message": "run_id is not configured"}

    model_name = str(config.get("model_name", "lgbm_ranker"))
    run_dir = get_run_dir(str(run_id))
    if not run_dir.exists():
        return {
            "status": "skipped",
            "message": f"run not found: {run_id}",
            "run_id": run_id,
        }

    metrics = _load_metric_bundle(run_dir, model_name)
    sharpe = metrics["sharpe"]
    max_drawdown = metrics["max_drawdown"]
    turnover = metrics["turnover"]
    val_ic = metrics["val_ic"]

    thresholds = config.get("promote_thresholds", {})
    if not isinstance(thresholds, dict):
        thresholds = {}
    sharpe_min = float(thresholds.get("sharpe_min", 0.1))
    max_drawdown_min = float(thresholds.get("max_drawdown_min", -0.4))
    turnover_max = float(thresholds.get("turnover_max", 3.0))
    val_ic_min = float(thresholds.get("val_ic_min", -1.0))

    failures: list[str] = []
    if sharpe < sharpe_min:
        failures.append(f"sharpe<{sharpe_min}")
    if max_drawdown < max_drawdown_min:
        failures.append(f"max_drawdown<{max_drawdown_min}")
    if turnover > turnover_max:
        failures.append(f"turnover>{turnover_max}")
    if val_ic < val_ic_min:
        failures.append(f"val_ic<{val_ic_min}")

    gate_payload = load_json(run_dir / "evaluation_gate.json", default={})
    if isinstance(gate_payload, dict):
        if gate_payload.get("passed") is False:
            failures.append("evaluation_gate_failed")
        gate_non_inferiority = gate_payload.get("non_inferiority_failures", [])
        if isinstance(gate_non_inferiority, list) and gate_non_inferiority:
            failures.extend(str(item) for item in gate_non_inferiority)

    incumbent_payload = get_promoted_model(model_name=model_name)
    incumbent_run_id = str(incumbent_payload.get("run_id") or "").strip()
    if incumbent_run_id and incumbent_run_id != str(run_id):
        incumbent_dir = get_run_dir(incumbent_run_id)
        if incumbent_dir.exists():
            incumbent = _load_metric_bundle(incumbent_dir, model_name)
            tol_cfg = config.get("non_inferiority_tolerance", {})
            if not isinstance(tol_cfg, dict):
                tol_cfg = {}
            sharpe_tol = float(tol_cfg.get("sharpe", 0.10))
            val_ic_tol = float(tol_cfg.get("val_ic", 0.01))
            maxdd_tol = float(tol_cfg.get("max_drawdown", 0.03))
            if sharpe < (incumbent["sharpe"] - sharpe_tol):
                failures.append("sharpe_non_inferiority")
            if val_ic < (incumbent["val_ic"] - val_ic_tol):
                failures.append("val_ic_non_inferiority")
            if max_drawdown < (incumbent["max_drawdown"] - maxdd_tol):
                failures.append("max_drawdown_non_inferiority")

    promoted = len(failures) == 0
    promoted_pointer = None
    if promoted and bool(config.get("promote_on_success", True)):
        promoted_pointer = set_promoted_model_pointer(
            run_id=str(run_id),
            model_name=model_name,
            source="promote_candidate_champion_challenger",
        )

    return {
        "status": "ok",
        "run_id": str(run_id),
        "promoted": promoted,
        "model_name": model_name,
        "metrics": {
            "sharpe": sharpe,
            "max_drawdown": max_drawdown,
            "turnover": turnover,
            "val_ic": val_ic,
        },
        "thresholds": {
            "sharpe_min": sharpe_min,
            "max_drawdown_min": max_drawdown_min,
            "turnover_max": turnover_max,
            "val_ic_min": val_ic_min,
        },
        "reasons": failures,
        "promoted_pointer": promoted_pointer,
        "message": (
            "candidate promoted"
            if promoted
            else "candidate did not pass promotion thresholds"
        ),
    }
