"""Macro time-series transform utilities."""

from __future__ import annotations

from datetime import date
from typing import Literal

import numpy as np
import pandas as pd

TransformType = Literal[
    "level",
    "diff",
    "log",
    "mom",
    "yoy",
    "annualized_mom",
    "qoq_saar",
    "zscore",
    "percentile_5y",
    "yoy_zscore",
]
FreqType = Literal["native", "D", "W", "M", "Q"]
FillType = Literal["ffill", "interpolate", "none"]


def normalize_series(rows: list[dict[str, object]]) -> pd.Series:
    """Convert row payload to datetime-indexed float series."""
    if not rows:
        return pd.Series(dtype=float)
    frame = pd.DataFrame(rows)
    if "date" not in frame.columns:
        return pd.Series(dtype=float)
    frame["date"] = pd.to_datetime(frame["date"], utc=False, errors="coerce")
    frame = frame.dropna(subset=["date"]).sort_values("date")
    values = pd.to_numeric(frame.get("value"), errors="coerce")
    series = pd.Series(values.to_numpy(dtype=float), index=frame["date"], dtype=float)
    series = series[~series.index.duplicated(keep="last")]
    return series.sort_index()


def _infer_observation_step_days(series: pd.Series) -> float:
    if series.size < 3:
        return 30.0
    diffs = pd.Series(series.index).sort_values().diff().dropna()
    if diffs.empty:
        return 30.0
    median = diffs.median()
    return max(float(median.total_seconds()) / 86_400.0, 1.0)


def infer_frequency_label(series: pd.Series) -> str:
    """Best-effort frequency label."""
    step = _infer_observation_step_days(series)
    if step <= 2:
        return "daily"
    if step <= 9:
        return "weekly"
    if step <= 40:
        return "monthly"
    return "quarterly"


def default_publish_lag_days(frequency_label: str | None) -> int:
    """Default lag days by frequency."""
    if not frequency_label:
        return 30
    freq = frequency_label.lower()
    if "day" in freq or freq == "d":
        return 1
    if "week" in freq or freq == "w":
        return 1
    if "month" in freq or freq == "m":
        return 30
    if "quarter" in freq or freq == "q":
        return 90
    return 30


def lag_period_text(lag_days: int, frequency_label: str | None) -> str:
    """Serialize lag as coarse ISO-like label."""
    if lag_days <= 0:
        return "P0D"
    freq = (frequency_label or "").lower()
    if "month" in freq and 28 <= lag_days <= 31:
        return "P1M"
    if "quarter" in freq and 89 <= lag_days <= 92:
        return "P1Q"
    return f"P{lag_days}D"


def apply_publish_lag(series: pd.Series, lag_days: int) -> pd.Series:
    """Shift observable date by publication lag."""
    if lag_days <= 0 or series.empty:
        return series
    shifted = series.copy()
    shifted.index = shifted.index + pd.to_timedelta(int(lag_days), unit="D")
    return shifted


def _target_freq_alias(freq: FreqType) -> str | None:
    if freq == "native":
        return None
    if freq == "D":
        return "D"
    if freq == "W":
        return "W-FRI"
    if freq == "M":
        return "ME"
    if freq == "Q":
        return "QE"
    return None


def _apply_fill(series: pd.Series, fill: FillType) -> pd.Series:
    if fill == "none" or series.empty:
        return series
    if fill == "interpolate":
        return series.interpolate(limit_direction="both")
    return series.ffill()


def resample_series(
    series: pd.Series,
    freq: FreqType = "native",
    fill: FillType = "ffill",
    start: date | None = None,
    end: date | None = None,
) -> pd.Series:
    """Resample and optionally bound the index range."""
    if series.empty:
        return series
    out = series.sort_index()
    alias = _target_freq_alias(freq)
    if alias is not None:
        out = out.resample(alias).last()
    if start is not None:
        out = out[out.index >= pd.Timestamp(start)]
    if end is not None:
        out = out[out.index <= pd.Timestamp(end)]
    if alias is not None and out.size > 0:
        idx = pd.date_range(out.index.min(), out.index.max(), freq=alias)
        out = out.reindex(idx)
    out = _apply_fill(out, fill)
    return out.dropna(how="all")


def _seasonal_periods(series: pd.Series) -> int:
    step = _infer_observation_step_days(series)
    if step <= 2:
        return 252
    if step <= 9:
        return 52
    if step <= 40:
        return 12
    return 4


def _annualize_factor(series: pd.Series) -> float:
    step = _infer_observation_step_days(series)
    if step <= 2:
        return 252.0
    if step <= 9:
        return 52.0
    if step <= 40:
        return 12.0
    return 4.0


def _zscore_full(series: pd.Series) -> pd.Series:
    std = float(series.std(ddof=0))
    if std <= 0 or np.isnan(std):
        return pd.Series(0.0, index=series.index)
    mean = float(series.mean())
    return (series - mean) / (std + 1e-12)


def _rolling_percentile_last(window: np.ndarray) -> float:
    clean = window[~np.isnan(window)]
    if clean.size == 0:
        return np.nan
    return float((clean <= clean[-1]).sum() / clean.size)


def _percentile_5y(series: pd.Series) -> pd.Series:
    periods = _seasonal_periods(series) * 5
    periods = max(periods, 20)
    return series.rolling(periods, min_periods=max(5, periods // 5)).apply(
        lambda arr: _rolling_percentile_last(np.asarray(arr, dtype=float)),
        raw=True,
    )


def apply_transform(series: pd.Series, transform: TransformType = "level") -> pd.Series:
    """Apply transformation."""
    if series.empty:
        return series
    name = str(transform or "level").lower()
    clean = pd.to_numeric(series, errors="coerce").astype(float)
    if name == "level":
        return clean
    if name == "diff":
        return clean.diff()
    if name == "log":
        safe = clean.where(clean > 0)
        return np.log(safe)
    if name == "mom":
        return clean.pct_change(fill_method=None)
    if name == "yoy":
        periods = _seasonal_periods(clean)
        return clean.pct_change(periods=periods, fill_method=None)
    if name == "annualized_mom":
        factor = _annualize_factor(clean)
        mom = clean.pct_change(fill_method=None)
        return (1.0 + mom).pow(factor) - 1.0
    if name == "qoq_saar":
        qoq = clean.pct_change(periods=1, fill_method=None)
        return (1.0 + qoq).pow(4.0) - 1.0
    if name == "zscore":
        return _zscore_full(clean)
    if name == "percentile_5y":
        return _percentile_5y(clean)
    if name == "yoy_zscore":
        return _zscore_full(apply_transform(clean, "yoy"))
    return clean


def compute_stats(series: pd.Series) -> dict[str, float | None]:
    """Compute compact stats payload."""
    if series.empty:
        return {
            "last": None,
            "change_1m": None,
            "change_3m": None,
            "z": None,
            "percentile_5y": None,
        }

    clean = series.dropna()
    if clean.empty:
        return {
            "last": None,
            "change_1m": None,
            "change_3m": None,
            "z": None,
            "percentile_5y": None,
        }

    freq_label = infer_frequency_label(clean)
    if freq_label == "daily":
        one_m = 21
        three_m = 63
    elif freq_label == "weekly":
        one_m = 4
        three_m = 13
    elif freq_label == "monthly":
        one_m = 1
        three_m = 3
    else:
        one_m = 1
        three_m = 1

    last = float(clean.iloc[-1])
    change_1m = float(last - clean.iloc[-1 - one_m]) if clean.size > one_m else None
    change_3m = float(last - clean.iloc[-1 - three_m]) if clean.size > three_m else None
    z = float(_zscore_full(clean).iloc[-1]) if clean.size > 2 else None
    percentile = float(_percentile_5y(clean).iloc[-1]) if clean.size > 20 else None
    return {
        "last": last,
        "change_1m": change_1m,
        "change_3m": change_3m,
        "z": z,
        "percentile_5y": percentile,
    }
