"""Feature engineering for Quant ML training/inference."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from openbb_quant_ml.models import CloseToNextOpenHorizonPolicy, FeatureConfig, TargetMode
from openbb_quant_ml.service.cache_registry import compute_params_hash, get_feature_version, update_feature_version
from openbb_quant_ml.service.constants import FEATURE_STORE_DIR
from openbb_quant_ml.service.data_loader import build_close_panel
from openbb_quant_ml.service.macro_feature_engineering import load_macro_feature_wide


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.rolling(period).mean()
    avg_loss = losses.rolling(period).mean()
    rs = avg_gain / (avg_loss + 1e-12)
    return 100 - (100 / (1 + rs))


def _macd_hist(series: pd.Series) -> pd.Series:
    ema_fast = series.ewm(span=12, adjust=False).mean()
    ema_slow = series.ewm(span=26, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd - signal


def _safe_symbol(symbol: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"_", "-", "."} else "_" for ch in str(symbol))


def _feature_cache_path(feature_set_id: str, params_hash: str, symbol: str) -> Path:
    return FEATURE_STORE_DIR / feature_set_id / params_hash / f"{_safe_symbol(symbol)}.parquet"


def _compute_target_return(
    frame: pd.DataFrame,
    target_mode: TargetMode,
    horizon_days: int,
    close_to_next_open_horizon_policy: CloseToNextOpenHorizonPolicy = "fixed_1",
) -> pd.Series:
    close = frame["close"].astype(float)
    open_ = frame["open"].astype(float)
    h = max(1, int(horizon_days))

    if target_mode == "close_to_close":
        return close.shift(-h) / (close + 1e-12) - 1.0

    if target_mode == "close_to_next_open":
        open_h = 1 if close_to_next_open_horizon_policy == "fixed_1" else h
        return open_.shift(-open_h) / (close + 1e-12) - 1.0

    # next_open_to_close
    return close.shift(-h) / (open_.shift(-1) + 1e-12) - 1.0


def _build_regime_features(data_by_symbol: dict[str, pd.DataFrame]) -> pd.DataFrame:
    close_panel = build_close_panel(data_by_symbol)
    if close_panel.empty:
        return pd.DataFrame(columns=["date", "regime_rate_change_1d", "regime_commodity_change_1d"])

    rate_candidates = ["^TNX", "IEF", "TLT", "BIL"]
    commodity_candidates = ["DBC", "GLD", "USO", "SLV"]

    available = set(close_panel.columns)
    rate_symbol = next((s for s in rate_candidates if s in available), None)
    commodity_symbol = next((s for s in commodity_candidates if s in available), None)

    regime = pd.DataFrame(index=close_panel.index)
    regime["regime_rate_change_1d"] = (
        close_panel[rate_symbol].pct_change() if rate_symbol else pd.Series(0.0, index=close_panel.index)
    )
    regime["regime_commodity_change_1d"] = (
        close_panel[commodity_symbol].pct_change()
        if commodity_symbol
        else pd.Series(0.0, index=close_panel.index)
    )
    return regime.fillna(0.0).reset_index(names="date")


def _build_single_symbol_features(
    symbol_df: pd.DataFrame,
    feature_config: FeatureConfig,
    horizon_days: int,
    target_mode: TargetMode,
    close_to_next_open_horizon_policy: CloseToNextOpenHorizonPolicy,
) -> pd.DataFrame:
    df = symbol_df.copy().sort_values("date").reset_index(drop=True)
    if "open" not in df.columns:
        df["open"] = df["close"]

    close = df["close"].astype(float)
    open_ = df["open"].astype(float)
    daily_return = close.pct_change(fill_method=None)

    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(df["date"]).dt.tz_localize(None),
            "symbol": df["symbol"],
            "open": open_,
            "close": close,
            "daily_return": daily_return,
        }
    )

    for lag in feature_config.lags:
        frame[f"ret_lag_{lag}"] = daily_return.shift(lag)

    for window in feature_config.vol_windows:
        frame[f"vol_{window}"] = daily_return.rolling(window).std()

    for window in feature_config.momentum_windows:
        frame[f"mom_{window}"] = close / (close.shift(window) + 1e-12) - 1.0

    frame["trend_ratio_20"] = close / (close.rolling(20).mean() + 1e-12)
    frame["trend_ratio_60"] = close / (close.rolling(60).mean() + 1e-12)

    if feature_config.include_rsi:
        frame["rsi_14"] = _rsi(close, period=14)
    if feature_config.include_macd:
        frame["macd_hist"] = _macd_hist(close)

    frame["target_return"] = _compute_target_return(
        frame=frame,
        target_mode=target_mode,
        horizon_days=horizon_days,
        close_to_next_open_horizon_policy=close_to_next_open_horizon_policy,
    )
    return frame


def attach_macro_features(
    panel_df: pd.DataFrame,
    include_macro_features: bool = True,
    subset: list[str] | None = None,
    publication_lag_mode: str = "none",
) -> pd.DataFrame:
    """Attach macro feature panel by backward as-of join on date."""
    if not include_macro_features or panel_df.empty:
        return panel_df

    macro_wide = load_macro_feature_wide(feature_names=subset or [])
    if macro_wide.empty:
        return panel_df

    macro_wide = macro_wide.copy()
    macro_wide["macro_date"] = (
        pd.to_datetime(macro_wide["date"]).dt.tz_localize(None).astype("datetime64[ns]")
    )
    if publication_lag_mode == "one_day":
        macro_wide["macro_date"] = macro_wide["macro_date"] + timedelta(days=1)
    macro_wide = macro_wide.drop(columns=["date"]).sort_values("macro_date")

    left_dates = (
        panel_df[["date"]]
        .drop_duplicates()
        .rename(columns={"date": "sample_date"})
        .assign(sample_date=lambda x: pd.to_datetime(x["sample_date"]).dt.tz_localize(None).astype("datetime64[ns]"))
        .sort_values("sample_date")
    )

    aligned = pd.merge_asof(
        left_dates,
        macro_wide,
        left_on="sample_date",
        right_on="macro_date",
        direction="backward",
    )
    if "macro_date" in aligned.columns:
        invalid = aligned["macro_date"].notna() & (aligned["macro_date"] > aligned["sample_date"])
        if bool(invalid.any()):
            raise ValueError("Macro asof join leakage detected.")
    aligned = aligned.rename(columns={"sample_date": "date"}).drop(columns=["macro_date"], errors="ignore")
    return panel_df.merge(aligned, on="date", how="left")


def _validate_feature_columns(feature_columns: list[str]) -> None:
    forbidden_prefixes = ("target_", "future_", "label_")
    leaked = [col for col in feature_columns if col.startswith(forbidden_prefixes)]
    if leaked:
        raise ValueError(f"Feature leakage columns detected: {', '.join(leaked[:5])}")


def _build_or_load_symbol_features(
    symbol: str,
    symbol_df: pd.DataFrame,
    feature_config: FeatureConfig,
    horizon_days: int,
    target_mode: TargetMode,
    close_to_next_open_horizon_policy: CloseToNextOpenHorizonPolicy,
    feature_set_id: str,
    params_hash: str,
) -> pd.DataFrame:
    cache_path = _feature_cache_path(feature_set_id, params_hash, symbol)
    last_date = pd.Timestamp(pd.to_datetime(symbol_df["date"]).max()).date().isoformat()
    version_row = get_feature_version(symbol=symbol, feature_set_id=feature_set_id)
    if (
        cache_path.exists()
        and version_row
        and str(version_row.get("params_hash")) == params_hash
        and str(version_row.get("last_date")) == last_date
    ):
        cached = pd.read_parquet(cache_path)
        if not cached.empty:
            cached["date"] = pd.to_datetime(cached["date"]).dt.tz_localize(None)
            return cached

    features = _build_single_symbol_features(
        symbol_df=symbol_df,
        feature_config=feature_config,
        horizon_days=horizon_days,
        target_mode=target_mode,
        close_to_next_open_horizon_policy=close_to_next_open_horizon_policy,
    )
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(cache_path, index=False)
    update_feature_version(
        symbol=symbol,
        feature_set_id=feature_set_id,
        params_hash=params_hash,
        frame=features,
    )
    return features


def build_feature_dataset(
    data_by_symbol: dict[str, pd.DataFrame],
    feature_config: FeatureConfig,
    horizon_days: int,
    target_mode: TargetMode = "next_open_to_close",
    close_to_next_open_horizon_policy: CloseToNextOpenHorizonPolicy = "fixed_1",
    include_macro_features: bool = True,
    macro_feature_subset: list[str] | None = None,
    feature_set_id: str = "default",
    max_workers: int | None = None,
) -> tuple[pd.DataFrame, list[str], list[str]]:
    """Create panel feature dataset from symbol-wise OHLCV series."""
    if not data_by_symbol:
        return pd.DataFrame(), [], []

    params_hash = compute_params_hash(
        {
            "feature_config": feature_config.model_dump(mode="json"),
            "horizon_days": int(horizon_days),
            "target_mode": target_mode,
            "close_to_next_open_horizon_policy": close_to_next_open_horizon_policy,
        }
    )

    all_frames: list[pd.DataFrame] = []
    skipped_symbols: list[str] = []
    workers = max(1, int(max_workers or min(8, len(data_by_symbol))))

    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="feature-build") as executor:
        futures = {
            executor.submit(
                _build_or_load_symbol_features,
                symbol,
                symbol_df,
                feature_config,
                horizon_days,
                target_mode,
                close_to_next_open_horizon_policy,
                feature_set_id,
                params_hash,
            ): symbol
            for symbol, symbol_df in data_by_symbol.items()
        }
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                features = future.result()
            except Exception:
                skipped_symbols.append(symbol)
                continue
            if features.empty:
                skipped_symbols.append(symbol)
                continue
            all_frames.append(features)

    if not all_frames:
        return pd.DataFrame(), [], sorted(list(data_by_symbol.keys()))

    merged = pd.concat(all_frames, ignore_index=True)
    merged["date"] = pd.to_datetime(merged["date"]).dt.tz_localize(None)

    if feature_config.include_regime_features:
        regime = _build_regime_features(data_by_symbol)
        merged = merged.merge(regime, on="date", how="left")

    merged = attach_macro_features(
        panel_df=merged,
        include_macro_features=include_macro_features,
        subset=macro_feature_subset,
        publication_lag_mode="none",
    )

    merged = merged.sort_values(["date", "symbol"]).reset_index(drop=True)
    merged = merged.replace([np.inf, -np.inf], np.nan)

    ignore_columns = {"date", "symbol", "target_return", "close", "open", "daily_return"}
    feature_columns = [col for col in merged.columns if col not in ignore_columns]
    _validate_feature_columns(feature_columns)

    merged[feature_columns] = merged[feature_columns].fillna(0.0)
    return merged, feature_columns, sorted(set(skipped_symbols))
