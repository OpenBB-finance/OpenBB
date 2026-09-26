# Single-Symbol Indicators

The bulk of the extension — 38 endpoints — computes a technical indicator on a single OHLC(V) series. They're grouped by family below. Every example assumes:

```python
from openbb import obb

data = obb.equity.price.historical(
    symbol="SPY", start_date="2022-01-01", provider="yfinance"
).results
```

## Overlays (15 endpoints)

Smooth or envelope the price series. Output overlays on the same axis as price.

```python
sma = obb.technical.sma(data=data, length=50).to_df()
ema = obb.technical.ema(data=data, length=20).to_df()
bb = obb.technical.bbands(data=data, length=20, std=2.0).to_df()
ich = obb.technical.ichimoku(data=data).to_df()
st = obb.technical.supertrend(data=data, length=10, multiplier=3.0).to_df()
```

Moving-average variants: `sma`, `ema`, `hma` (Hull), `wma` (Weighted), `zlma` (Zero-Lag), `tema` (Triple-EMA), `dema` (Double-EMA), `kama` (Kaufman Adaptive), `frama` (Fractal Adaptive), `vwma` (Volume-Weighted).

Bands / channels: `bbands` (Bollinger), `donchian`, `kc` (Keltner).

Composites: `ichimoku` (5-line cloud), `supertrend` (ATR-anchored trailing band).

## Oscillators (10 endpoints)

Bounded momentum indicators. Often consulted alongside an overlay for divergence signals.

```python
rsi = obb.technical.rsi(data=data, length=14).to_df()
stoch = obb.technical.stoch(data=data).to_df()  # %K and %D
mfi = obb.technical.mfi(data=data, length=14).to_df()  # volume-weighted RSI
```

All 10: `rsi`, `stoch` (Stochastic), `cci` (Commodity Channel), `fisher` (Fisher Transform), `cg` (Centre of Gravity), `williams_r`, `mfi` (Money Flow Index), `trix` (Triple Smoothed ROC), `ultimate_oscillator`, `awesome_oscillator`.

## Trend (5 endpoints)

Decompose the price series into direction + strength signals.

```python
macd = obb.technical.macd(data=data, fast=12, slow=26, signal=9).to_df()
adx = obb.technical.adx(data=data, length=14).to_df()
aroon = obb.technical.aroon(data=data, length=14).to_df()
```

`macd` (Moving Average Convergence/Divergence), `adx` (Average Directional Index), `di` (Directional Indicator +DI/-DI), `aroon`, `choppiness`.

## Volume (4 endpoints)

Use the volume column. Useful for confirming or invalidating price moves.

```python
obv = obb.technical.obv(data=data).to_df()
ad = obb.technical.ad(data=data).to_df()
vwap = obb.technical.vwap(data=data, anchor="D").to_df()    # pandas offset alias
```

`obv` (On-Balance Volume), `ad` (Accumulation/Distribution), `adosc` (Chaikin A/D Oscillator), `vwap` (Volume-Weighted Average Price).

## Volatility (4 endpoints)

```python
atr = obb.technical.atr(data=data, length=14).to_df()

# All six realised-volatility estimators side by side
rv = obb.technical.realized_volatility_compare(data=data, window=30).to_df()

# Volatility cones — historical band of rolling vol vs. realised today
cones = obb.technical.cones(data=data, model="yang_zhang").to_df()
```

`atr` (Average True Range), `realized_volatility` (single estimator), `realized_volatility_compare` (all six estimators in one frame), `cones` (per-window realised vs. historical band).

Estimators available for `realized_volatility` and `cones`: `std` (close-to-close), `parkinson` (range-based), `garman_klass` (OHLC), `hodges_tompkins` (bias-corrected close-to-close), `rogers_satchell` (drift-invariant range), `yang_zhang` (minimum-variance composite).

## Structure (3 endpoints)

Price-action levels (support/resistance/pivot points).

```python
fib = obb.technical.fib(data=data, period=120).to_df()
dem = obb.technical.demark(data=data).to_df()
piv = obb.technical.pivot_points(data=data, method="classic", anchor="day").to_df()
```

`fib` (Fibonacci retracement), `demark` (sequential 9 setup), `pivot_points` (five methods: classic, fibonacci, woodie, camarilla, demark; three anchors: day, week, month).

## Statistics (6 endpoints)

Distributional and time-series diagnostics on a price or return series.

```python
clenow = obb.technical.clenow(data=data, period=90).to_df()
dd = obb.technical.drawdown(data=data).to_df()
stats = obb.technical.returns_stats(data=data, frequency="daily").to_df()
stat = obb.technical.stationarity(data=data).to_df()
hurst = obb.technical.hurst(data=data).to_df()
acf = obb.technical.autocorrelation(data=data, max_lag=20).to_df()
```

`clenow` (volatility-adjusted momentum), `drawdown` (peak-to-trough), `returns_stats` (skew, kurtosis, sharpe, sortino, etc.), `stationarity` (ADF + KPSS hypothesis tests), `hurst` (R/S and DFA exponents), `autocorrelation` (ACF + PACF with confidence bands).

## Common parameters

Every data-consuming endpoint accepts:

- `data` — the price series (`list[Data]` / DataFrame / records).
- `index` — column to use as the time index (default `"date"`).
- `target` — for endpoints that work on a single column, the column name (default `"close"`).

Overlay/oscillator endpoints expose a `length` (or `period`) parameter for the rolling window. Most also accept `offset` to shift the output. See the per-endpoint docstring (`help(obb.technical.<name>)`) for the full parameter list.

## Choosing an input shape

`pandas.DataFrame` is convenient if you're already in pandas:

```python
import pandas as pd
df = pd.read_csv("spy.csv")
obb.technical.rsi(data=df, length=14)
```

`list[dict]` is the simplest when reading from CSV or JSON without pandas:

```python
import csv
with open("spy.csv") as f:
    records = list(csv.DictReader(f))
obb.technical.rsi(data=records, length=14)
```

Both produce identical output.
