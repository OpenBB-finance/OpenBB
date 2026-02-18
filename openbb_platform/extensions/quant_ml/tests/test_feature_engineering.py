"""Feature engineering tests for Quant ML extension."""

from __future__ import annotations

import numpy as np
import pandas as pd
from openbb_quant_ml.models import FeatureConfig
from openbb_quant_ml.service.feature_engineering import attach_macro_features, build_feature_dataset


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


def test_target_modes_produce_different_labels():
    data_by_symbol = {"SPY": _make_symbol_frame("SPY", periods=260)}
    common = dict(
        data_by_symbol=data_by_symbol,
        feature_config=FeatureConfig(include_regime_features=False),
        horizon_days=1,
        include_macro_features=False,
    )
    c2c, _, _ = build_feature_dataset(target_mode="close_to_close", **common)
    c2o, _, _ = build_feature_dataset(target_mode="close_to_next_open", **common)
    o2c, _, _ = build_feature_dataset(target_mode="next_open_to_close", **common)

    merged = (
        c2c[["date", "symbol", "target_return"]]
        .rename(columns={"target_return": "c2c"})
        .merge(c2o[["date", "symbol", "target_return"]].rename(columns={"target_return": "c2o"}), on=["date", "symbol"])
        .merge(o2c[["date", "symbol", "target_return"]].rename(columns={"target_return": "o2c"}), on=["date", "symbol"])
        .dropna()
    )
    assert not merged.empty
    assert (np.abs(merged["c2c"] - merged["o2c"]) > 1e-12).any()
    assert (np.abs(merged["c2o"] - merged["o2c"]) > 1e-12).any()


def test_attach_macro_features_asof_does_not_use_future(monkeypatch):
    panel = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-02", "2025-01-03", "2025-01-06"]),
            "symbol": ["SPY", "SPY", "SPY"],
            "ret_lag_1": [0.01, 0.02, 0.03],
        }
    )
    macro = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-01", "2025-01-05"]),
            "macro_cpiaucsl_yoy": [1.0, 2.0],
        }
    )
    monkeypatch.setattr(
        "openbb_quant_ml.service.feature_engineering.load_macro_feature_wide",
        lambda feature_names=None: macro,
    )
    out = attach_macro_features(panel, include_macro_features=True, subset=["yoy"])
    assert float(out.loc[out["date"] == pd.Timestamp("2025-01-03"), "macro_cpiaucsl_yoy"].iloc[0]) == 1.0
    assert float(out.loc[out["date"] == pd.Timestamp("2025-01-06"), "macro_cpiaucsl_yoy"].iloc[0]) == 2.0
