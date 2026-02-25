"""Step: enqueue training run."""

from __future__ import annotations

import time
from datetime import date, timedelta
from typing import Any

from openbb_quant_ml.models import DateRange, TrainRequest
from openbb_quant_ml.service.pipeline import get_run, submit_training


def run(config: dict[str, Any]) -> dict[str, Any]:
    end_date = date.today()
    start_date = end_date - timedelta(days=365 * int(config.get("recent_years", 5)))
    request_payload: dict[str, Any] = {
        "universe_id": config.get("universe_id"),
        "date_range": DateRange(start_date=start_date, end_date=end_date),
        "horizon_days": int(config.get("horizon_days", 1)),
        "target_mode": str(config.get("target_mode", "next_open_to_close")),
        "include_macro_features": bool(config.get("include_macro_features", True)),
        "macro_feature_subset": list(
            config.get("macro_feature_subset", ["z_252", "yoy", "mom_3", "slope"])
        ),
        "quick_mode": bool(config.get("quick_mode", False)),
        "model_choice": str(config.get("model_choice", "dual")),
        "early_stopping": bool(config.get("early_stopping", True)),
        "feature_pruning": bool(config.get("feature_pruning", False)),
        "walk_forward_compact": bool(config.get("walk_forward_compact", False)),
        "cross_sectional_sampling": bool(config.get("cross_sectional_sampling", False)),
        "top_liquid_n": config.get("top_liquid_n"),
    }
    walk_forward_config = config.get("walk_forward_config")
    if isinstance(walk_forward_config, dict):
        request_payload["walk_forward_config"] = walk_forward_config
    ranker_config = config.get("ranker_config")
    if isinstance(ranker_config, dict):
        request_payload["ranker_config"] = ranker_config
    feature_config = config.get("feature_config")
    if isinstance(feature_config, dict):
        request_payload["feature_config"] = feature_config
    hpo_config = config.get("hpo_config")
    if isinstance(hpo_config, dict):
        request_payload["hpo_config"] = hpo_config
    market_data_workers = config.get("market_data_workers")
    if market_data_workers is not None:
        request_payload["market_data_workers"] = int(market_data_workers)
    request = TrainRequest(**request_payload)
    run_id_scheme = str(
        config.get("training_run_id_scheme")
        or config.get("run_id_scheme")
        or "compact_v1"
    )
    timezone = str(config.get("timezone") or "Asia/Seoul")
    response = submit_training(
        request,
        run_id_scheme=run_id_scheme,
        timezone=timezone,
    )
    run_id = response.run_id
    wait_timeout_sec = max(60, int(config.get("training_wait_timeout_sec", 7200)))
    poll_sec = max(0.5, float(config.get("training_poll_sec", 2.0)))
    started = time.perf_counter()

    while True:
        status = get_run(run_id)
        if status.status in {"completed", "failed"}:
            break
        if (time.perf_counter() - started) >= wait_timeout_sec:
            raise RuntimeError(
                f"training_timeout: run_id={run_id}, timeout_sec={wait_timeout_sec}"
            )
        time.sleep(poll_sec)

    if status.status == "failed":
        raise RuntimeError(
            f"training_failed: run_id={run_id}, stage={status.stage}, error={status.error}"
        )

    return {"run_id": run_id, "status": status.status}
