"""Additional coverage tests for ops status aggregation."""

from __future__ import annotations

from pathlib import Path

from openbb_quant_ml.service import ops_status as osvc


def test_job_state_and_latest_runs_fallback(monkeypatch) -> None:
    payload = {
        "daily.last_status": "ok",
        "daily.last_run_id": "d-1",
        "daily.predict.last_success": "ts",
        "daily.predict.result": {"as_of_date": "2026-02-28"},
    }
    row = osvc._build_job_state(payload, "daily")
    assert row.job == "daily"
    assert row.last_status == "ok"
    assert "predict" in row.steps

    monkeypatch.setattr(osvc, "list_latest_runs_from_index", lambda limit=10: [])
    monkeypatch.setattr(
        osvc,
        "read_registry",
        lambda: {
            "runs": {
                "run-a": {"status": "completed", "updated_at": "2026-02-01"},
                "run-b": {"status": "running", "updated_at": "2026-02-05"},
            }
        },
    )
    rows = osvc._latest_runs(limit=10)
    assert rows[0]["run_id"] == "run-b"


def test_walkforward_depth_and_lock_health(tmp_path: Path, monkeypatch) -> None:
    jobs_path = tmp_path / "walkforward_jobs.json"
    jobs_path.write_text(
        '{"jobs":{"a":{"status":"queued"},"b":{"status":"running"},"c":{"status":"completed"}}}',
        encoding="utf-8",
    )
    monkeypatch.setattr(osvc, "WALKFORWARD_JOBS_PATH", jobs_path)
    assert osvc._walkforward_queue_depth() == 2

    lock_dir = tmp_path / ".locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    (lock_dir / "daily.lock").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(osvc, "ARTIFACT_ROOT", tmp_path)
    monkeypatch.setattr(
        osvc,
        "inspect_lock",
        lambda path, stale_ttl_sec: {"health": "ok", "stale": False, "pid": 1, "reason": "lock_in_use"},
    )
    rows, health = osvc._collect_lock_health()
    assert rows and rows[0]["lock_name"] == "daily.lock"
    assert health["daily.lock"] == "ok"


def test_get_ops_status_response(monkeypatch, tmp_path: Path) -> None:
    jobs_state = {"daily.last_status": "ok", "weekly.last_status": "ok", "monthly.last_status": "ok"}
    latest_publish = {"job": "daily", "run_id": "run-1"}

    monkeypatch.setattr(osvc, "ARTIFACT_ROOT", tmp_path)
    monkeypatch.setattr(
        osvc,
        "load_json",
        lambda path, default=None: jobs_state
        if "job_state.json" in str(path)
        else latest_publish
        if "latest_publish.json" in str(path)
        else default,
    )
    monkeypatch.setattr(osvc, "rebuild_runs_index", lambda: None)
    monkeypatch.setattr(osvc, "get_data_versions", lambda: {"a": 1})
    monkeypatch.setattr(osvc, "get_feature_versions", lambda: {"b": 2})
    monkeypatch.setattr(osvc, "_latest_runs", lambda limit=10: [{"run_id": "run-1"}])
    monkeypatch.setattr(osvc, "get_latest_training_run_id_from_index", lambda: "run-1")
    monkeypatch.setattr(osvc, "_latest_daily_infer_date", lambda state: "2026-02-28")
    monkeypatch.setattr(osvc, "_walkforward_queue_depth", lambda: 1)
    monkeypatch.setattr(osvc, "_collect_lock_health", lambda: ([], {}))

    class _Health:
        def model_dump(self):
            return {"status": "ok"}

    monkeypatch.setattr(
        __import__("openbb_quant_ml.service.macro_service", fromlist=["*"]),
        "get_health_response",
        lambda: _Health(),
    )

    payload = osvc.get_ops_status_response()
    assert payload.status == "ok"
    assert payload.latest_training_run_id == "run-1"
    assert payload.walkforward_queue_depth == 1
