"""Step: light backtest execution."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from openbb_quant_ml.models import BacktestConstraints, BacktestRequest
from openbb_quant_ml.service.pipeline import run_backtest_for_run


def run(config: dict[str, Any]) -> dict[str, Any]:
    run_id = str(config.get("run_id", "")).strip()
    if not run_id:
        return {"status": "skipped", "message": "run_id is not configured"}
    window_days = int(config.get("window_days", 90))
    end_date = date.today()
    start_date = end_date - timedelta(days=max(30, window_days))
    try:
        response = run_backtest_for_run(
            BacktestRequest(
                run_id=run_id,
                model_name=str(config.get("model_name", "lgbm_ranker")),
                start_date=start_date,
                end_date=end_date,
                constraints=BacktestConstraints(),
                cost_bps=float(config.get("cost_bps", 10.0)),
                slippage_bps=float(config.get("slippage_bps", 2.0)),
                entry_price=str(config.get("entry_price", "next_open")),
                exit_price=str(config.get("exit_price", "close")),
            )
        )
    except ValueError as exc:
        return {"status": "skipped", "message": str(exc), "run_id": run_id}
    return {"status": "ok", "sharpe": response.metrics.sharpe, "net_return": response.metrics.net_return}
