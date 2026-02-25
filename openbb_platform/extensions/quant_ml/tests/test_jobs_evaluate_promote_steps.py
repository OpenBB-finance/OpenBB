"""Tests for evaluate/promote job steps."""

from __future__ import annotations

from pathlib import Path

import pytest
from openbb_quant_ml.jobs.steps import evaluate, promote_candidate
from openbb_quant_ml.service.storage import save_json


def _write_candidate_run(run_dir: Path, *, sharpe: float, max_drawdown: float, turnover: float, val_ic: float) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    save_json(
        run_dir / "backtest_lgbm_ranker.json",
        {"metrics": {"sharpe": sharpe, "max_drawdown": max_drawdown, "turnover": turnover}},
    )
    save_json(
        run_dir / "metrics_lgbm_ranker.json",
        {"metrics": {"val_ic": val_ic}},
    )


def test_evaluate_step_writes_gate_payload(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    run_id = "trn-260301-001"
    run_dir = tmp_path / run_id
    _write_candidate_run(
        run_dir,
        sharpe=0.6,
        max_drawdown=-0.2,
        turnover=0.8,
        val_ic=0.04,
    )

    monkeypatch.setattr(evaluate, "get_run_dir", lambda rid: run_dir)
    monkeypatch.setattr(
        evaluate, "get_promoted_model", lambda model_name=None: {"run_id": None}
    )

    payload = evaluate.run({"run_id": run_id, "model_name": "lgbm_ranker"})
    assert payload["status"] == "ok"
    assert payload["passed"] is True
    gate = evaluate.load_json(run_dir / "evaluation_gate.json", default={})
    assert gate.get("passed") is True


def test_promote_step_respects_evaluation_gate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    run_id = "trn-260301-002"
    run_dir = tmp_path / run_id
    _write_candidate_run(
        run_dir,
        sharpe=0.6,
        max_drawdown=-0.2,
        turnover=0.8,
        val_ic=0.04,
    )
    save_json(
        run_dir / "evaluation_gate.json",
        {"status": "ok", "run_id": run_id, "passed": False, "non_inferiority_failures": ["val_ic_non_inferiority"]},
    )

    monkeypatch.setattr(promote_candidate, "get_run_dir", lambda rid: run_dir)
    monkeypatch.setattr(
        promote_candidate, "get_promoted_model", lambda model_name=None: {"run_id": None}
    )

    called = {"value": False}

    def _set_pointer(**kwargs):
        called["value"] = True
        return {"run_id": kwargs.get("run_id"), "ready": True}

    monkeypatch.setattr(promote_candidate, "set_promoted_model_pointer", _set_pointer)

    payload = promote_candidate.run({"run_id": run_id, "model_name": "lgbm_ranker"})
    assert payload["status"] == "ok"
    assert payload["promoted"] is False
    assert "evaluation_gate_failed" in payload["reasons"]
    assert called["value"] is False
