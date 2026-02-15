"""Feature engineering for Quant ML training/inference."""

from __future__ import annotations

import numpy as np
import pandas as pd

from openbb_quant_ml.models import FeatureConfig
from openbb_quant_ml.service.data_loader import build_close_panel


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
    if rate_symbol:
        regime["regime_rate_change_1d"] = close_panel[rate_symbol].pct_change()
    else:
        regime["regime_rate_change_1d"] = 0.0

    if commodity_symbol:
        regime["regime_commodity_change_1d"] = close_panel[commodity_symbol].pct_change()
    else:
        regime["regime_commodity_change_1d"] = 0.0

    regime = regime.fillna(0.0).reset_index(names="date")
    return regime


def _build_single_symbol_features(
    symbol_df: pd.DataFrame,
    feature_config: FeatureConfig,
    horizon_days: int,
) -> pd.DataFrame:
    df = symbol_df.copy().sort_values("date").reset_index(drop=True)
    close = df["close"].astype(float)
    daily_return = close.pct_change()

    frame = pd.DataFrame(
        {
            "date": df["date"],
            "symbol": df["symbol"],
            "close": close,
            "daily_return": daily_return,
        }
    )

    for lag in feature_config.lags:
        frame[f"ret_lag_{lag}"] = daily_return.shift(lag)

    for window in feature_config.vol_windows:
        frame[f"vol_{window}"] = daily_return.rolling(window).std()

    for window in feature_config.momentum_windows:
        frame[f"mom_{window}"] = close / close.shift(window) - 1.0

    frame["trend_ratio_20"] = close / close.rolling(20).mean()
    frame["trend_ratio_60"] = close / close.rolling(60).mean()

    if feature_config.include_rsi:
        frame["rsi_14"] = _rsi(close, period=14)
    if feature_config.include_macd:
        frame["macd_hist"] = _macd_hist(close)

    # T+1 target return regression.
    frame["target_return"] = close.shift(-horizon_days) / close - 1.0
    return frame


def build_feature_dataset(
    data_by_symbol: dict[str, pd.DataFrame],
    feature_config: FeatureConfig,
    horizon_days: int,
) -> tuple[pd.DataFrame, list[str], list[str]]:
    """Create training dataset from symbol-wise OHLCV series."""
    all_frames: list[pd.DataFrame] = []
    skipped_symbols: list[str] = []

    for symbol, symbol_df in data_by_symbol.items():
        features = _build_single_symbol_features(symbol_df, feature_config, horizon_days)
        if features.empty:
            skipped_symbols.append(symbol)
            continue
        all_frames.append(features)

    if not all_frames:
        return pd.DataFrame(), [], list(data_by_symbol.keys())

    merged = pd.concat(all_frames, ignore_index=True)
    merged["date"] = pd.to_datetime(merged["date"]).dt.tz_localize(None)

    if feature_config.include_regime_features:
        regime = _build_regime_features(data_by_symbol)
        merged = merged.merge(regime, on="date", how="left")

    merged = merged.sort_values(["date", "symbol"]).reset_index(drop=True)
    merged = merged.replace([np.inf, -np.inf], np.nan)

    ignore_columns = {"date", "symbol", "target_return", "close", "daily_return"}
    feature_columns = [col for col in merged.columns if col not in ignore_columns]

    # Use zero imputation for robust local runs; downstream models still get standardized features.
    merged[feature_columns] = merged[feature_columns].fillna(0.0)
    return merged, feature_columns, skipped_symbols
