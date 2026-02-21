"""Step: publish artifacts marker."""

from __future__ import annotations

from typing import Any

import pandas as pd

from openbb_quant_ml.service.artifact_store import write_parquet
from openbb_quant_ml.service.constants import ARTIFACT_ROOT
from openbb_quant_ml.service.ops_status import get_ops_status_response
from openbb_quant_ml.service.storage import get_run_dir, load_json
from openbb_quant_ml.service.universe_engine import load_latest_universe_snapshot
from openbb_quant_ml.service.storage import save_json


def run(config: dict[str, Any]) -> dict[str, Any]:
    run_id = str(config.get("run_id") or "").strip()
    model_name = str(config.get("model_name") or "lgbm_ranker")
    payload = {
        "job": str(config.get("job", "unknown")),
        "run_id": run_id or None,
        "updated_at": config.get("updated_at"),
    }
    path = ARTIFACT_ROOT / "jobs" / "latest_publish.json"
    save_json(path, payload)
    ops_snapshot_path = ARTIFACT_ROOT / "jobs" / "ops_status_snapshot.json"
    save_json(ops_snapshot_path, get_ops_status_response().model_dump())
    shadow_cfg = config.get("shadow_live", {})
    shadow_enabled = bool(
        shadow_cfg.get("enabled", False) if isinstance(shadow_cfg, dict) else False
    )
    if not shadow_enabled or not run_id:
        return {
            "status": "ok",
            "path": str(path),
            "ops_snapshot": str(ops_snapshot_path),
        }

    run_dir = get_run_dir(run_id)
    backtest_path = run_dir / f"backtest_{model_name}.json"
    if not backtest_path.exists():
        backtest_path = run_dir / "backtest.json"
    backtest = load_json(backtest_path, default={})
    period_weights = backtest.get("period_weights", []) if isinstance(backtest, dict) else []
    trade_rows: list[dict[str, Any]] = []
    prev: dict[str, float] = {}
    if isinstance(period_weights, list):
        for row in period_weights:
            if not isinstance(row, dict):
                continue
            as_of = str(row.get("date", "")).strip()
            weights = row.get("weights", {})
            if not as_of or not isinstance(weights, dict):
                continue
            curr = {
                str(symbol).strip().upper(): float(weight)
                for symbol, weight in weights.items()
                if str(symbol).strip()
            }
            for symbol in sorted(set(prev) | set(curr)):
                before = float(prev.get(symbol, 0.0))
                after = float(curr.get(symbol, 0.0))
                delta = after - before
                if abs(delta) <= 1e-12:
                    continue
                trade_rows.append(
                    {
                        "date": as_of,
                        "symbol": symbol,
                        "action": "buy" if delta > 0 else "sell",
                        "weight_before": before,
                        "weight_after": after,
                        "weight_delta": delta,
                    }
                )
            prev = curr

    write_parquet(run_id, "trade_plan.parquet", pd.DataFrame(trade_rows))
    risk_report = {
        "run_id": run_id,
        "model_name": model_name,
        "execution_blocked_shadow_mode": True,
        "risk_contribution_max": float(
            backtest.get("risk_contribution_max", 0.0) if isinstance(backtest, dict) else 0.0
        ),
        "liquidity_clip_ratio": float(
            backtest.get("liquidity_clip_ratio", 0.0) if isinstance(backtest, dict) else 0.0
        ),
    }
    save_json(run_dir / "risk_report.json", risk_report)
    snapshot = load_latest_universe_snapshot(run_id) or {}
    save_json(run_dir / "universe_snapshot_shadow.json", snapshot)
    return {
        "status": "ok",
        "path": str(path),
        "ops_snapshot": str(ops_snapshot_path),
        "shadow_live": {
            "enabled": True,
            "execution_blocked_shadow_mode": True,
            "trade_plan_rows": len(trade_rows),
            "risk_report": str(run_dir / "risk_report.json"),
            "universe_snapshot": str(run_dir / "universe_snapshot_shadow.json"),
        },
    }
