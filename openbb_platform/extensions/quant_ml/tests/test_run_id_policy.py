"""Run id policy and daily run-date behavior tests."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

import pytest
from openbb_quant_ml.jobs import daily
from openbb_quant_ml.jobs.state import JobState
from openbb_quant_ml.service import run_id as rid


def test_compact_job_run_id_sequence(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    (tmp_path / "dly-260219-01").mkdir(parents=True, exist_ok=True)
    (tmp_path / "dly-260219-02").mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(rid, "RUNS_DIR", tmp_path)
    monkeypatch.setattr(
        rid,
        "read_registry",
        lambda: {"runs": {"dly-260219-03": {"status": "completed"}}},
    )
    monkeypatch.setattr(
        rid,
        "_now_local",
        lambda _: datetime(2026, 2, 19, 9, 0, 0, tzinfo=UTC),
    )

    run_id, run_date = rid.build_job_run_id(
        "daily",
        run_id_scheme="compact_v1",
        timezone="Asia/Seoul",
    )
    assert run_id == "dly-260219-04"
    assert run_date == "2026-02-19"


def test_compact_training_run_id_sequence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    (tmp_path / "trn-260219-001").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(rid, "RUNS_DIR", tmp_path)
    monkeypatch.setattr(
        rid,
        "read_registry",
        lambda: {"runs": {"trn-260219-002": {"status": "completed"}}},
    )
    monkeypatch.setattr(
        rid,
        "_now_local",
        lambda _: datetime(2026, 2, 19, 9, 0, 0, tzinfo=UTC),
    )

    run_id = rid.build_training_run_id(
        run_id_scheme="compact_v1",
        timezone="Asia/Seoul",
    )
    assert run_id == "trn-260219-003"


def test_legacy_run_id_compatibility():
    run_id, _ = rid.build_job_run_id("daily", run_id_scheme="legacy")
    assert re.match(r"^\d{8}-\d{6}-[0-9a-f]{8}$", run_id)

    training_run_id = rid.build_training_run_id(run_id_scheme="legacy")
    assert re.match(r"^[0-9a-f]{32}$", training_run_id)


def test_daily_uses_explicit_run_date(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    run_dir = tmp_path / "job-run"
    run_dir.mkdir(parents=True, exist_ok=True)
    state = JobState({})

    monkeypatch.setattr(
        daily,
        "_run_step",
        lambda *args, **kwargs: ({"status": "ok"}, 0.0),
    )
    monkeypatch.setattr(daily, "write_json", lambda *args, **kwargs: None)

    daily.run_daily(
        config={"daily": {"run_id": "trn-260219-001"}},
        state=state,
        run_id="legacy-run-id",
        run_dir=run_dir,
        run_date="2026-02-19",
    )

    assert state.get("daily.update_market_data.last_success_date") == "2026-02-19"
