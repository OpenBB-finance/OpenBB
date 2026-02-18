"""Macro feature engineering and feature-store helpers."""

from __future__ import annotations

from typing import Any

import pandas as pd

from openbb_quant_ml.service.macro_db import load_macro_features, load_observations, upsert_macro_features
from openbb_quant_ml.service.macro_transforms import normalize_series
from openbb_quant_ml.service.storage import utc_now_iso


def _freq_windows(series: pd.Series) -> tuple[int, int]:
    if series.shape[0] < 3:
        return 12, 36
    idx = pd.to_datetime(series.index).sort_values()
    step_days = float((idx.to_series().diff().dropna().dt.days).median())
    if step_days <= 2:
        return 252, 252
    if step_days <= 8:
        return 52, 104
    return 12, 36


def _safe_zscore(values: pd.Series, window: int) -> pd.Series:
    rolling_mean = values.rolling(window, min_periods=max(3, window // 5)).mean()
    rolling_std = values.rolling(window, min_periods=max(3, window // 5)).std(ddof=0)
    return (values - rolling_mean) / (rolling_std + 1e-12)


def _series_feature_rows(series_id: str, series: pd.Series) -> list[dict[str, Any]]:
    if series.empty:
        return []
    series = series.sort_index().astype(float)
    yoy_window, z_window = _freq_windows(series)
    rows: list[dict[str, Any]] = []
    now_iso = utc_now_iso()
    derived = {
        "level": series,
        "mom_1": series.pct_change(1),
        "mom_3": series.pct_change(3),
        "yoy": series.pct_change(yoy_window),
        "z_252": _safe_zscore(series, z_window),
    }
    for feat_name, feat_series in derived.items():
        for idx, value in feat_series.items():
            rows.append(
                {
                    "date": pd.Timestamp(idx).date().isoformat(),
                    "feat_name": feat_name,
                    "feat_value": float(value) if pd.notna(value) else None,
                    "updated_at": now_iso,
                }
            )
    return rows


def _build_slope_rows(series_map: dict[str, pd.Series]) -> list[tuple[str, list[dict[str, Any]]]]:
    out: list[tuple[str, list[dict[str, Any]]]] = []
    if "DGS10" in series_map and "DGS2" in series_map:
        left, right = series_map["DGS10"].align(series_map["DGS2"], join="inner")
        slope = left - right
        out.append(("SLOPE_DGS10_DGS2", _series_feature_rows("SLOPE_DGS10_DGS2", slope)))
    if "DGS10" in series_map and "FEDFUNDS" in series_map:
        left, right = series_map["DGS10"].align(series_map["FEDFUNDS"], join="inner")
        slope = left - right
        out.append(("SLOPE_DGS10_FEDFUNDS", _series_feature_rows("SLOPE_DGS10_FEDFUNDS", slope)))
    return out


def _regime_flag_rows(series_map: dict[str, pd.Series]) -> list[dict[str, Any]]:
    now_iso = utc_now_iso()
    base_index: pd.DatetimeIndex | None = None
    if "CPIAUCSL" in series_map:
        base_index = pd.DatetimeIndex(series_map["CPIAUCSL"].index)
    elif "INDPRO" in series_map:
        base_index = pd.DatetimeIndex(series_map["INDPRO"].index)
    elif "VIXCLS" in series_map:
        base_index = pd.DatetimeIndex(series_map["VIXCLS"].index)
    elif "BAMLH0A0HYM2" in series_map:
        base_index = pd.DatetimeIndex(series_map["BAMLH0A0HYM2"].index)
    if base_index is None or len(base_index) == 0:
        return []

    def _reindex(name: str) -> pd.Series:
        series = series_map.get(name, pd.Series(dtype=float))
        if series.empty:
            return pd.Series(0.0, index=base_index)
        return series.reindex(base_index).ffill().astype(float)

    cpi_yoy_z = _safe_zscore(_reindex("CPIAUCSL").pct_change(12), 36)
    ind_yoy_z = _safe_zscore(_reindex("INDPRO").pct_change(12), 36)
    vix_z = _safe_zscore(_reindex("VIXCLS"), 252)
    credit_z = _safe_zscore(_reindex("BAMLH0A0HYM2"), 104)

    flags = {
        "inflation_up": (cpi_yoy_z > 0).astype(float),
        "growth_down": (ind_yoy_z < 0).astype(float),
        "risk_off_proxy": ((vix_z > 0) | (credit_z > 0)).astype(float),
    }
    rows: list[dict[str, Any]] = []
    for feat_name, feat_series in flags.items():
        for idx, value in feat_series.items():
            rows.append(
                {
                    "date": pd.Timestamp(idx).date().isoformat(),
                    "feat_name": feat_name,
                    "feat_value": float(value),
                    "updated_at": now_iso,
                }
            )
    return rows


def update_macro_features_for_series(
    series_ids: list[str],
    start: str | None = None,
    end: str | None = None,
) -> list[str]:
    """Recompute macro feature rows for given FRED series ids."""
    updated: list[str] = []
    series_map: dict[str, pd.Series] = {}
    for series_id in sorted(set(str(item).upper() for item in series_ids if str(item).strip())):
        rows = load_observations("FRED", series_id, start=start, end=end)
        series = normalize_series(rows)
        if series.empty:
            continue
        series_map[series_id] = series
        feature_rows = _series_feature_rows(series_id, series)
        upsert_macro_features("FRED", series_id, feature_rows)
        updated.append(series_id)

    for slope_series_id, rows in _build_slope_rows(series_map):
        if rows:
            upsert_macro_features("FRED", slope_series_id, rows)
            updated.append(slope_series_id)

    regime_rows = _regime_flag_rows(series_map)
    if regime_rows:
        upsert_macro_features("FRED", "REGIME_FLAGS", regime_rows)
        updated.append("REGIME_FLAGS")
    return sorted(set(updated))


def load_macro_feature_wide(feature_names: list[str] | None = None) -> pd.DataFrame:
    """Load feature store as date-indexed wide table for panel asof join."""
    feat_names = [name.strip() for name in (feature_names or []) if str(name).strip()]
    rows = load_macro_features(source="FRED", feat_names=feat_names or None)
    if not rows:
        return pd.DataFrame()
    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame()
    frame["date"] = pd.to_datetime(frame["date"]).dt.tz_localize(None)
    frame["column_name"] = (
        "macro_"
        + frame["series_id"].astype(str).str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True)
        + "_"
        + frame["feat_name"].astype(str).str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True)
    )
    wide = frame.pivot_table(index="date", columns="column_name", values="feat_value", aggfunc="last").sort_index()
    if wide.empty:
        return pd.DataFrame()
    wide = wide.reset_index()
    wide.columns = [str(col) for col in wide.columns]
    return wide
