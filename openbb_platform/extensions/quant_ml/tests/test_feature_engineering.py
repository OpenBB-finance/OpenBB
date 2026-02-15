"""Feature engineering tests for Quant ML extension."""

from __future__ import annotations

import numpy as np
import pandas as pd

from openbb_quant_ml.models import FeatureConfig
from openbb_quant_ml.service.feature_engineering import build_feature_dataset


def _make_symbol_frame(symbol: str, periods: int = 220) -> pd.DataFrame:
    dates = pd.date_range("2022-01-01", periods=periods, freq="B")
    base = np.linspace(100, 130, periods) + np.random.default_rng(7).normal(0, 1, periods)
    return pd.DataFrame(
        {
            "date": dates,
            "open": base * 0.99,
            "high": base * 1.01,
            "low": base * 0.98,
            "close": base,
            "volume": 1_000_000,
            "symbol": symbol,
        }
    )


def test_build_feature_dataset_shapes_and_nans():
    data_by_symbol = {
        "SPY": _make_symbol_frame("SPY"),
        "QQQ": _make_symbol_frame("QQQ"),
        "DBC": _make_symbol_frame("DBC"),
    }
    feature_data, feature_columns, skipped = build_feature_dataset(
        data_by_symbol=data_by_symbol,
        feature_config=FeatureConfig(),
        horizon_days=1,
    )
    assert skipped == []
    assert not feature_data.empty
    assert len(feature_columns) > 5
    assert "ret_lag_1" in feature_columns
    assert "vol_5" in feature_columns
    assert "mom_5" in feature_columns
    assert "trend_ratio_20" in feature_columns
    assert "rsi_14" in feature_columns
    assert feature_data[feature_columns].isna().sum().sum() == 0
