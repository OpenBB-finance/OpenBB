"""Tests for canonical run-scoped snapshot services."""

from __future__ import annotations

from pathlib import Path

from openbb_quant_ml.models import (
    PortfolioExposureResponse,
    PortfolioRiskResponse,
    RollingPerformanceResponse,
)
from openbb_quant_ml.service.snapshot.run_snapshot import (
    get_run_audit,
    get_run_snapshot,
)


def test_get_run_snapshot_builds_dashboard_snapshot(
    monkeypatch, tmp_path: Path
) -> None:
    run_id = "trn-260221-001"
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "backtest_lgbm_ranker.json").write_text(
        """
{
  "metrics": {"cagr": 0.11, "sharpe": 1.2, "max_drawdown": -0.08, "volatility": 0.15, "turnover": 0.21, "net_return": 0.32},
  "equity_curve": [{"date": "2026-02-20", "equity": 1.12}],
  "constraint_binding_summary": [{"constraint_type": "single_name_cap", "binding_count": 3, "binding_ratio": 0.2}]
}
        """.strip(),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "openbb_quant_ml.service.snapshot.run_snapshot.get_run_dir", lambda _: run_dir
    )
    monkeypatch.setattr(
        "openbb_quant_ml.service.snapshot.run_snapshot.ensure_run_context",
        lambda *_: {"run_uid": "2026-02-21_150233Z_ab12cd34"},
    )
    monkeypatch.setattr(
        "openbb_quant_ml.service.snapshot.run_snapshot.get_performance_rolling",
        lambda **_: RollingPerformanceResponse(
            run_id=run_id,
            model_name="lgbm_ranker",
            rolling_ic_3m=[{"date": "2026-02-20", "value": 0.12}],
        ),
    )
    monkeypatch.setattr(
        "openbb_quant_ml.service.snapshot.run_snapshot.get_portfolio_risk",
        lambda **_: PortfolioRiskResponse(
            run_id=run_id,
            model_name="lgbm_ranker",
            position_risk_contrib_top10=[{"symbol": "AAPL", "contribution": 0.03}],
        ),
    )
    monkeypatch.setattr(
        "openbb_quant_ml.service.snapshot.run_snapshot.get_portfolio_exposure",
        lambda **_: PortfolioExposureResponse(
            run_id=run_id,
            model_name="lgbm_ranker",
            sector_exposure=[{"category": "technology", "weight": 0.24}],
        ),
    )

    payload = get_run_snapshot(run_id=run_id, model_name="lgbm_ranker")
    assert payload.run_id == run_id
    assert payload.model_name == "lgbm_ranker"
    assert payload.constraint_bindings[0].constraint_type == "single_name_cap"
    assert payload.exposure.get("technology", 0.0) == 0.24


def test_get_run_audit_not_found(monkeypatch, tmp_path: Path) -> None:
    run_id = "missing-run"
    monkeypatch.setattr(
        "openbb_quant_ml.service.snapshot.run_snapshot.get_run_dir",
        lambda _: tmp_path / run_id,
    )
    payload = get_run_audit(run_id=run_id, limit=10)
    assert payload.status == "not_found"
    assert payload.events == []


def test_get_run_audit_falls_back_to_legacy_logs(monkeypatch, tmp_path: Path) -> None:
    run_id = "trn-260221-legacy"
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(
        "openbb_quant_ml.service.snapshot.run_snapshot.get_run_dir", lambda _: run_dir
    )
    monkeypatch.setattr(
        "openbb_quant_ml.service.snapshot.run_snapshot.list_run_events",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        "openbb_quant_ml.service.snapshot.run_snapshot.read_registry",
        lambda: {
            "runs": {
                run_id: {
                    "updated_at": "2026-02-21T15:02:33+00:00",
                    "logs_tail": ["training started", "training completed"],
                }
            }
        },
    )
    payload = get_run_audit(run_id=run_id, limit=10)
    assert payload.status == "ok"
    assert len(payload.events) == 2
    assert payload.events[0].event_type == "legacy_log_tail"
