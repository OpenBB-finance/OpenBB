"""Execution and risk service tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from openbb_quant_ml.models import ExecutionOrderPreviewRequest, RiskPretradeRequest
from openbb_quant_ml.service import (
    execution as ex,
    pipeline,
)
from openbb_quant_ml.service.storage import save_json


def _build_execution_run(
    tmp_path: Path, run_id: str, concentrated: bool = False
) -> Path:
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    dates = pd.date_range("2025-01-01", periods=40, freq="B")
    market_rows: list[dict[str, object]] = []
    for date_value in dates:
        market_rows.append(
            {
                "date": date_value,
                "symbol": "AAA",
                "close": 100.0 + float(date_value.day % 10),
            }
        )
        market_rows.append(
            {
                "date": date_value,
                "symbol": "BBB",
                "close": 80.0 + float(date_value.day % 7),
            }
        )
    pd.DataFrame(market_rows).to_parquet(run_dir / "market_data.parquet", index=False)

    if concentrated:
        weights = {"AAA": 0.9, "BBB": 0.1}
    else:
        weights = {"AAA": 0.04, "BBB": 0.04, "CASH": 0.92}

    backtest_payload = {
        "run_id": run_id,
        "model_name": "lgbm_ranker",
        "start_date": "2025-01-01",
        "end_date": "2025-03-01",
        "benchmark_symbol": "SPY",
        "metrics": {
            "cagr": 0.1,
            "sharpe": 1.0,
            "max_drawdown": -0.1,
            "volatility": 0.2,
            "turnover": 0.3,
        },
        "equity_curve": [
            {"date": "2025-01-02", "daily_return": 0.0, "equity": 100.0},
            {"date": "2025-01-03", "daily_return": 0.001, "equity": 100.1},
        ],
        "period_weights": [{"date": "2025-02-03", "weights": weights}],
        "constraints": {
            "max_weight": 0.9 if concentrated else 0.04,
            "long_only": True,
            "risk_aversion": 3.0,
            "lookback_days": 126,
        },
        "effective_constraints": {
            "max_weight_requested": 0.9 if concentrated else 0.04,
            "max_weight_applied": 0.04,
            "max_weight": 0.04,
            "long_only": True,
            "risk_aversion": 3.0,
            "lookback_days": 126.0,
        },
        "cash_weight": 0.92 if not concentrated else 0.0,
        "cost_bps": 10.0,
    }
    save_json(run_dir / "backtest_lgbm_ranker.json", backtest_payload)
    save_json(run_dir / "backtest.json", backtest_payload)
    save_json(run_dir / "config.json", {"request": {"symbols": ["AAA", "BBB"]}})
    return run_dir


def _patch_run(monkeypatch: pytest.MonkeyPatch, run_dir: Path, run_id: str) -> None:
    monkeypatch.setattr(
        ex,
        "get_run_dir",
        lambda rid: run_dir if rid == run_id else run_dir.parent / rid,
    )
    monkeypatch.setattr(
        pipeline,
        "get_run_dir",
        lambda rid: run_dir if rid == run_id else run_dir.parent / rid,
    )
    monkeypatch.setattr(
        pipeline,
        "load_universe_config",
        lambda: {
            "assets": [
                {"symbol": "AAA", "category": "equity"},
                {"symbol": "BBB", "category": "equity"},
            ]
        },
    )


def test_execution_preview_submit_and_pnl(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    run_id = "run-exec"
    run_dir = _build_execution_run(tmp_path, run_id=run_id, concentrated=False)
    _patch_run(monkeypatch, run_dir, run_id)

    request = ExecutionOrderPreviewRequest(
        run_id=run_id,
        model_name="lgbm_ranker",
        slippage_bps=2.0,
        cost_bps=10.0,
        nav=1_000_000.0,
    )

    preview = ex.preview_execution_orders(request)
    assert preview.status == "ok"
    assert len(preview.orders) > 0

    submit = ex.submit_execution_orders(request)
    assert submit.status == "ok"
    assert submit.fills_count > 0
    assert submit.nav_after > 0

    orders = ex.get_execution_orders_current(run_id, "lgbm_ranker")
    assert orders.status == "ok"
    assert len(orders.orders) > 0

    fills = ex.get_execution_fills_history(run_id, "lgbm_ranker", limit=100)
    assert fills.status == "ok"
    assert len(fills.fills) >= submit.fills_count

    positions = ex.get_execution_positions_current(run_id, "lgbm_ranker")
    assert positions.status == "ok"
    assert len(positions.positions) > 0

    pnl = ex.get_execution_pnl(run_id, "lgbm_ranker")
    assert pnl.status == "ok"


def test_risk_pretrade_killswitch_blocks_submit(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    run_id = "run-risk"
    run_dir = _build_execution_run(tmp_path, run_id=run_id, concentrated=True)
    _patch_run(monkeypatch, run_dir, run_id)

    check = ex.risk_check_pretrade(
        RiskPretradeRequest(
            run_id=run_id,
            model_name="lgbm_ranker",
            turnover_limit=0.5,
        )
    )
    assert check.status == "ok"
    assert check.passed is False
    assert check.kill_switch is True
    assert any(item.rule_id == "max_weight" for item in check.violations)

    submit = ex.submit_execution_orders(
        ExecutionOrderPreviewRequest(
            run_id=run_id,
            model_name="lgbm_ranker",
            slippage_bps=2.0,
            cost_bps=10.0,
            nav=1_000_000.0,
        )
    )
    assert submit.kill_switch is True
    assert submit.status == "insufficient_data"

    events = ex.get_risk_events(run_id, "lgbm_ranker", limit=100)
    assert events.status == "ok"
    assert len(events.events) > 0

    limits = ex.get_risk_limits(run_id, "lgbm_ranker")
    assert limits.status == "ok"
    assert limits.kill_switch is True
    assert limits.limits.get("max_weight") == pytest.approx(0.04)
