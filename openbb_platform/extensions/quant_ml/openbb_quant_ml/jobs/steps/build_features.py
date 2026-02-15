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
    start_date = end_date - timedelta(days=365 * int(config.get("lookback_years", 3)))
    datasets, _ = load_market_data(symbols, start_date=start_date, end_date=end_date)
    frame, feature_cols, skipped = build_feature_dataset(
        data_by_symbol=datasets,
        feature_config=FeatureConfig(),
        horizon_days=1,
        target_mode="next_open_to_close",
        include_macro_features=True,
        macro_feature_subset=["z_252", "yoy", "mom_3", "slope"],
    )
    return {"rows": int(len(frame)), "feature_count": len(feature_cols), "skipped": len(skipped)}
