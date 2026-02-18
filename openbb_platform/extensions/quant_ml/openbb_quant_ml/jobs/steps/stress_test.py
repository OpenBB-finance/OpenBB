"""Step: stress-test summary on latest backtest artifacts."""

from __future__ import annotations

from typing import Any

import pandas as pd

from openbb_quant_ml.service.storage import get_run_dir, load_json


def run(config: dict[str, Any]) -> dict[str, Any]:
    run_id = str(config.get("run_id", "")).strip()
    if not run_id:
        return {"status": "skipped", "message": "run_id is not configured"}

    model_name = str(config.get("model_name", "lgbm_ranker"))
    run_dir = get_run_dir(run_id)
    backtest_payload = load_json(run_dir / f"backtest_{model_name}.json", default={})
    if not isinstance(backtest_payload, dict) or not backtest_payload:
        backtest_payload = load_json(run_dir / "backtest.json", default={})
    if not isinstance(backtest_payload, dict) or not backtest_payload:
        return {"status": "skipped", "message": "backtest artifact is missing", "run_id": run_id}

    curve = pd.DataFrame(backtest_payload.get("equity_curve", []))
    if curve.empty or "daily_return" not in curve.columns:
        return {"status": "skipped", "message": "equity_curve is empty", "run_id": run_id}

    returns = pd.to_numeric(curve["daily_return"], errors="coerce").fillna(0.0)
    returns = returns.replace([pd.NA], 0.0).astype(float)
    worst_1d = float(returns.min()) if not returns.empty else 0.0
    rolling_20 = (1.0 + returns).rolling(20, min_periods=5).apply(lambda x: float(x.prod() - 1.0), raw=False)
    worst_20d = float(rolling_20.min()) if not rolling_20.empty else 0.0

    equity = pd.to_numeric(curve.get("equity"), errors="coerce").ffill().fillna(100.0)
    drawdown = equity / equity.cummax() - 1.0
    max_drawdown = float(drawdown.min()) if not drawdown.empty else 0.0

    return {
        "status": "ok",
        "run_id": run_id,
        "model_name": model_name,
        "stress_summary": {
            "worst_1d_return": worst_1d,
            "worst_20d_return": worst_20d,
            "max_drawdown": max_drawdown,
        },
    }
