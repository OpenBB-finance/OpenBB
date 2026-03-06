"""Feature cache regression tests."""

from __future__ import annotations

import numpy as np
import pandas as pd
from openbb_quant_ml.models import FeatureConfig
from openbb_quant_ml.service import (
    cache_registry as cr,
    feature_engineering as fe,
)


def _make_symbol_frame(symbol: str, periods: int = 260) -> pd.DataFrame:
    dates = pd.date_range("2023-01-02", periods=periods, freq="B")
    base = np.linspace(100.0, 130.0, periods) + np.random.default_rng(19).normal(0, 1, periods)
    return pd.DataFrame(
        {
            "date": dates,
            "open": base * 0.99,
            "high": base * 1.01,
            "low": base * 0.98,
            "close": base,
            "volume": 1_000_000 + np.arange(periods) * 1_000,
            "symbol": symbol,
        }
    )


def _patch_feature_cache_paths(monkeypatch, tmp_path) -> None:
    feature_store = tmp_path / "feature_store"
    versions = tmp_path / "versions"
    raw_store = tmp_path / "raw_store"
    monkeypatch.setattr(fe, "FEATURE_STORE_DIR", feature_store)
    monkeypatch.setattr(cr, "FEATURE_STORE_DIR", feature_store)
    monkeypatch.setattr(cr, "RAW_STORE_DIR", raw_store)
    monkeypatch.setattr(cr, "VERSIONS_DIR", versions)
    monkeypatch.setattr(cr, "FEATURE_VERSION_PATH", versions / "feature_versions.json")
    monkeypatch.setattr(cr, "DATA_VERSION_PATH", versions / "data_versions.json")


def test_incremental_feature_cache_keeps_unique_date_symbol(monkeypatch, tmp_path) -> None:
    _patch_feature_cache_paths(monkeypatch, tmp_path)

    feature_config = FeatureConfig(include_regime_features=False)
    data_small = {"SPY": _make_symbol_frame("SPY", periods=190)}
    data_large = {"SPY": _make_symbol_frame("SPY", periods=240)}

    first, _, skipped_first = fe.build_feature_dataset(
        data_by_symbol=data_small,
        feature_config=feature_config,
        horizon_days=1,
        include_macro_features=False,
        feature_set_id="feature_cache_dedup",
    )
    second, _, skipped_second = fe.build_feature_dataset(
        data_by_symbol=data_large,
        feature_config=feature_config,
        horizon_days=1,
        include_macro_features=False,
        feature_set_id="feature_cache_dedup",
    )

    assert skipped_first == []
    assert skipped_second == []
    assert not first.empty and not second.empty
    assert not second.duplicated(subset=["date", "symbol"]).any()
    assert pd.Timestamp(second["date"].max()) > pd.Timestamp(first["date"].max())


def test_obv_enabled_rebuild_matches_fresh_full_build(monkeypatch, tmp_path) -> None:
    _patch_feature_cache_paths(monkeypatch, tmp_path)

    feature_config = FeatureConfig(include_obv=True, include_regime_features=False)
    seed_data = {"SPY": _make_symbol_frame("SPY", periods=210)}
    full_data = {"SPY": _make_symbol_frame("SPY", periods=260)}

    fe.build_feature_dataset(
        data_by_symbol=seed_data,
        feature_config=feature_config,
        horizon_days=1,
        include_macro_features=False,
        feature_set_id="obv_cache_rebuild",
    )
    cached_result, _, _ = fe.build_feature_dataset(
        data_by_symbol=full_data,
        feature_config=feature_config,
        horizon_days=1,
        include_macro_features=False,
        feature_set_id="obv_cache_rebuild",
    )
    fresh_result, _, _ = fe.build_feature_dataset(
        data_by_symbol=full_data,
        feature_config=feature_config,
        horizon_days=1,
        include_macro_features=False,
        feature_set_id="obv_cache_fresh",
    )

    merged = cached_result.merge(
        fresh_result[["date", "symbol", "obv"]],
        on=["date", "symbol"],
        how="inner",
        suffixes=("_cached", "_fresh"),
    )
    assert not merged.empty
    assert np.allclose(
        merged["obv_cached"].to_numpy(dtype=float),
        merged["obv_fresh"].to_numpy(dtype=float),
        equal_nan=True,
        atol=1e-12,
    )
