"""Step: enqueue training run."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from openbb_quant_ml.models import DateRange, TrainRequest
from openbb_quant_ml.service.pipeline import submit_training


def run(config: dict[str, Any]) -> dict[str, Any]:
    end_date = date.today()
    start_date = end_date - timedelta(days=365 * int(config.get("recent_years", 5)))
    request = TrainRequest(
        universe_id=config.get("universe_id"),
        date_range=DateRange(start_date=start_date, end_date=end_date),
        horizon_days=int(config.get("horizon_days", 1)),
        target_mode=str(config.get("target_mode", "next_open_to_close")),
        include_macro_features=bool(config.get("include_macro_features", True)),
        macro_feature_subset=list(config.get("macro_feature_subset", ["z_252", "yoy", "mom_3", "slope"])),
        quick_mode=bool(config.get("quick_mode", False)),
        model_choice=str(config.get("model_choice", "dual")),
        early_stopping=bool(config.get("early_stopping", True)),
        feature_pruning=bool(config.get("feature_pruning", False)),
        walk_forward_compact=bool(config.get("walk_forward_compact", False)),
        cross_sectional_sampling=bool(config.get("cross_sectional_sampling", False)),
        top_liquid_n=config.get("top_liquid_n"),
    )
    response = submit_training(request)
    return {"run_id": response.run_id, "status": response.status}
