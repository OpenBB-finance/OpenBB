# OpenBB Technical Analysis Extension

This extension provides Technical Analysis  tools for the OpenBB Platform.



## Installation

To install the extension, run the following command in this folder:

```bash
pip install openbb-technical
```

Documentation available [here](https://docs.openbb.co/odp/python/extensions/data-processing/technical)



| Endpoint | Category | Description |
|---|---|---|
| `bbands` | overlay | Bollinger Bands — mean +/- N standard deviations. |
| `dema` | overlay | Double-smoothed exponential moving average. |
| `donchian` | overlay | Donchian channel — rolling high/low envelope. |
| `ema` | overlay | Exponential moving average. |
| `frama` | overlay | Fractal Adaptive Moving Average — speed varies with fractal dimension. |
| `hma` | overlay | Hull moving average — reduced lag. |
| `ichimoku` | overlay | Ichimoku Cloud — five-line trend system. |
| `kama` | overlay | Kaufman Adaptive Moving Average — speed varies with efficiency. |
| `kc` | overlay | Keltner Channels — ATR-scaled envelope around an EMA. |
| `sma` | overlay | Simple moving average. |
| `supertrend` | overlay | SuperTrend — ATR-anchored trailing band. |
| `tema` | overlay | Triple-smoothed exponential moving average. |
| `vwma` | overlay | Volume-weighted moving average. |
| `wma` | overlay | Weighted moving average — linear weights. |
| `zlma` | overlay | Zero-lag exponential moving average. |
| `awesome_oscillator` | oscillator | Bill Williams' AO — 5/34 SMA difference of midpoints. |
| `cci` | oscillator | Commodity Channel Index — deviation from typical-price MA. |
| `cg` | oscillator | Center of Gravity oscillator (Ehlers). |
| `fisher` | oscillator | Fisher Transform — Gaussian-shaped oscillator. |
| `mfi` | oscillator | Money Flow Index — volume-weighted RSI. |
| `rsi` | oscillator | Relative Strength Index — momentum oscillator (0-100). |
| `stoch` | oscillator | Stochastic Oscillator — %K and %D bounded 0-100. |
| `trix` | oscillator | Triple-smoothed rate of change — noise-filtered momentum. |
| `ultimate_oscillator` | oscillator | Three-window weighted momentum oscillator. |
| `williams_r` | oscillator | Williams %R — momentum bounded -100 to 0. |
| `adx` | trend | Average Directional Index — trend strength (0-100). |
| `aroon` | trend | Aroon Up/Down — bars since highest high / lowest low. |
| `choppiness` | trend | Choppiness Index — trending vs. ranging classifier. |
| `di` | trend | Directional Indicators (+DI, -DI) — bullish/bearish pressure. |
| `macd` | trend | MACD — fast/slow EMA difference plus signal line and histogram. |
| `ad` | volume | Accumulation/Distribution Line — volume weighted by close-location. |
| `adosc` | volume | Chaikin A/D Oscillator — fast EMA minus slow EMA of A/D. |
| `obv` | volume | On-Balance Volume — cumulative signed volume. |
| `vwap` | volume | Volume-Weighted Average Price, anchored. |
| `atr` | volatility | Average True Range — Wilder's volatility measure. |
| `cones` | volatility | Volatility cones — per-window realised vs. historical band. |
| `realized_volatility` | volatility | Annualised rolling realised volatility (one of six estimators). |
| `realized_volatility_compare` | volatility | All six realised-volatility estimators side by side. |
| `demark` | structure | DeMark sequential — 9-bar setup count for exhaustion. |
| `fib` | structure | Fibonacci retracement levels between a swing high and low. |
| `pivot_points` | structure | Pivot-point support/resistance under multiple methods. |
| `autocorrelation` | stats | ACF + PACF with significance bands. |
| `clenow` | stats | Clenow Volatility-Adjusted Momentum (R^2 * regression slope). |
| `drawdown` | stats | Cumulative-return drawdown plus running peak and duration. |
| `hurst` | stats | Hurst exponent (R/S and DFA) — long-memory diagnostic. |
| `returns_stats` | stats | Distributional and risk-adjusted return statistics. |
| `stationarity` | stats | ADF + KPSS unit-root and stationarity tests. |
| `breakouts` | signal | Channel-breakout events (Donchian or Bollinger). |
| `candlestick_patterns` | signal | Single- and two-bar candlestick pattern detection. |
| `crossovers` | signal | Fast/slow moving-average crossover events. |
| `divergences` | signal | Bullish/bearish/hidden divergences between price and an oscillator. |
| `oscillator_signals` | signal | Oscillator overbought/oversold regime + crossing events. |
| `regime` | signal | Trend-strength regime classification + transitions. |
| `correlation` | multi | Rolling pairwise correlation of returns across symbols. |
| `correlation_matrix` | multi | Snapshot correlation matrix across every symbol. |
| `indicators` | multi | Programmatic catalog of all registered endpoints. |
| `multi` | multi | Run many indicators on one series and merge by date. |
| `relative_rotation` | multi | JdK RS-Ratio + RS-Momentum vs. a benchmark (RRG). |
| `screen` | multi | Filter a multi-symbol basket by indicator-driven predicates. |
