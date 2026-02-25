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


def test_train_models_maps_nested_configs_and_market_data_workers(
    monkeypatch: pytest.MonkeyPatch,
):
    captured: dict[str, object] = {}

    def _submit_training(request, *args, **kwargs):  # noqa: ANN001
        captured["request"] = request
        return _request_stub()

    monkeypatch.setattr(train_models, "submit_training", _submit_training)
    monkeypatch.setattr(
        train_models, "get_run", lambda run_id: _status_stub("completed")
    )
    monkeypatch.setattr(train_models.time, "sleep", lambda *_: None)

    payload = train_models.run(
        {
            "training_wait_timeout_sec": 120,
            "training_poll_sec": 0.5,
            "market_data_workers": 10,
            "walk_forward_config": {
                "train_months": 36,
                "embargo_months": 1,
                "val_months": 1,
                "step_months": 2,
            },
            "ranker_config": {
                "n_estimators": 3000,
                "early_stopping_rounds": 100,
            },
            "feature_config": {
                "include_bollinger": True,
                "include_atr": True,
                "include_adx": True,
                "include_obv": True,
            },
            "hpo_config": {
                "enabled": True,
                "n_trials": 9,
                "timeout_sec": 120,
                "objective_metric": "val_ic",
                "random_state": 7,
            },
        }
    )

    request = captured.get("request")
    assert request is not None
    assert request.market_data_workers == 10
    assert request.walk_forward_config.train_months == 36
    assert request.walk_forward_config.step_months == 2
    assert request.ranker_config.n_estimators == 3000
    assert request.ranker_config.early_stopping_rounds == 100
    assert request.feature_parameters.include_bollinger is True
    assert request.feature_parameters.include_obv is True
    assert request.hpo_config.enabled is True
    assert request.hpo_config.n_trials == 9
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
