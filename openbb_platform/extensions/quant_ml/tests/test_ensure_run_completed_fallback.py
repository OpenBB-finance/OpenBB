"""Tests for _ensure_run_completed artifact fallback behavior."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from openbb_quant_ml.service import pipeline


def test_ensure_run_completed_allows_artifact_fallback_for_non_completed_state(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        pipeline,
        "get_run_state",
        lambda run_id: SimpleNamespace(status="running"),
    )
    monkeypatch.setattr(pipeline, "_run_has_completion_artifacts", lambda run_id: True)

    # No exception: fallback should pass even if registry status is still running.
    pipeline._ensure_run_completed("run-1", allow_artifact_fallback=True)

    with pytest.raises(ValueError, match="Run is not completed"):
        pipeline._ensure_run_completed("run-1", allow_artifact_fallback=False)


def test_ensure_run_completed_raises_when_fallback_has_no_artifacts(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        pipeline,
        "get_run_state",
        lambda run_id: SimpleNamespace(status="failed"),
    )
    monkeypatch.setattr(pipeline, "_run_has_completion_artifacts", lambda run_id: False)

    with pytest.raises(ValueError, match="Run is not completed: failed"):
        pipeline._ensure_run_completed("run-2", allow_artifact_fallback=True)
