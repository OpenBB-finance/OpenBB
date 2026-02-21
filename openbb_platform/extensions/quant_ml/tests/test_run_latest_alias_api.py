"""Tests for run/latest alias service helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from openbb_quant_ml.models import PortfolioRiskResponse
from openbb_quant_ml.service.run_latest import get_run_latest_constraints


def test_get_run_latest_constraints_reads_constraints_log(
    monkeypatch, tmp_path: Path
) -> None:
    run_id = "trn-260221-001"
    run_dir = tmp_path / run_id
    artifacts = run_dir / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)

    frame = pd.DataFrame(
        [
            {
                "date": "2026-02-21",
                "ticker": "AAPL",
                "constraint_type": "single_name_cap",
                "binding": True,
                "threshold": 0.04,
                "violation_bp": 0.0,
            },
            {
                "date": "2026-02-21",
                "ticker": "AAPL",
                "constraint_type": "liquidity_adv20",
                "binding": True,
                "threshold": 0.03,
                "violation_bp": 0.0,
            },
        ]
    )
    frame.to_parquet(artifacts / "constraints_log.parquet", index=False)

    monkeypatch.setattr("openbb_quant_ml.service.run_latest.get_run_dir", lambda _: run_dir)
    monkeypatch.setattr(
        "openbb_quant_ml.service.run_latest.get_portfolio_risk",
        lambda **_: PortfolioRiskResponse(
            run_id=run_id,
            model_name="lgbm_ranker",
            position_risk_contrib_top10=[{"symbol": "AAPL", "contribution": 0.02}],
        ),
    )

    payload = get_run_latest_constraints(run_id=run_id, model_name="lgbm_ranker")
    assert payload.status == "ok"
    assert any(item.constraint_type == "single_name_cap" for item in payload.items)
    assert payload.liquidity_adv_top[0]["symbol"] == "AAPL"

