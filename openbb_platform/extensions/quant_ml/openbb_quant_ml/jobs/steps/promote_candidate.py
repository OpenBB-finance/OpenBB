"""Step: promote model candidate using configurable thresholds."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.service.storage import get_run_dir, load_json


def run(config: dict[str, Any]) -> dict[str, Any]:
    run_id = config.get("run_id")
    if not run_id:
        return {"status": "skipped", "message": "run_id is not configured"}

    model_name = str(config.get("model_name", "lgbm_ranker"))
    run_dir = get_run_dir(str(run_id))
    if not run_dir.exists():
        return {"status": "skipped", "message": f"run not found: {run_id}", "run_id": run_id}

    backtest_payload = load_json(run_dir / f"backtest_{model_name}.json", default={})
    if not isinstance(backtest_payload, dict) or not backtest_payload:
        backtest_payload = load_json(run_dir / "backtest.json", default={})
    metrics_payload = load_json(run_dir / f"metrics_{model_name}.json", default={})
    if not isinstance(metrics_payload, dict) or not metrics_payload:
        metrics_payload = load_json(run_dir / "metrics.json", default={})

    metrics_block = backtest_payload.get("metrics", {}) if isinstance(backtest_payload, dict) else {}
    if not isinstance(metrics_block, dict):
        metrics_block = {}

    sharpe = float(metrics_block.get("sharpe", 0.0))
    max_drawdown = float(metrics_block.get("max_drawdown", 0.0))
    turnover = float(metrics_block.get("turnover", 0.0))
    val_ic = float(metrics_payload.get("val_ic", metrics_payload.get("train_ic", 0.0)) or 0.0)

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

    promoted = len(failures) == 0
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
        "message": "candidate promoted" if promoted else "candidate did not pass promotion thresholds",
    }
