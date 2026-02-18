"""Step: incremental macro data update."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.service.macro_catalog import all_default_series_ids
from openbb_quant_ml.service.macro_update import update_macro_all


def run(config: dict[str, Any]) -> dict[str, Any]:
    series = config.get("series") or all_default_series_ids()
    lookback_years = int(config.get("lookback_years", 30))
    compute_features = bool(config.get("compute_features", True))
    features_lookback_days = config.get("features_lookback_days")
    updated = update_macro_all(
        series_list=list(series),
        lookback_years=lookback_years,
        compute_features=compute_features,
        features_lookback_days=features_lookback_days,
    )
    return {"updated_series": updated, "count": len(updated)}
