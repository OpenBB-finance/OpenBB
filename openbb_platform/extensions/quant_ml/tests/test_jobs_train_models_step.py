"""Training job-step polling behavior tests."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from openbb_quant_ml.jobs.steps import train_models


def _request_stub(run_id: str = "trn-260219-001") -> SimpleNamespace:
    return SimpleNamespace(run_id=run_id, status="queued")


def _status_stub(
    status: str,
    *,
    stage: str = "running",
    error: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(status=status, stage=stage, error=error)


def test_train_models_waits_until_completed(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        train_models, "submit_training", lambda *args, **kwargs: _request_stub()
    )
    states = iter(
        [
            _status_stub("queued", stage="queued"),
            _status_stub("running", stage="training_ranker"),
            _status_stub("completed", stage="completed"),
        ]
    )
    monkeypatch.setattr(train_models, "get_run", lambda run_id: next(states))
    monkeypatch.setattr(train_models.time, "sleep", lambda *_: None)

    payload = train_models.run(
        {"training_wait_timeout_sec": 120, "training_poll_sec": 0.5}
    )
    assert payload["run_id"] == "trn-260219-001"
    assert payload["status"] == "completed"


def test_train_models_raises_on_failed_run(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        train_models, "submit_training", lambda *args, **kwargs: _request_stub()
    )
    monkeypatch.setattr(
        train_models,
        "get_run",
        lambda run_id: _status_stub("failed", stage="failed", error="boom"),
    )
    monkeypatch.setattr(train_models.time, "sleep", lambda *_: None)

    with pytest.raises(RuntimeError, match="training_failed"):
        train_models.run({})


def test_train_models_timeout(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        train_models, "submit_training", lambda *args, **kwargs: _request_stub()
    )
    monkeypatch.setattr(
        train_models,
        "get_run",
        lambda run_id: _status_stub("running", stage="training_ranker"),
    )
    monkeypatch.setattr(train_models.time, "sleep", lambda *_: None)

    counter = {"value": 0.0}

    def _fake_perf_counter() -> float:
        counter["value"] += 61.0
        return counter["value"]

    monkeypatch.setattr(train_models.time, "perf_counter", _fake_perf_counter)

    with pytest.raises(RuntimeError, match="training_timeout"):
        train_models.run({"training_wait_timeout_sec": 60})
