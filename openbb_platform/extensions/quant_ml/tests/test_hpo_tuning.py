"""HPO tuning helper tests."""

from __future__ import annotations

import numpy as np
import pandas as pd
from openbb_quant_ml.models import ModelConfig
from openbb_quant_ml.service.modeling import tune_xgb_hyperparameters


def _make_feature_frame(periods: int = 180) -> pd.DataFrame:
    rng = np.random.default_rng(21)
    dates = pd.date_range("2024-01-01", periods=periods, freq="B")
    symbols = ["AAA", "BBB", "CCC"]
    rows: list[dict[str, object]] = []
    for symbol in symbols:
        base = rng.normal(0.0, 0.01, periods)
        for idx, date_value in enumerate(dates):
            ret_lag_1 = float(base[idx - 1] if idx > 0 else 0.0)
            mom_5 = float(np.mean(base[max(0, idx - 5) : idx + 1]))
            noise = float(rng.normal(0, 0.002))
            target = float(0.4 * ret_lag_1 + 0.6 * mom_5 + noise)
            rows.append(
                {
                    "date": date_value,
                    "symbol": symbol,
                    "close": 100.0,
                    "daily_return": ret_lag_1,
                    "target_return": target,
                    "ret_lag_1": ret_lag_1,
                    "mom_5": mom_5,
                }
            )
    return pd.DataFrame(rows)


def test_xgb_hpo_is_deterministic_for_same_seed():
    feature_data = _make_feature_frame()
    feature_columns = ["ret_lag_1", "mom_5"]
    cfg = ModelConfig()

    tuned_a, summary_a = tune_xgb_hyperparameters(
        feature_data=feature_data,
        feature_columns=feature_columns,
        config=cfg,
        n_trials=3,
        timeout_sec=30,
        random_state=7,
        objective_metric="validation_mse",
    )
    tuned_b, summary_b = tune_xgb_hyperparameters(
        feature_data=feature_data,
        feature_columns=feature_columns,
        config=cfg,
        n_trials=3,
        timeout_sec=30,
        random_state=7,
        objective_metric="validation_mse",
    )

    assert summary_a["status"] == "ok"
    assert summary_b["status"] == "ok"
    assert summary_a["best_params"] == summary_b["best_params"]
    assert tuned_a.xgb_n_estimators == tuned_b.xgb_n_estimators
    assert tuned_a.xgb_max_depth == tuned_b.xgb_max_depth
