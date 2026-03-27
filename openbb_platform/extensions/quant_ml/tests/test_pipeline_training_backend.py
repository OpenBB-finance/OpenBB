"""Training backend dispatch tests for pipeline submit flow."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from openbb_quant_ml.models import TrainRequest
from openbb_quant_ml.service import pipeline


class _FakeFuture:
    def done(self) -> bool:
        return False


class _RecordingExecutor:
    def __init__(self) -> None:
        self.calls: list[tuple[object, tuple[object, ...]]] = []
        self.future = _FakeFuture()

    def submit(self, fn, *args):  # noqa: ANN001
        self.calls.append((fn, args))
        return self.future


class _FakeProcess:
    def __init__(self, *, pid: int = 1234, alive: bool = False) -> None:
        self.pid = pid
        self._alive = alive
        self.join_calls: list[float | None] = []

    def is_alive(self) -> bool:
        return self._alive

    def join(self, timeout: float | None = None) -> None:
        self.join_calls.append(timeout)


def _request() -> TrainRequest:
    return TrainRequest.model_validate(
        {
            "symbols": ["AAPL"],
            "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
        }
    )


def _state() -> SimpleNamespace:
    return SimpleNamespace(
        run_id="run-1",
        status="queued",
        artifact_root="artifacts/run-1",
        created_at="2026-03-27T00:00:00+00:00",
    )


@pytest.fixture(autouse=True)
def _reset_training_dispatch(monkeypatch: pytest.MonkeyPatch):
    pipeline._FUTURES.clear()
    pipeline._PROCESSES.clear()
    monkeypatch.delenv("OPENBB_QUANT_ML_TRAINING_BACKEND", raising=False)
    yield
    pipeline._FUTURES.clear()
    pipeline._PROCESSES.clear()


def test_submit_training_uses_thread_backend_by_default(
    monkeypatch: pytest.MonkeyPatch,
):
    executor = _RecordingExecutor()
    ops_updates: dict[str, object] = {}
    monkeypatch.setattr(pipeline, "_EXECUTOR", executor)
    monkeypatch.setattr(
        pipeline,
        "_resolve_symbols_for_training_request",
        lambda request: ["AAPL", "MSFT"],
    )
    monkeypatch.setattr(pipeline, "initialize_registry", lambda: None)
    monkeypatch.setattr(pipeline, "create_run", lambda **_: _state())
    monkeypatch.setattr(pipeline, "_save_run_config", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        pipeline,
        "_update_ops_metadata",
        lambda run_id, **updates: ops_updates.update({"run_id": run_id, **updates}),
    )

    response = pipeline.submit_training(_request())

    assert response.run_id == "run-1"
    assert response.status == "queued"
    assert len(executor.calls) == 1
    fn, args = executor.calls[0]
    assert fn is pipeline._run_training_job
    assert args[0] == "run-1"
    assert isinstance(args[1], TrainRequest)
    assert args[1].symbols == ["AAPL", "MSFT"]
    assert pipeline._FUTURES["run-1"] is executor.future
    assert ops_updates == {"run_id": "run-1", "training_backend": "thread"}


def test_submit_training_uses_process_backend_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
):
    started: dict[str, object] = {}
    ops_updates: dict[str, object] = {}
    process = _FakeProcess(pid=4321)

    monkeypatch.setenv("OPENBB_QUANT_ML_TRAINING_BACKEND", "process")
    monkeypatch.setattr(
        pipeline,
        "_resolve_symbols_for_training_request",
        lambda request: ["AAPL", "MSFT"],
    )
    monkeypatch.setattr(pipeline, "initialize_registry", lambda: None)
    monkeypatch.setattr(pipeline, "create_run", lambda **_: _state())
    monkeypatch.setattr(pipeline, "_save_run_config", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        pipeline,
        "_start_training_process",
        lambda run_id, request: started.update(
            {"run_id": run_id, "request": request}
        )
        or process,
    )
    monkeypatch.setattr(
        pipeline,
        "_update_ops_metadata",
        lambda run_id, **updates: ops_updates.update({"run_id": run_id, **updates}),
    )

    response = pipeline.submit_training(_request())

    assert response.run_id == "run-1"
    assert started["run_id"] == "run-1"
    assert isinstance(started["request"], TrainRequest)
    assert started["request"].symbols == ["AAPL", "MSFT"]
    assert pipeline._PROCESSES["run-1"] is process
    assert ops_updates == {
        "run_id": "run-1",
        "training_backend": "process",
        "training_worker_pid": 4321,
    }


def test_run_training_job_process_entry_reconstructs_request(
    monkeypatch: pytest.MonkeyPatch,
):
    captured: dict[str, object] = {}
    request = _request()
    request_payload = request.model_dump(mode="json", by_alias=True)

    monkeypatch.setattr(
        pipeline,
        "_run_training_job",
        lambda run_id, rebuilt_request: captured.update(
            {"run_id": run_id, "request": rebuilt_request}
        ),
    )

    pipeline._run_training_job_process_entry("run-1", request_payload)

    assert captured["run_id"] == "run-1"
    assert isinstance(captured["request"], TrainRequest)
    assert captured["request"].date_range.start_date.isoformat() == "2024-01-01"


def test_submit_training_marks_run_failed_when_dispatch_raises(
    monkeypatch: pytest.MonkeyPatch,
):
    updates: list[dict[str, object]] = []
    logs: list[str] = []

    monkeypatch.setenv("OPENBB_QUANT_ML_TRAINING_BACKEND", "process")
    monkeypatch.setattr(
        pipeline,
        "_resolve_symbols_for_training_request",
        lambda request: ["AAPL"],
    )
    monkeypatch.setattr(pipeline, "initialize_registry", lambda: None)
    monkeypatch.setattr(pipeline, "create_run", lambda **_: _state())
    monkeypatch.setattr(pipeline, "_save_run_config", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        pipeline,
        "_start_training_process",
        lambda run_id, request: (_ for _ in ()).throw(RuntimeError("spawn failed")),
    )
    monkeypatch.setattr(
        pipeline,
        "update_run",
        lambda run_id, **kwargs: updates.append({"run_id": run_id, **kwargs}),
    )
    monkeypatch.setattr(pipeline, "append_log", lambda run_id, message: logs.append(message))

    with pytest.raises(RuntimeError, match="spawn failed"):
        pipeline.submit_training(_request())

    assert updates == [
        {
            "run_id": "run-1",
            "status": "failed",
            "progress": 100,
            "stage": "dispatch_failed",
            "error": "spawn failed",
        }
    ]
    assert any("spawn failed" in message for message in logs)
