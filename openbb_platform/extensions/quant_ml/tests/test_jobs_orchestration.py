"""Coverage tests for jobs orchestration modules."""

from __future__ import annotations

import contextlib
from datetime import date
from pathlib import Path

import pytest
from openbb_quant_ml.jobs import bootstrap, cli, daily, monthly, weekly
from openbb_quant_ml.jobs.state import JobState


def test_run_step_retries_then_succeeds(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    attempts = {"n": 0}
    logs: list[str] = []
    monkeypatch.setattr(weekly, "append_log", lambda *args, **kwargs: logs.append(str(args[3])))

    def _func(_cfg):  # noqa: ANN001
        attempts["n"] += 1
        if attempts["n"] < 2:
            raise RuntimeError("temporary")
        return {"ok": True}

    result, elapsed = weekly._run_step(
        run_dir=tmp_path,
        name="step",
        func=_func,
        config={},
        retries=1,
        backoff_sec=0.0,
    )
    assert result["ok"] is True
    assert elapsed >= 0.0
    assert attempts["n"] == 2
    assert any("step failed" in row for row in logs)


def test_run_bootstrap_weekly_monthly(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    state = JobState({})
    writes: list[tuple[str, object]] = []

    monkeypatch.setattr(bootstrap, "append_log", lambda *args, **kwargs: None)
    monkeypatch.setattr(weekly, "append_log", lambda *args, **kwargs: None)
    monkeypatch.setattr(monthly, "append_log", lambda *args, **kwargs: None)
    monkeypatch.setattr(bootstrap, "write_json", lambda run_dir, name, payload: writes.append((name, payload)))
    monkeypatch.setattr(weekly, "write_json", lambda run_dir, name, payload: writes.append((name, payload)))
    monkeypatch.setattr(monthly, "write_json", lambda run_dir, name, payload: writes.append((name, payload)))

    for module in (bootstrap, weekly, monthly):
        if hasattr(module, "update_market_data"):
            monkeypatch.setattr(module.update_market_data, "run", lambda cfg: {"status": "ok"}, raising=False)
        if hasattr(module, "update_macro_data"):
            monkeypatch.setattr(module.update_macro_data, "run", lambda cfg: {"status": "ok"}, raising=False)
        monkeypatch.setattr(module.build_features, "run", lambda cfg: {"status": "ok"}, raising=False)
        if hasattr(module, "evaluate"):
            monkeypatch.setattr(module.evaluate, "run", lambda cfg: {"status": "ok"}, raising=False)
        monkeypatch.setattr(module.publish, "run", lambda cfg: {"status": "ok"}, raising=False)
        monkeypatch.setattr(module.notify, "run", lambda cfg: {"status": "ok"}, raising=False)
        monkeypatch.setattr(
            module.train_models,
            "run",
            lambda cfg: {"status": "ok", "run_id": "trained-1"},
            raising=False,
        )
        if hasattr(module, "promote_candidate"):
            monkeypatch.setattr(
                module.promote_candidate,
                "run",
                lambda cfg: {"status": "ok", "promoted": True, "run_id": "trained-1"},
                raising=False,
            )

    monkeypatch.setattr(monthly.rebuild_universe, "run", lambda cfg: {"status": "ok"})
    monkeypatch.setattr(monthly.backfill_if_needed, "run", lambda cfg: {"status": "ok"})
    monkeypatch.setattr(monthly.stress_test, "run", lambda cfg: {"status": "ok"})
    monkeypatch.setattr(monthly.db_maintenance, "run", lambda cfg: {"status": "ok"})

    bootstrap.run_bootstrap({"defaults": {}, "weekly": {}}, state, "rid-1", tmp_path)
    weekly.run_weekly({"defaults": {}, "weekly": {}}, state, "rid-2", tmp_path)
    monthly.run_monthly({"defaults": {}, "monthly": {}}, state, "rid-3", tmp_path)
    assert state.get("weekly.latest_run_id") == "trained-1"
    assert any(name == "time_profile.json" for name, _ in writes)


def test_run_daily_with_skip_and_fallback(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    state = JobState({"daily.update_market_data.last_success_date": "2026-02-28"})
    monkeypatch.setattr(daily, "append_log", lambda *args, **kwargs: None)
    snapshots: list[dict[str, object]] = []
    monkeypatch.setattr(daily, "write_json", lambda run_dir, name, payload: snapshots.append(payload))

    # Step functions are routed through _run_step, so patch _run_step directly.
    calls: list[tuple[str, str]] = []
    first_predict = {"done": False}

    def _fake_run_step(run_dir, name, func, config, retries, backoff_sec):  # noqa: ANN001
        calls.append((name, str(config.get("run_id"))))
        if name == "predict" and not first_predict["done"]:
            first_predict["done"] = True
            raise RuntimeError("predict fail")
        return {"status": "ok", "as_of_date": "2026-02-28"}, 0.01

    monkeypatch.setattr(daily, "_run_step", _fake_run_step)
    monkeypatch.setattr(daily, "_resolve_operational_run_id", lambda state, model_name=None: "fallback-run")

    daily.run_daily(
        config={"defaults": {}, "daily": {"run_id": "initial-run", "model_name": "lgbm_ranker"}},
        state=state,
        run_id="job-run",
        run_dir=tmp_path,
        run_date="2026-02-28",
    )

    predict_calls = [row for row in calls if row[0] == "predict"]
    assert len(predict_calls) == 2
    assert predict_calls[0][1] == "initial-run"
    assert predict_calls[1][1] == "fallback-run"
    assert snapshots


def test_cli_main_success_and_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    run_dir = tmp_path / "jobs"
    run_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(cli, "_load_config", lambda path: {"retention": {"index_compaction": True}})
    monkeypatch.setattr(cli, "create_run_dir", lambda job, run_id_scheme, timezone: ("rid", run_dir, "2026-02-28"))
    monkeypatch.setattr(cli, "job_lock", lambda job: contextlib.nullcontext())
    monkeypatch.setattr(cli, "append_log", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "write_json", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "rebuild_runs_index", lambda: None)

    class _Args:
        job = "daily"
        config = "config.yaml"

    monkeypatch.setattr(cli.argparse.ArgumentParser, "parse_args", lambda self: _Args())
    monkeypatch.setattr(cli, "run_daily", lambda *args, **kwargs: None)
    monkeypatch.setattr(JobState, "load", classmethod(lambda cls: JobState({})))
    assert cli.main() == 0

    monkeypatch.setattr(cli, "run_daily", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))
    assert cli.main() == 1


def test_daily_registry_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = {
        "runs": {
            "a": {"status": "completed", "updated_at": "2026-02-01T00:00:00"},
            "b": {"status": "running", "updated_at": "2026-02-02T00:00:00"},
            "c": {"status": "completed", "updated_at": "2026-02-03T00:00:00"},
        }
    }
    monkeypatch.setattr(daily, "read_registry", lambda: registry)
    assert daily._latest_completed_run_id() == "c"
    assert daily._is_completed_run("a") is True
    assert daily._is_completed_run("b") is False
    assert daily._resolve_run_date("invalid-date") == date.today().isoformat()

    state = JobState({"weekly.latest_run_id": "a"})
    monkeypatch.setattr(daily, "get_promoted_run_id", lambda model_name=None: "missing")
    assert daily._resolve_operational_run_id(state, model_name="lgbm_ranker") == "a"
