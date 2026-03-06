"""Tests for recent runs list service."""

from __future__ import annotations

from openbb_quant_ml.service import pipeline


def test_get_runs_list_respects_limit_and_shapes_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        pipeline,
        "list_latest_runs_from_index",
        lambda limit=20: [
            {
                "run_id": "run-003",
                "status": "completed",
                "stage": "backtest_completed",
                "created_at": "2026-02-20T00:00:00Z",
                "updated_at": "2026-02-20T01:00:00Z",
            },
            {
                "run_id": "run-002",
                "status": "running",
                "stage": "training",
                "created_at": "2026-02-19T00:00:00Z",
                "updated_at": "2026-02-19T00:30:00Z",
            },
            {
                "run_id": "run-001",
                "status": "failed",
                "stage": "feature_build",
                "created_at": "2026-02-18T00:00:00Z",
                "updated_at": "2026-02-18T00:10:00Z",
            },
        ][:limit],
    )

    response = pipeline.get_runs_list(limit=2)
    assert response.limit == 2
    assert len(response.runs) == 2
    assert response.runs[0].run_id == "run-003"
    assert response.runs[1].run_id == "run-002"
