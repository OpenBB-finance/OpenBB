"""Additional coverage tests for macro feature engineering."""

from __future__ import annotations

import pandas as pd
from openbb_quant_ml.service import macro_feature_engineering as mfe


def _rows_from_series(series: pd.Series) -> list[dict[str, object]]:
    return [
        {"date": idx.date().isoformat(), "value": float(value)}
        for idx, value in series.items()
    ]


def test_freq_window_selection_and_safe_zscore_shapes() -> None:
    short = pd.Series([1.0, 2.0], index=pd.date_range("2026-01-01", periods=2, freq="D"))
    assert mfe._freq_windows(short) == (12, 36)

    daily = pd.Series(range(40), index=pd.date_range("2026-01-01", periods=40, freq="D"), dtype=float)
    assert mfe._freq_windows(daily) == (252, 252)

    monthly = pd.Series(range(36), index=pd.date_range("2023-01-01", periods=36, freq="MS"), dtype=float)
    assert mfe._freq_windows(monthly) == (12, 36)

    z = mfe._safe_zscore(daily, window=20)
    assert len(z) == len(daily)


def test_update_macro_features_and_wide_loader(monkeypatch) -> None:
    dgs10 = pd.Series(
        [4.0, 4.1, 4.2, 4.3],
        index=pd.date_range("2025-01-01", periods=4, freq="MS"),
        dtype=float,
    )
    dgs2 = pd.Series(
        [3.8, 3.9, 4.0, 4.1],
        index=pd.date_range("2025-01-01", periods=4, freq="MS"),
        dtype=float,
    )
    cpi = pd.Series(
        [300.0, 301.0, 302.0, 303.0, 304.0, 305.0, 306.0, 307.0, 308.0, 309.0, 310.0, 311.0, 312.0],
        index=pd.date_range("2024-01-01", periods=13, freq="MS"),
        dtype=float,
    )
    indpro = pd.Series(
        [100.0, 99.8, 99.9, 100.2, 100.1, 99.7, 99.5, 99.6, 99.7, 99.9, 100.0, 100.2, 100.1],
        index=pd.date_range("2024-01-01", periods=13, freq="MS"),
        dtype=float,
    )
    vix = pd.Series(
        [18.0, 17.0, 19.0, 20.0, 21.0, 19.0, 18.0, 17.0, 16.0, 18.0, 19.0, 20.0, 22.0],
        index=pd.date_range("2024-01-01", periods=13, freq="MS"),
        dtype=float,
    )
    hy = pd.Series(
        [3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 3.8, 3.7, 3.6, 3.5, 3.7, 3.8, 3.9],
        index=pd.date_range("2024-01-01", periods=13, freq="MS"),
        dtype=float,
    )

    obs_map = {
        "DGS10": _rows_from_series(dgs10),
        "DGS2": _rows_from_series(dgs2),
        "CPIAUCSL": _rows_from_series(cpi),
        "INDPRO": _rows_from_series(indpro),
        "VIXCLS": _rows_from_series(vix),
        "BAMLH0A0HYM2": _rows_from_series(hy),
    }
    written: list[tuple[str, list[dict[str, object]]]] = []

    monkeypatch.setattr(
        mfe,
        "load_observations",
        lambda source, series_id, start=None, end=None: obs_map.get(series_id, []),
    )
    monkeypatch.setattr(
        mfe,
        "upsert_macro_features",
        lambda source, series_id, rows: written.append((series_id, rows)),
    )

    updated = mfe.update_macro_features_for_series(list(obs_map.keys()))
    assert "DGS10" in updated
    assert "SLOPE_DGS10_DGS2" in updated
    assert "REGIME_FLAGS" in updated
    assert any(name == "REGIME_FLAGS" and len(rows) > 0 for name, rows in written)

    monkeypatch.setattr(
        mfe,
        "load_macro_features",
        lambda source="FRED", feat_names=None: [
            {"date": "2026-01-01", "series_id": "DGS10", "feat_name": "level", "feat_value": 4.1},
            {"date": "2026-01-01", "series_id": "CPIAUCSL", "feat_name": "yoy", "feat_value": 0.02},
        ],
    )
    wide = mfe.load_macro_feature_wide()
    assert "macro_dgs10_level" in wide.columns
    assert "macro_cpiaucsl_yoy" in wide.columns
