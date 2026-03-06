"""Tests for completed-first/actionable runs list behavior."""

from __future__ import annotations

from openbb_quant_ml.service import pipeline


def test_get_runs_list_completed_first_and_actionable_filters(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        pipeline,
        "list_latest_runs_from_index",
        lambda limit=20: [
            {
                "run_id": "run-running",
                "status": "running",
                "stage": "training",
                "updated_at": "2026-02-28T12:00:00Z",
                "created_at": "2026-02-28T11:00:00Z",
                "artifacts": {"predictions": True, "backtest": False},
            },
            {
                "run_id": "run-completed-ready",
                "status": "completed",
                "stage": "done",
                "updated_at": "2026-02-28T10:00:00Z",
                "created_at": "2026-02-28T09:00:00Z",
                "artifacts": {"predictions": True, "backtest": True},
            },
            {
                "run_id": "run-completed-empty",
                "status": "completed",
                "stage": "done",
                "updated_at": "2026-02-27T10:00:00Z",
                "created_at": "2026-02-27T09:00:00Z",
                "artifacts": {"predictions": False, "backtest": False},
            },
        ][:limit],
    )
    monkeypatch.setattr(
        pipeline,
        "_run_has_completion_artifacts",
        lambda run_id: run_id == "run-completed-ready",
    )

    payload = pipeline.get_runs_list(limit=10, completed_first=True, actionable_only=False)
    assert [item.run_id for item in payload.runs] == [
        "run-completed-ready",
        "run-completed-empty",
        "run-running",
    ]
    assert payload.runs[0].actionable_backtest is True
    assert payload.runs[1].actionable_backtest is False
    assert payload.runs[2].actionable_backtest is False

    actionable = pipeline.get_runs_list(
        limit=10, completed_first=True, actionable_only=True
    )
    assert [item.run_id for item in actionable.runs] == ["run-completed-ready"]
