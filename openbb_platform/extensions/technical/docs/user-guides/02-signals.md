# Signal Endpoints

The `/signals/` subrouter exposes six event-detection endpoints. Unlike the indicator endpoints (which return a dense per-bar series), these emit a **sparse list of detected events** — rows only on bars where the condition fires.

All examples assume:

```python
from openbb import obb

data = obb.equity.price.historical(
    symbol="SPY", start_date="2022-01-01", provider="yfinance"
).results
```

## Crossovers

Detects moving-average crossover events between a fast and slow MA.

```python
events = obb.technical.signals.crossovers(
    data=data,
    fast_length=20,
    slow_length=50,
    mamode="sma",       # or "ema", "wma", "hma", "zlma"
).results
```

Each event row carries: `date`, `direction` (`"bullish"` / `"bearish"`), `fast_value`, `slow_value`, `price`, `distance` (price gap between the two MAs at the crossover bar).

## Oscillator Signals

Labels every bar with a regime (`overbought` / `oversold` / `neutral`) for the chosen oscillator and flags the four boundary-crossing events.

```python
sig = obb.technical.signals.oscillator_signals(
    data=data,
    indicator="rsi",                 # or "mfi", "stoch", "williams_r", "cci"
    length=14,
    overbought_threshold=70.0,       # optional override; defaults per indicator
    oversold_threshold=30.0,
).results
```

This is a **dense** output (one row per bar) with boolean flags `crossed_into_overbought`, `crossed_into_oversold`, `crossed_out_of_overbought`, `crossed_out_of_oversold` — convenient for plotting shaded regimes and vertical event markers.

## Breakouts

Detects when price closes beyond a rolling-channel envelope.

```python
events = obb.technical.signals.breakouts(
    data=data,
    method="donchian",   # rolling high/low; or "bollinger" (mean +/- stdev band)
    length=20,
    band_std=2.0,        # only used for "bollinger"
).results
```

Each event row carries: `date`, `direction`, `price`, `band` (the breached level), `magnitude` (signed price - band), `bars_in_range` (consolidation length).

## Divergences

Detects classical bullish/bearish/hidden/exaggerated divergences between price and an oscillator across the last `lookback` bars.

```python
events = obb.technical.signals.divergences(
    data=data,
    indicator="rsi",                 # or "macd", "stoch", "cci"
    indicator_length=14,
    lookback=60,
    swing_window=3,                  # bars on either side that define a swing high/low
).results
```

Each event row identifies the kind, the two swing dates that form the pattern, the indicator and price values at each swing, and the bar where the divergence was confirmed.

## Candlestick Patterns

Single-bar and two-bar pattern detection.

```python
events = obb.technical.signals.candlestick_patterns(
    data=data,
    patterns=["doji", "hammer", "shooting_star", "engulfing"],   # None = all
).results
```

Each event row carries: `date`, `pattern` name, `direction` (`bullish` / `bearish` / `neutral`), `confidence` (0-1, based on body/wick ratios meeting textbook thresholds).

Supported patterns: `doji`, `hammer`, `inverted_hammer`, `hanging_man`, `shooting_star`, `bullish_engulfing`, `bearish_engulfing`, `morning_star`, `evening_star`, `three_white_soldiers`, `three_black_crows`, `harami_bullish`, `harami_bearish`, `piercing`, `dark_cloud_cover`. Pass `patterns=None` to scan for all of them.

## Regime

Classifies each bar into one of four regimes based on ADX strength and price trendiness.

```python
out = obb.technical.signals.regime(
    data=data,
    length=14,
    adx_strong_threshold=25.0,
    adx_weak_threshold=20.0,
).results
```

Regimes: `strong_trend`, `weak_trend`, `ranging`, `transition`. Each row also flags `regime_changed` on bars where the label shifts — useful for triggering position-sizing rules tied to regime persistence.

## Backtest pattern

The sparse event endpoints (`crossovers`, `breakouts`, `divergences`, `candlestick_patterns`) are designed to plug directly into a vectorised backtester:

```python
events = obb.technical.signals.crossovers(data=data, fast_length=20, slow_length=50).results
trades = [
    e for e in events
    if e.direction == "bullish" and e.distance > 0.5  # filter weak crossovers
]
```

The dense endpoints (`oscillator_signals`, `regime`) are designed for filter conditions:

```python
sig = obb.technical.signals.oscillator_signals(data=data, indicator="rsi", length=14).results
regime = obb.technical.signals.regime(data=data).results

# Only act on RSI crosses during a strong trend
combined = [
    s for s, r in zip(sig, regime)
    if s.crossed_into_overbought and r.regime == "strong_trend"
]
```
