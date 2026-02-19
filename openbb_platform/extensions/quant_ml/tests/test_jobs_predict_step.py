"""Daily predict-step mode tests."""

from __future__ import annotations

import pytest
from openbb_quant_ml.jobs.steps import predict as predict_step


def test_predict_step_infer_only_success(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        predict_step,
        "refresh_latest_ranker_predictions",
        lambda **kwargs: {
            "status": "ok",
            "run_id": kwargs["run_id"],
            "as_of_date": "2026-02-19",
            "latest_rows_upserted": 120,
        },
    )

    payload = predict_step.run(
        {
            "run_id": "trn-260219-001",
            "predict_mode": "infer_only",
            "model_name": "lgbm_ranker",
            "lookback_years": 3,
        }
    )

    assert payload["status"] == "ok"
    assert payload["run_id"] == "trn-260219-001"
    assert payload["mode"] == "infer_only"
    assert payload["as_of_date"] == "2026-02-19"


def test_predict_step_missing_artifact_with_legacy_fallback(
    monkeypatch: pytest.MonkeyPatch,
):
    def _raise_missing(**kwargs):
        raise predict_step.InferenceArtifactMissingError("missing artifact")

    monkeypatch.setattr(
        predict_step, "refresh_latest_ranker_predictions", _raise_missing
    )

    payload = predict_step.run(
        {
            "run_id": "trn-260219-001",
            "predict_mode": "infer_only",
            "predict_fallback_legacy": True,
        }
    )

    assert payload["status"] == "skipped"
    assert payload["fallback"] == "legacy"
    assert "missing artifact" in payload["message"]


def test_predict_step_missing_artifact_without_fallback(
    monkeypatch: pytest.MonkeyPatch,
):
    def _raise_missing(**kwargs):
        raise predict_step.InferenceArtifactMissingError("missing artifact")

    monkeypatch.setattr(
        predict_step, "refresh_latest_ranker_predictions", _raise_missing
    )

    with pytest.raises(predict_step.InferenceArtifactMissingError):
        predict_step.run(
            {
                "run_id": "trn-260219-001",
                "predict_mode": "infer_only",
                "predict_fallback_legacy": False,
            }
        )
