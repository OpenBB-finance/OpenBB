"""Coverage tests for small service helper modules."""

from __future__ import annotations

import numpy as np
from openbb_quant_ml.service.capacity_estimator import position_value_cap_from_adv20
from openbb_quant_ml.service.cost_model import (
    TransactionCostModel,
    estimate_roundtrip_cost,
)
from openbb_quant_ml.service.exposure_report import build_sector_exposure_rows
from openbb_quant_ml.service.liquidity_cap import adv20_weight_cap
from openbb_quant_ml.service.pnl_attribution import build_pnl_attribution
from openbb_quant_ml.service.report_builder import build_report_html
from openbb_quant_ml.service.risk_contribution import compute_risk_contribution
from openbb_quant_ml.service.risk_report import build_risk_summary
from openbb_quant_ml.service.trade_engine import build_trade_plan


def test_capacity_and_liquidity_caps_handle_negative_inputs() -> None:
    assert position_value_cap_from_adv20(-100.0, max_adv_participation=0.05) == 0.0
    assert position_value_cap_from_adv20(2000.0, max_adv_participation=0.1) == 200.0
    assert adv20_weight_cap(-10.0, 1000.0, max_adv_participation=0.05) == 0.0
    assert adv20_weight_cap(1000.0, 0.0, max_adv_participation=0.1) > 0.0


def test_cost_model_and_roundtrip_estimation_are_positive() -> None:
    model = TransactionCostModel(commission_bps=5.0, spread_bps=3.0, market_impact_bps=2.0)
    cost = model.compute_cost(weight_delta=-0.2, adv_ratio=0.25)
    assert cost > 0.0
    roundtrip = estimate_roundtrip_cost(
        turnover=0.8,
        cost_bps=5.0,
        slippage_bps=3.0,
        participation_impact_bps=2.0,
        fee_bps=1.0,
    )
    assert roundtrip > 0.0


def test_exposure_and_pnl_builders_normalize_frames() -> None:
    exposure = build_sector_exposure_rows(
        [{"category": "tech", "weight": "0.3"}, {"category": "energy", "weight": 0.2}]
    )
    assert list(exposure.columns) == ["sector", "weight"]
    assert set(exposure["sector"].tolist()) == {"tech", "energy"}
    pnl = build_pnl_attribution(
        [{"date": "2026-01-01", "gross_return": "0.01", "trading_cost": 0.001, "net_return": 0.009}]
    )
    assert list(pnl.columns) == ["date", "gross_return", "trading_cost", "net_return"]
    assert float(pnl.iloc[0]["net_return"]) == 0.009


def test_risk_and_trade_helpers_produce_expected_payloads() -> None:
    weights = np.array([0.6, 0.4], dtype=float)
    cov = np.array([[0.04, 0.01], [0.01, 0.03]], dtype=float)
    rc = compute_risk_contribution(weights, cov)
    assert rc.shape == (2,)
    assert float(np.sum(rc)) > 0.0

    summary = build_risk_summary(
        run_id="run-1",
        model_name="lgbm_ranker",
        vol_ex_ante=0.2,
        cvar_95=-0.03,
        risk_contribution_max=0.08,
        invalid_rebalance_count=1,
    )
    assert summary["run_id"] == "run-1"
    assert summary["invalid_rebalance_count"] == 1

    trades = build_trade_plan(
        as_of_date="2026-02-28",
        previous_weights={"AAPL": 0.1, "MSFT": 0.2},
        target_weights={"AAPL": 0.15, "GOOG": 0.05},
    )
    assert len(trades) == 3
    actions = {row["symbol"]: row["action"] for row in trades}
    assert actions["AAPL"] == "buy"
    assert actions["MSFT"] == "sell"
    assert actions["GOOG"] == "buy"


def test_report_builder_renders_core_fields() -> None:
    html = build_report_html(
        {
            "run_id": "run-1",
            "run_uid": "uid-1",
            "model_name": "lgbm_ranker",
            "metrics": {"sharpe": 1.2, "cagr": 0.15, "max_drawdown": -0.08},
        }
    )
    assert "Quant ML Run Report" in html
    assert "run-1" in html
    assert "uid-1" in html
    assert "Sharpe" in html
