"""Indicator computation for trading runtime."""

from __future__ import annotations

import pandas as pd

from openbb_quant_ml.service import feature_engineering as features


def compute_indicator_frame(
    frame: pd.DataFrame,
    *,
    ema_fast: int = 12,
    ema_slow: int = 26,
    breakout_lookback: int = 20,
    volume_window: int = 20,
) -> pd.DataFrame:
    """Attach runtime indicators needed by built-in trading strategies."""
    if frame.empty:
        return frame.copy()
    enriched = frame.copy().sort_values("date").reset_index(drop=True)
    close = enriched["close"].astype(float)
    high = enriched["high"].astype(float)
    low = enriched["low"].astype(float)
    volume = enriched["volume"].astype(float)
    enriched["ema_fast"] = close.ewm(span=max(ema_fast, 2), adjust=False).mean()
    enriched["ema_slow"] = close.ewm(span=max(ema_slow, 3), adjust=False).mean()
    enriched["sma_20"] = close.rolling(20).mean()
    enriched["sma_50"] = close.rolling(50).mean()
    enriched["rsi"] = features._rsi(close, period=14)
    enriched["macd_hist"] = features._macd_hist(close)
    enriched["bollinger_pct_b"] = features._bollinger_percent_b(close, window=20, n_std=2.0)
    enriched["atr"] = features._atr(high, low, close, period=14)
    enriched["atr_pct"] = enriched["atr"] / close.replace(0.0, pd.NA)
    enriched["recent_return"] = close.pct_change(5)
    enriched["volume_avg"] = volume.rolling(max(volume_window, 5)).mean()
    enriched["volume_change_pct"] = volume / enriched["volume_avg"].replace(0.0, pd.NA) - 1.0
    enriched["avg_dollar_volume"] = (close * volume).rolling(max(volume_window, 5)).mean()
    enriched["ma_relation"] = enriched["ema_fast"] - enriched["ema_slow"]
    enriched["rolling_high_breakout"] = close.rolling(max(breakout_lookback, 5)).max().shift(1)
    enriched["rolling_low_exit"] = close.rolling(max(breakout_lookback, 5)).min().shift(1)
    return enriched
