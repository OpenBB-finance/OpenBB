"""Cache registry tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from openbb_quant_ml.service import cache_registry as cr


def test_data_and_feature_version_roundtrip(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(cr, "RAW_STORE_DIR", tmp_path / "raw_store")
    monkeypatch.setattr(cr, "FEATURE_STORE_DIR", tmp_path / "feature_store")
    monkeypatch.setattr(cr, "VERSIONS_DIR", tmp_path / "versions")
    monkeypatch.setattr(cr, "DATA_VERSION_PATH", tmp_path / "versions" / "data_version.json")
    monkeypatch.setattr(cr, "FEATURE_VERSION_PATH", tmp_path / "versions" / "feature_version.json")

    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-02", "2025-01-03"]),
            "open": [100.0, 101.0],
            "high": [101.0, 102.0],
            "low": [99.0, 100.0],
            "close": [100.5, 101.5],
            "volume": [1_000_000, 1_200_000],
            "symbol": ["SPY", "SPY"],
            "target_return": [0.01, 0.02],
        }
    )
    cr.update_data_version("SPY", frame, source="test")
    data_versions = cr.get_data_versions()
    assert "SPY" in data_versions.get("symbols", {})
    assert data_versions["symbols"]["SPY"]["rows"] == 2

    params_hash = cr.compute_params_hash({"a": 1, "b": "x"})
    cr.update_feature_version("SPY", "default", params_hash, frame)
    feature_versions = cr.get_feature_versions()
    key = "default:SPY"
    assert key in feature_versions.get("features", {})
    assert feature_versions["features"][key]["params_hash"] == params_hash
