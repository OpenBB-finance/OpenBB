"""Step: signal generation from latest run."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.models import SignalRequest
from openbb_quant_ml.service.pipeline import build_signals


def run(config: dict[str, Any]) -> dict[str, Any]:
    run_id = str(config.get("run_id", "")).strip()
    if not run_id:
        return {"status": "skipped", "message": "run_id is not configured"}
    try:
        response = build_signals(
            SignalRequest(
                run_id=run_id,
                model_name=str(config.get("model_name", "lgbm_ranker")),
                top_k=int(config.get("top_k", 20)),
                score_threshold=float(config.get("score_threshold", 0.5)),
            )
        )
    except ValueError as exc:
        return {"status": "skipped", "message": str(exc), "run_id": run_id}
    return {"status": "ok", "as_of_date": response.as_of_date, "count": len(response.signals)}
