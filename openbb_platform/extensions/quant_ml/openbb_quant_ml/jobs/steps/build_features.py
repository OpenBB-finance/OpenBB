"""Step: feature build/checkpoint."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from openbb_quant_ml.models import FeatureConfig
from openbb_quant_ml.service.data_loader import load_market_data
from openbb_quant_ml.service.feature_engineering import build_feature_dataset
from openbb_quant_ml.service.universe import get_symbols_for_universe


def run(config: dict[str, Any]) -> dict[str, Any]:
    universe_id = config.get("universe_id")
    symbols = get_symbols_for_universe(universe_id)
    end_date = date.today()
    feature_delta_days = int(
        config.get("feature_delta_days", 365 * int(config.get("lookback_years", 3)))
    )
    start_date = end_date - timedelta(days=max(30, feature_delta_days))
    horizon_days = int(config.get("horizon_days", 1))
    target_mode = str(config.get("target_mode", "next_open_to_close"))
    include_macro_features = bool(config.get("include_macro_features", True))
    macro_feature_subset = list(
        config.get("macro_feature_subset", ["z_252", "yoy", "mom_3", "slope"])
    )
    max_workers = config.get("max_infer_workers")
    datasets, _ = load_market_data(
        symbols,
        start_date=start_date,
        end_date=end_date,
        timeout_sec=int(config.get("market_data_timeout_sec", 20)),
        retry=int(config.get("market_data_retry", 2)),
        backoff_base=float(config.get("market_data_backoff_base", 2.0)),
        max_workers=int(config.get("market_data_workers", 6)),
    )
    frame, feature_cols, skipped = build_feature_dataset(
        data_by_symbol=datasets,
        feature_config=FeatureConfig(),
        horizon_days=horizon_days,
        target_mode=target_mode,  # type: ignore[arg-type]
        include_macro_features=include_macro_features,
        macro_feature_subset=macro_feature_subset,
        max_workers=max_workers if isinstance(max_workers, int) else None,
    )
    return {
        "rows": int(len(frame)),
        "feature_count": len(feature_cols),
        "skipped": len(skipped),
        "feature_delta_days": max(30, feature_delta_days),
    }
