"""Additional coverage tests for jobs step modules."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from openbb_quant_ml.jobs.steps import db_maintenance, publish, rebuild_universe, stress_test
from openbb_quant_ml.service.storage import save_json


def test_publish_step_without_shadow(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(publish, "ARTIFACT_ROOT", tmp_path)
    monkeypatch.setattr(publish, "get_ops_status_response", lambda: type("O", (), {"model_dump": lambda self: {"status": "ok"}})())
    out = publish.run({"job": "daily", "run_id": "r1"})
    assert out["status"] == "ok"
    assert (tmp_path / "jobs" / "latest_publish.json").exists()
    assert (tmp_path / "jobs" / "ops_status_snapshot.json").exists()


def test_publish_step_with_shadow_live(tmp_path: Path, monkeypatch) -> None:
    run_id = "run-shadow-1"
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    save_json(
        run_dir / "backtest_lgbm_ranker.json",
        {
            "period_weights": [
                {"date": "2026-01-01", "weights": {"AAPL": 0.1, "MSFT": 0.2}},
                {"date": "2026-02-01", "weights": {"AAPL": 0.15, "MSFT": 0.1}},
            ],
            "risk_contribution_max": 0.08,
            "liquidity_clip_ratio": 0.01,
        },
    )

    monkeypatch.setattr(publish, "ARTIFACT_ROOT", tmp_path)
    monkeypatch.setattr(publish, "get_run_dir", lambda rid: run_dir)
    monkeypatch.setattr(
        publish,
        "get_ops_status_response",
        lambda: type("O", (), {"model_dump": lambda self: {"status": "ok"}})(),
    )
    monkeypatch.setattr(publish, "load_latest_universe_snapshot", lambda rid: {"run_id": rid, "rows": []})
    parquet_calls: list[tuple[str, str, int]] = []
    monkeypatch.setattr(
        publish,
        "write_parquet",
        lambda rid, name, frame: parquet_calls.append((rid, name, len(frame))),
    )

    out = publish.run(
        {
            "job": "daily",
            "run_id": run_id,
            "model_name": "lgbm_ranker",
            "shadow_live": {"enabled": True},
        }
    )
    assert out["status"] == "ok"
    assert out["shadow_live"]["enabled"] is True
    assert parquet_calls and parquet_calls[0][1] == "trade_plan.parquet"
    assert (run_dir / "risk_report.json").exists()
    assert (run_dir / "universe_snapshot_shadow.json").exists()


def test_stress_test_step_paths(tmp_path: Path, monkeypatch) -> None:
    assert stress_test.run({})["status"] == "skipped"

    run_id = "run-stress-1"
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(stress_test, "get_run_dir", lambda rid: run_dir)

    missing = stress_test.run({"run_id": run_id, "model_name": "lgbm_ranker"})
    assert missing["status"] == "skipped"

    save_json(
        run_dir / "backtest.json",
        {
            "equity_curve": [
                {"date": "2026-01-01", "equity": 100.0, "daily_return": 0.0},
                {"date": "2026-01-02", "equity": 98.0, "daily_return": -0.02},
                {"date": "2026-01-03", "equity": 99.0, "daily_return": 0.01},
            ]
        },
    )
    ok = stress_test.run({"run_id": run_id, "model_name": "lgbm_ranker"})
    assert ok["status"] == "ok"
    assert "stress_summary" in ok


def test_db_maintenance_and_rebuild_universe_steps(tmp_path: Path, monkeypatch) -> None:
    missing_db = tmp_path / "missing.sqlite"
    monkeypatch.setattr(db_maintenance, "MACRO_DB_PATH", missing_db)
    skipped = db_maintenance.run({})
    assert skipped["status"] == "skipped"

    db_path = tmp_path / "macro.sqlite"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE t (id INTEGER);")
    conn.commit()
    conn.close()
    monkeypatch.setattr(db_maintenance, "MACRO_DB_PATH", db_path)
    ok = db_maintenance.run({})
    assert ok["status"] == "ok"

    monkeypatch.setattr(
        rebuild_universe,
        "build_universe",
        lambda universe_id=None: {
            "universe_id": universe_id or "default",
            "train_universe": ["AAPL", "MSFT"],
            "trade_universe": ["AAPL"],
        },
    )
    rebuilt = rebuild_universe.run({"universe_id": "sp500"})
    assert rebuilt["status"] == "ok"
    assert rebuilt["train_size"] == 2
    assert rebuilt["trade_size"] == 1
