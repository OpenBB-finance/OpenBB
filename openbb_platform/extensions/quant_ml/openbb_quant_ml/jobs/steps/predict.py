"""Step: prediction refresh placeholder."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.service.inference import (
    InferenceArtifactMissingError,
    refresh_latest_ranker_predictions,
)


def run(config: dict[str, Any]) -> dict[str, Any]:
    run_id = str(config.get("run_id", "")).strip()
    if not run_id:
        return {"status": "skipped", "message": "run_id is not configured"}

    mode = str(config.get("predict_mode", "infer_only")).strip().lower()
    if mode == "legacy":
        return {
            "status": "ok",
            "run_id": run_id,
            "mode": "legacy",
            "message": "prediction step uses existing model artifacts",
        }

    model_name = str(config.get("model_name", "lgbm_ranker"))
    lookback_years = int(config.get("lookback_years", 3))
    market_delta_days = config.get("market_delta_days")
    max_workers = config.get("max_infer_workers")
    fallback_legacy = bool(config.get("predict_fallback_legacy", True))

    try:
        result = refresh_latest_ranker_predictions(
            run_id=run_id,
            model_name=model_name,  # type: ignore[arg-type]
            lookback_years=lookback_years,
            market_delta_days=(
                int(market_delta_days) if market_delta_days is not None else None
            ),
            max_workers=int(max_workers) if max_workers is not None else None,
        )
        result["mode"] = "infer_only"
        return result
    except InferenceArtifactMissingError as exc:
        if fallback_legacy:
            return {
                "status": "skipped",
                "run_id": run_id,
                "mode": "infer_only",
                "fallback": "legacy",
                "message": str(exc),
            }
        raise
