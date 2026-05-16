# API Reference

Auto-generated from the registered router by `docs/_generate_api_reference.py`. Endpoint names match the Python interface (`obb.technical.<name>` or `obb.technical.signals.<name>`) and the HTTP path (`POST /api/v1/technical/<name>`).

**Total endpoints**: 59

Each endpoint also takes `data` (the OHLC(V) price series) which is omitted from the parameter tables below. `requires_columns` lists the OHLC(V) columns the endpoint reads from `data`.

---

## Overlays

Price-smoothing and envelope indicators plotted on the same axis as price.

### `bbands`

_Query parameters for the Bollinger Bands endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `target` | `str` | `close` |  |  |
| `index` | `str` | `date` |  |  |
| `length` | `int` | `20` | `gt=0` | Moving-average period. |
| `std` | `float` | `2.0` | `gt=0` | Standard-deviation multiplier. |
| `mamode` | `Literal["sma", "ema", "wma", "rma"]` | `sma` |  | Type of moving average for the middle band. |
| `offset` | `int` | `0` |  |  |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `lower` | `float \| None` | yes | Lower band — middle minus ``std`` deviations. |
| `middle` | `float \| None` | yes | Center moving average. |
| `upper` | `float \| None` | yes | Upper band — middle plus ``std`` deviations. |
| `bandwidth` | `float \| None` | yes | ``(upper - lower) / middle`` — width relative to the centre. |
| `percent` | `float \| None` | yes | ``(price - lower) / (upper - lower)`` — position within the band. |

### `dema`

_Query parameters for the Double Exponential Moving Average endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `target` | `str` | `close` |  |  |
| `index` | `str` | `date` |  |  |
| `length` | `int` | `10` | `gt=0` | DEMA period. |
| `offset` | `int` | `0` |  |  |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `dema` | `float \| None` | yes | Double EMA — ``2*EMA - EMA(EMA)``. |

### `donchian`

_Query parameters for the Donchian Channel endpoint._

**Required input columns**: `high`, `low`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `lower_length` | `int` | `20` | `gt=0` | Lookback for the lower band. |
| `upper_length` | `int` | `20` | `gt=0` | Lookback for the upper band. |
| `offset` | `int` | `0` |  |  |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `lower` | `float \| None` | yes | Trailing min over ``lower_length`` bars. |
| `middle` | `float \| None` | yes | Midpoint between upper and lower bands. |
| `upper` | `float \| None` | yes | Trailing max over ``upper_length`` bars. |

### `ema`

_Query parameters for the Exponential Moving Average endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `target` | `str` | `close` |  |  |
| `index` | `str` | `date` |  |  |
| `length` | `int` | `50` | `gt=0` | EMA period. |
| `offset` | `int` | `0` |  |  |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `ema` | `float \| None` | yes | Exponential moving average of ``target``. |

### `frama`

_Query parameters for the Fractal Adaptive Moving Average endpoint._

**Required input columns**: `high`, `low`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `window` | `int` | `10` | `gt=0` | Window length — must be even. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `frama` | `float \| None` | yes | Fractal adaptive moving average — Ehlers (2005). |

### `hma`

_Query parameters for the Hull Moving Average endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `target` | `str` | `close` |  |  |
| `index` | `str` | `date` |  |  |
| `length` | `int` | `50` | `gt=0` | HMA period. |
| `offset` | `int` | `0` |  |  |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `hma` | `float \| None` | yes | Hull moving average — lag-reduced WMA blend. |

### `ichimoku`

_Query parameters for the Ichimoku Cloud endpoint._

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `conversion` | `int` | `9` | `gt=0` | Tenkan-sen lookback. |
| `base` | `int` | `26` | `gt=0` | Kijun-sen lookback. |
| `lagging` | `int` | `52` | `gt=0` | Senkou Span B lookback. |
| `offset` | `int` | `26` | `gt=0` | Forward projection for the cloud. |
| `lookahead` | `bool` | `False` |  | If ``True``, emit the Chikou Span (look-ahead). Off by default to prevent data leakage. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `tenkan_sen` | `float \| None` | yes | Conversion line. |
| `kijun_sen` | `float \| None` | yes | Base line. |
| `senkou_a` | `float \| None` | yes | Leading span A. |
| `senkou_b` | `float \| None` | yes | Leading span B. |
| `chikou_span` | `float \| None` | yes | Lagging span. Always ``None`` when ``lookahead=False``. |

### `kama`

_Query parameters for the Kaufman Adaptive Moving Average endpoint._

**Required input columns**: `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `target` | `str` | `close` |  |  |
| `index` | `str` | `date` |  |  |
| `length` | `int` | `10` | `gt=0` | Efficiency-ratio lookback. |
| `fast` | `int` | `2` | `gt=0` | Fastest EMA period bound. |
| `slow` | `int` | `30` | `gt=0` | Slowest EMA period bound. |
| `offset` | `int` | `0` |  |  |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `kama` | `float \| None` | yes | Kaufman adaptive moving average of ``target``. |

### `kc`

_Query parameters for the Keltner Channel endpoint._

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `length` | `int` | `20` | `gt=0` | Centerline MA period. |
| `scalar` | `float` | `2.0` | `gt=0` | ATR multiplier for the bands. |
| `mamode` | `Literal["ema", "sma"]` | `ema` |  | Centreline moving-average type. |
| `offset` | `int` | `0` | `ge=0` |  |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `lower` | `float \| None` | yes | Centerline minus ``scalar * ATR``. |
| `middle` | `float \| None` | yes | Centreline moving average. |
| `upper` | `float \| None` | yes | Centerline plus ``scalar * ATR``. |

### `sma`

_Query parameters for the Simple Moving Average endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `target` | `str` | `close` |  | Column to smooth. |
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `length` | `int` | `50` | `gt=0` | Window length in bars. |
| `offset` | `int` | `0` |  | Output offset, positive shifts forward. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no | Observation date. |
| `sma` | `float \| None` | yes | Simple moving average of ``target`` over ``length`` bars. |

### `supertrend`

_Query parameters for the Supertrend endpoint._

**Required input columns**: `low`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `length` | `int` | `7` | `gt=0` | ATR lookback. |
| `multiplier` | `float` | `3.0` | `gt=0` | ATR multiplier for the bands. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `supertrend` | `float \| None` | yes | Current trailing-stop value. |
| `direction` | `Literal[-1, 1] \| None` | yes | ``1`` when the trend is up, ``-1`` when down. ``None`` during warm-up. |
| `long_band` | `float \| None` | yes | Long-side band — populated only when the trend is up. |
| `short_band` | `float \| None` | yes | Short-side band — populated only when the trend is down. |

### `tema`

_Query parameters for the Triple Exponential Moving Average endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `target` | `str` | `close` |  |  |
| `index` | `str` | `date` |  |  |
| `length` | `int` | `10` | `gt=0` | TEMA period. |
| `offset` | `int` | `0` |  |  |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `tema` | `float \| None` | yes | Triple EMA — ``3*EMA - 3*EMA(EMA) + EMA(EMA(EMA))``. |

### `vwma`

_Query parameters for the Volume Weighted Moving Average endpoint._

**Required input columns**: `close`, `volume`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `length` | `int` | `10` | `gt=0` | VWMA period. |
| `offset` | `int` | `0` |  |  |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `vwma` | `float \| None` | yes | Volume weighted moving average of close. |

### `wma`

_Query parameters for the Weighted Moving Average endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `target` | `str` | `close` |  |  |
| `index` | `str` | `date` |  |  |
| `length` | `int` | `50` | `gt=0` | WMA period. |
| `offset` | `int` | `0` |  |  |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `wma` | `float \| None` | yes | Linearly-weighted moving average of ``target``. |

### `zlma`

_Query parameters for the Zero-Lag Moving Average endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `target` | `str` | `close` |  |  |
| `index` | `str` | `date` |  |  |
| `length` | `int` | `50` | `gt=0` | ZLMA period. |
| `offset` | `int` | `0` |  |  |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `zlma` | `float \| None` | yes | Zero-Lag EMA of ``target`` — Ehlers/Way de-lagged EMA. |

## Oscillators

Bounded momentum indicators.

### `awesome_oscillator`

_Query parameters for Bill Williams' Awesome Oscillator endpoint._

**Required input columns**: `high`, `low`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `fast` | `int` | `5` | `gt=0` | Short SMA window on median price. |
| `slow` | `int` | `34` | `gt=0` | Long SMA window on median price. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `awesome_oscillator` | `float \| None` | yes | Fast SMA minus slow SMA of median price. |

### `cci`

_Query parameters for the Commodity Channel Index endpoint._

**Required input columns**: `high`, `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `length` | `int` | `14` | `gt=0` | Lookback window in bars. |
| `scalar` | `float` | `0.015` | `gt=0` | Mean-deviation scaling factor (Lambert's original constant). |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `cci` | `float \| None` | yes | CCI value over the trailing ``length`` bars. |

### `cg`

_Query parameters for the Center of Gravity endpoint._

**Required input columns**: `high`, `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `length` | `int` | `14` | `gt=0` | Lookback window in bars. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `cg` | `float \| None` | yes | Center of Gravity value. |

### `fisher`

_Query parameters for the Fisher Transform endpoint._

**Required input columns**: `high`, `low`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `length` | `int` | `14` | `gt=0` | Fisher transform window. |
| `signal` | `int` | `1` | `gt=0` | Lag for the signal line. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `fisher` | `float \| None` | yes | Fisher Transform value. |
| `signal` | `float \| None` | yes | Lagged Fisher signal line. |

### `mfi`

_Query parameters for the Money Flow Index endpoint._

**Required input columns**: `high`, `low`, `close`, `volume`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `length` | `int` | `14` | `gt=0` | Lookback window in bars. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `mfi` | `float \| None` | yes | Money Flow Index — volume-weighted RSI on typical price (0–100). |

### `rsi`

_Query parameters for the Relative Strength Index endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `target` | `str` | `close` |  | Target column to apply RSI to. |
| `length` | `int` | `14` | `gt=0` | Lookback window in bars. |
| `scalar` | `float` | `100.0` | `gt=0` | Output scaling. ``100`` produces the conventional 0–100 range. |
| `drift` | `int` | `1` | `gt=0` | Difference period for momentum. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no | Observation date. |
| `rsi` | `float \| None` | yes | RSI value over the trailing ``length`` bars on ``target``. |

### `stoch`

_Query parameters for the Stochastic Oscillator endpoint._

**Required input columns**: `high`, `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `fast_k_period` | `int` | `14` | `gt=0` | Fast %K lookback. |
| `slow_d_period` | `int` | `3` | `gt=0` | Slow %D smoothing. |
| `slow_k_period` | `int` | `3` | `gt=0` | Slow %K smoothing. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `k` | `float \| None` | yes | %K — current close vs. recent range. |
| `d` | `float \| None` | yes | %D — moving average of %K. |

### `trix`

_Query parameters for the TRIX endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `target` | `str` | `close` |  | Target column to apply TRIX to. |
| `length` | `int` | `30` | `gt=0` | Triple-EMA window. |
| `signal` | `int` | `9` | `gt=0` | Signal line EMA length. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `trix` | `float \| None` | yes | 1-day ROC of a triple-EMA of ``target``. |
| `signal` | `float \| None` | yes | EMA of TRIX, length ``signal``. |

### `ultimate_oscillator`

_Query parameters for Larry Williams' Ultimate Oscillator endpoint._

**Required input columns**: `high`, `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `fast` | `int` | `7` | `gt=0` | Short-period lookback. |
| `medium` | `int` | `14` | `gt=0` | Medium-period lookback. |
| `slow` | `int` | `28` | `gt=0` | Long-period lookback. |
| `fast_weight` | `float` | `4.0` | `gt=0` | Weight applied to the fast period. |
| `medium_weight` | `float` | `2.0` | `gt=0` | Weight applied to the medium period. |
| `slow_weight` | `float` | `1.0` | `gt=0` | Weight applied to the slow period. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `ultimate_oscillator` | `float \| None` | yes | Weighted blend of buying pressure over three timeframes (0–100). |

### `williams_r`

_Query parameters for the Williams %R endpoint._

**Required input columns**: `high`, `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `length` | `int` | `14` | `gt=0` | Lookback window in bars. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `williams_r` | `float \| None` | yes | Williams %R — close relative to the trailing high/low range (−100 to 0). |

## Trend

Direction and strength of the prevailing move.

### `adx`

_Query parameters for the ADX endpoint._

**Required input columns**: `high`, `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `length` | `int` | `14` | `gt=0` | ADX lookback window. |
| `scalar` | `float` | `100.0` | `gt=0` | Output magnification factor. |
| `drift` | `int` | `1` | `gt=0` | Difference period for directional movement. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `adx` | `float \| None` | yes | Average Directional Index — trend-strength score. |

### `aroon`

_Query parameters for the Aroon endpoint._

**Required input columns**: `high`, `low`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `length` | `int` | `25` | `gt=0` | Aroon lookback window. |
| `scalar` | `float` | `100.0` | `gt=0` | Output magnification factor. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `aroon_up` | `float \| None` | yes | Bars since the highest high, scaled. |
| `aroon_down` | `float \| None` | yes | Bars since the lowest low, scaled. |
| `aroon_oscillator` | `float \| None` | yes | ``aroon_up`` minus ``aroon_down``. |

### `choppiness`

_Query parameters for the Choppiness Index endpoint._

**Required input columns**: `high`, `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `length` | `int` | `14` | `gt=0` | Choppiness lookback window. |
| `atr_length` | `int` | `1` | `gt=0` | ATR window used inside choppiness. |
| `scalar` | `float` | `100.0` | `gt=0` | Output magnification factor. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `choppiness` | `float \| None` | yes | Choppiness Index — high values mean sideways action. |

### `di`

_Query parameters for the Directional Indicators endpoint._

**Required input columns**: `high`, `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `length` | `int` | `14` | `gt=0` | Lookback window for +DI / -DI. |
| `scalar` | `float` | `100.0` | `gt=0` | Output magnification factor. |
| `drift` | `int` | `1` | `gt=0` | Difference period for directional movement. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `plus_di` | `float \| None` | yes | Positive Directional Indicator (+DI). |
| `minus_di` | `float \| None` | yes | Negative Directional Indicator (-DI). |
| `dx` | `float \| None` | yes | Directional Index — \|+DI - -DI\| / (+DI + -DI) * scalar. |

### `macd`

_Query parameters for the MACD endpoint._

**Required input columns**: `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `target` | `str` | `close` |  | Column to compute MACD on. |
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `fast` | `int` | `12` | `gt=0` | Fast EMA window. |
| `slow` | `int` | `26` | `gt=0` | Slow EMA window. |
| `signal` | `int` | `9` | `gt=0` | Signal-line EMA window. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `macd` | `float \| None` | yes | MACD line — fast EMA minus slow EMA. |
| `signal` | `float \| None` | yes | Signal line — EMA of MACD. |
| `histogram` | `float \| None` | yes | MACD minus signal. |

## Volume

Volume-weighted indicators.

### `ad`

_Query parameters for the Accumulation/Distribution line endpoint._

**Required input columns**: `high`, `low`, `close`, `volume`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `offset` | `int` | `0` |  | Periods to offset the result. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no | Observation date. |
| `ad` | `float \| None` | yes | Accumulation/Distribution cumulative line. |

### `adosc`

_Query parameters for the Chaikin Accumulation/Distribution Oscillator endpoint._

**Required input columns**: `high`, `low`, `close`, `volume`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `fast` | `int` | `3` | `gt=0` | Fast EMA window. |
| `slow` | `int` | `10` | `gt=0` | Slow EMA window. |
| `offset` | `int` | `0` |  | Periods to offset the result. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no | Observation date. |
| `adosc` | `float \| None` | yes | Chaikin Accumulation/Distribution Oscillator. |

### `obv`

_Query parameters for the On-Balance Volume endpoint._

**Required input columns**: `close`, `volume`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `offset` | `int` | `0` |  | Periods to offset the result. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no | Observation date. |
| `obv` | `float \| None` | yes | On-Balance Volume cumulative total. |

### `vwap`

_Query parameters for the Volume-Weighted Average Price endpoint._

**Required input columns**: `high`, `low`, `close`, `volume`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `anchor` | `str` | `D` |  | Resample anchor — pandas offset alias such as ``D``, ``W``, ``ME``. Determines the VWAP reset boundary. |
| `offset` | `int` | `0` |  | Periods to offset the result. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no | Observation date. |
| `vwap` | `float \| None` | yes | Volume-weighted average price. |

## Volatility

Realised-volatility estimators and the ATR family.

### `atr`

_Query parameters for the Average True Range endpoint._

**Required input columns**: `high`, `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `length` | `int` | `14` | `gt=0` | ATR lookback window. |
| `mamode` | `Literal["sma", "ema", "wma", "rma"]` | `rma` |  | Smoothing applied to true-range. ``rma`` is the Wilder default. |
| `drift` | `int` | `1` | `gt=0` | Difference period for true-range. |
| `offset` | `int` | `0` |  |  |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `atr` | `float \| None` | yes | Average true range over the trailing ``length`` bars. |

### `cones`

_Query parameters for the volatility-cones endpoint._

**Required input columns**: `low`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `lower_q` | `float` | `0.25` |  | Lower quantile for the cone band (0–1, exclusive of 1). |
| `upper_q` | `float` | `0.75` |  | Upper quantile for the cone band (0–1, exclusive of 1). |
| `model` | `Literal["std", "parkinson", "garman_klass", "hodges_tompkins", "rogers_satchell", "yang_zhang"]` | `std` |  |  |
| `is_crypto` | `bool` | `False` |  |  |
| `trading_periods` | `Annotated[int, Gt(gt=0)] \| None` | *required* |  |  |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `window` | `int` | no | Rolling window length in bars. |
| `realized` | `float \| None` | yes | Most-recent annualised volatility. |
| `min` | `float \| None` | yes |  |
| `lower` | `float \| None` | yes | Lower-quantile cone band. |
| `median` | `float \| None` | yes |  |
| `upper` | `float \| None` | yes | Upper-quantile cone band. |
| `max` | `float \| None` | yes |  |

### `realized_volatility`

_Query parameters for the realized-volatility endpoint._

**Required input columns**: `open`, `high`, `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `model` | `Literal["std", "parkinson", "garman_klass", "hodges_tompkins", "rogers_satchell", "yang_zhang"]` | `yang_zhang` |  | Volatility estimator. ``yang_zhang`` is the lowest-error blend; ``parkinson`` and ``rogers_satchell`` are range-based and drift-invariant; ``hodges_tompkins`` is bias-corrected close-to-close. |
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `window` | `int` | `30` | `gt=0` | Rolling window length in bars. |
| `trading_periods` | `Annotated[int, Gt(gt=0)] \| None` | *required* |  | Annualisation factor. ``None`` resolves to 365 when ``is_crypto`` is true, otherwise 252. |
| `is_crypto` | `bool` | `False` |  | When true and ``trading_periods`` is unset, annualise over 365 instead of 252. |
| `clean` | `bool` | `True` |  | Drop the leading warm-up rows where the rolling window is incomplete. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no | Observation date. |
| `volatility` | `float \| None` | yes | Annualised realised volatility per the chosen ``model`` over the trailing ``window`` bars. ``None`` during warm-up when ``clean=False``. |
| `model` | `Literal['std', 'parkinson', 'garman_klass', 'hodges_tompkins', 'rogers_satchell', 'yang_zhang']` | no | Echoed on every row so the response is self-describing. |
| `window` | `int` | no | Window used to produce this row. |
| `trading_periods` | `int` | no | Annualisation factor used to produce this row. |

### `realized_volatility_compare`

_Query parameters for the side-by-side realized-volatility endpoint._

**Required input columns**: `open`, `high`, `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `models` | `Literal["std", "parkinson", "garman_klass", "hodges_tompkins", "rogers_satchell", "yang_zhang"]` | `['std', 'parkinson', 'garman_klass', 'hodges_tompkins', 'rogers_satchell', 'yang_zhang']` |  | Estimators to compute. Defaults to all six. |
| `index` | `str` | `date` |  |  |
| `window` | `int` | `30` | `gt=0` |  |
| `trading_periods` | `Annotated[int, Gt(gt=0)] \| None` | *required* |  |  |
| `is_crypto` | `bool` | `False` |  |  |
| `clean` | `bool` | `True` |  | Drop rows where ANY requested model has not yet warmed up. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `std` | `float \| None` | yes |  |
| `parkinson` | `float \| None` | yes |  |
| `garman_klass` | `float \| None` | yes |  |
| `hodges_tompkins` | `float \| None` | yes |  |
| `rogers_satchell` | `float \| None` | yes |  |
| `yang_zhang` | `float \| None` | yes |  |

## Structure

Price-action support/resistance levels.

### `demark`

_Query parameters for the DeMark sequential endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `target` | `str` | `close` |  | Column to evaluate. |
| `show_all` | `bool` | `True` |  | When True show counts 1-13; False shows only 6-9. |
| `asint` | `bool` | `True` |  | Cast counts to integers and fill NaN with 0. |
| `offset` | `int` | `0` |  | Periods to offset the result. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `up` | `int \| float \| None` | yes | Upward sequential count. |
| `down` | `int \| float \| None` | yes | Downward sequential count. |

### `fib`

_Query parameters for the Fibonacci-retracement endpoint._

**Required input columns**: `high`, `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `close_column` | `Literal["close", "adj_close"]` | `close` |  | Column used for high/low detection. |
| `period` | `int` | `120` | `gt=0` | Lookback in bars for retracement. |
| `start_date` | `str \| None` | *required* |  | Explicit retracement start date. |
| `end_date` | `str \| None` | *required* |  | Explicit retracement end date. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `level` | `str` | no | Retracement percentage label, e.g. ``38.2%``. |
| `price` | `float` | no | Price at the retracement level. |

### `pivot_points`

_Query parameters for the pivot-points endpoint._

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  |  |
| `method` | `Literal["classic", "fibonacci", "woodie", "camarilla", "demark"]` | `classic` |  | Pivot-point family. ``camarilla`` is the only one that fills r4/s4. |
| `anchor` | `Literal["day", "week", "month"]` | `day` |  | Resample anchor for the pivot calculation. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no |  |
| `pivot` | `float \| None` | yes | Central pivot price. |
| `r1` | `float \| None` | yes |  |
| `r2` | `float \| None` | yes |  |
| `r3` | `float \| None` | yes |  |
| `r4` | `float \| None` | yes | Only populated for camarilla. |
| `s1` | `float \| None` | yes |  |
| `s2` | `float \| None` | yes |  |
| `s3` | `float \| None` | yes |  |
| `s4` | `float \| None` | yes | Only populated for camarilla. |

## Statistics

Distributional and time-series diagnostics.

### `autocorrelation`

_Query parameters for the autocorrelation endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `target` | `str` | `close` |  | Column to evaluate. |
| `use_returns` | `bool` | `True` |  | Difference and percent-change before computing. |
| `max_lag` | `int` | `40` | `gt=0` | Largest lag to compute. |
| `method` | `Literal["acf", "pacf", "both"]` | `both` |  | Which functions to compute. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `lag` | `int` | no |  |
| `acf` | `float \| None` | yes |  |
| `pacf` | `float \| None` | yes |  |
| `acf_confidence_lower` | `float \| None` | yes |  |
| `acf_confidence_upper` | `float \| None` | yes |  |
| `significant` | `bool` | no |  |

### `clenow`

_Query parameters for the Clenow Volatility-Adjusted Momentum endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `target` | `str` | `close` |  | Column to regress. |
| `period` | `int` | `90` | `gt=0` | Lookback window for the log-price regression. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no | Observation date. |
| `predicted` | `float \| None` | yes | Best-fit log-linear value at this date. |
| `r2` | `float` | no | R-squared of the regression fit on log prices. |
| `coefficient` | `float` | no | Annualised slope of the log-price regression. |
| `annualized_coefficient` | `float` | no | ``coefficient * r2`` - Clenow's momentum factor. |

### `drawdown`

_Query parameters for the drawdown endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `target` | `str` | `close` |  | Column to evaluate drawdowns on. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no | Observation date. |
| `cumulative_return` | `float \| None` | yes | Cumulative return from the first observation. |
| `running_peak` | `float \| None` | yes | Running maximum of ``cumulative_return``. |
| `drawdown` | `float \| None` | yes | Percentage drop from the running peak (negative or zero). |
| `drawdown_duration_days` | `int` | no | Consecutive observations since the most recent peak. |

### `hurst`

_Query parameters for the Hurst-exponent endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `target` | `str` | `close` |  | Column to evaluate. |
| `method` | `Literal["rs", "dfa"]` | `rs` |  | ``rs`` = Rescaled Range; ``dfa`` = Detrended Fluctuation. |
| `min_lag` | `int` | `2` | `gt=0` | Smallest window length. |
| `max_lag` | `int` | `100` | `gt=0` | Largest window length (exclusive). |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `hurst_exponent` | `float \| None` | yes |  |
| `interpretation` | `Literal['trending', 'mean_reverting', 'random_walk']` | no |  |
| `confidence` | `float \| None` | yes | R-squared of the log-log fit used to estimate the exponent. |

### `returns_stats`

_Query parameters for the ``returns_stats`` endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `target` | `str` | `close` |  | Column to evaluate returns on. |
| `frequency` | `Literal["daily", "weekly", "monthly", "quarterly", "annual"]` | `daily` |  | Annualisation frequency for Sharpe/Sortino/Calmar/risk-free. |
| `risk_free_rate` | `float` | `0.0` |  | Annualised risk-free rate used for Sharpe and Sortino. |
| `window` | `Annotated[int, Gt(gt=0)] \| None` | *required* |  | Rolling window. ``None`` returns a single summary row. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str \| None` | yes | Window end date, or ``None`` for the summary row. |
| `mean_return` | `float \| None` | yes |  |
| `std_return` | `float \| None` | yes |  |
| `skew` | `float \| None` | yes |  |
| `kurtosis` | `float \| None` | yes |  |
| `sharpe` | `float \| None` | yes |  |
| `sortino` | `float \| None` | yes |  |
| `calmar` | `float \| None` | yes |  |
| `max_drawdown` | `float \| None` | yes |  |
| `var_95` | `float \| None` | yes |  |
| `cvar_95` | `float \| None` | yes |  |

### `stationarity`

_Query parameters for the stationarity endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `target` | `str` | `close` |  | Column to test for stationarity. |
| `test` | `Literal["adf", "kpss", "both"]` | `both` |  | Which test(s) to run. |
| `regression` | `Literal["c", "ct", "ctt", "n"]` | `c` |  | Regression component: constant, trend, quadratic-trend, or none. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `adf_statistic` | `float \| None` | yes |  |
| `adf_pvalue` | `float \| None` | yes |  |
| `adf_critical_1pct` | `float \| None` | yes |  |
| `adf_critical_5pct` | `float \| None` | yes |  |
| `adf_critical_10pct` | `float \| None` | yes |  |
| `adf_verdict` | `Literal['stationary', 'non_stationary', 'skipped'] \| None` | yes |  |
| `kpss_statistic` | `float \| None` | yes |  |
| `kpss_pvalue` | `float \| None` | yes |  |
| `kpss_critical_1pct` | `float \| None` | yes |  |
| `kpss_critical_5pct` | `float \| None` | yes |  |
| `kpss_critical_10pct` | `float \| None` | yes |  |
| `kpss_verdict` | `Literal['stationary', 'non_stationary', 'skipped'] \| None` | yes |  |
| `overall_verdict` | `Literal['stationary', 'non_stationary', 'trend_stationary', 'inconclusive']` | no |  |

## Signals

Event detectors. Reachable under the `/signals/` URL prefix; in Python, via `obb.technical.signals.<name>`.

### `breakouts`

_Query parameters for the channel-breakouts endpoint._

**Required input columns**: `high`, `low`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `method` | `Literal["donchian", "bollinger"]` | `donchian` |  | Channel definition: Donchian (rolling high/low) or Bollinger (mean +/- ``band_std`` * stdev). |
| `length` | `int` | `20` | `gt=0` | Lookback window for the channel. |
| `band_std` | `Annotated[float, Gt(gt=0)] \| None` | *required* |  | Bollinger band multiplier. Ignored for ``donchian``. ``None`` resolves to 2.0 when ``method='bollinger'``. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `str` | no |  |
| `direction` | `str` | no |  |
| `price` | `str` | no |  |
| `band` | `str` | no |  |
| `magnitude` | `str` | no |  |
| `bars_in_range` | `str` | no |  |

### `candlestick_patterns`

_Query parameters for the candlestick-patterns endpoint._

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `patterns` | `list[str] \| None` | *required* |  | Subset of patterns to scan for. ``None`` runs every entry in ``SUPPORTED_PATTERNS``. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `str` | no |  |
| `pattern` | `str` | no |  |
| `direction` | `str` | no |  |
| `confidence` | `str` | no |  |

### `crossovers`

_Query parameters for the moving-average crossover endpoint._

**Required input columns**: `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `target` | `str` | `close` |  | Column on which to compute moving averages. |
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `fast_length` | `int` | `20` | `gt=0` | Lookback for the fast moving average. |
| `slow_length` | `int` | `50` | `gt=0` | Lookback for the slow moving average. |
| `mamode` | `Literal["sma", "ema", "wma", "hma", "zlma"]` | `sma` |  | Moving-average flavour. ``sma`` is the default; ``ema``, ``wma``, ``hma`` and ``zlma`` are also supported. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `str` | no |  |
| `direction` | `str` | no |  |
| `fast_value` | `str` | no |  |
| `slow_value` | `str` | no |  |
| `price` | `str` | no |  |
| `distance` | `str` | no |  |

### `divergences`

_Query parameters for the divergence-detection endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `indicator` | `Literal["rsi", "macd", "stoch", "cci"]` | *required* |  | Oscillator paired with price for divergence detection. |
| `indicator_length` | `int` | `14` | `gt=0` | Lookback length used inside the oscillator. |
| `target` | `str` | `close` |  | Price column used for swings. |
| `lookback` | `int` | `60` | `gt=0` | Number of recent bars in which to search for swing pairs. |
| `min_swing_distance` | `int` | `5` | `gt=0` | Minimum number of bars separating two swing points. Also doubles as the half-window for local-extreme detection. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `confirmation_date` | `str` | no |  |
| `prior_swing_date` | `str` | no |  |
| `kind` | `str` | no |  |
| `price_at_prior` | `str` | no |  |
| `price_at_confirmation` | `str` | no |  |
| `indicator_at_prior` | `str` | no |  |
| `indicator_at_confirmation` | `str` | no |  |
| `strength` | `str` | no |  |

### `oscillator_signals`

_Query parameters for the oscillator threshold-signals endpoint._

**Required input columns**: `low`, `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `target` | `str` | `close` |  | Price column used for oscillators that take a single series (rsi, cci). |
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `indicator` | `Literal["rsi", "mfi", "stoch", "williams_r", "cci"]` | *required* |  | Which oscillator to evaluate against its threshold bands. |
| `length` | `int` | `14` | `gt=0` | Lookback window for the oscillator. |
| `overbought_threshold` | `float \| None` | *required* |  | Upper band. ``None`` resolves to the indicator default (rsi 70, mfi 80, stoch 80, williams_r -20, cci 100). |
| `oversold_threshold` | `float \| None` | *required* |  | Lower band. ``None`` resolves to the indicator default (rsi 30, mfi 20, stoch 20, williams_r -80, cci -100). |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `str` | no |  |
| `value` | `str` | no |  |
| `regime` | `str` | no |  |
| `crossed_into_overbought` | `str` | no |  |
| `crossed_into_oversold` | `str` | no |  |
| `crossed_out_of_overbought` | `str` | no |  |
| `crossed_out_of_oversold` | `str` | no |  |

### `regime`

_Query parameters for the regime-classification endpoint._

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `adx_length` | `int` | `14` | `gt=0` | ADX lookback window. |
| `choppiness_length` | `int` | `14` | `gt=0` | Choppiness Index lookback window. |
| `adx_trend_threshold` | `float` | `25.0` | `gt=0` | ADX above this threshold marks a trending bar. Half this value is the cutoff for a weak trend. |
| `choppiness_range_threshold` | `float` | `61.8` | `gt=0` | Choppiness above this threshold marks a ranging bar. The default 61.8 is a common Fibonacci-derived cutoff. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no | Observation date. |
| `adx` | `float \| None` | yes | ADX reading at this bar. ``None`` during warm-up. |
| `choppiness` | `float \| None` | yes | Choppiness Index reading at this bar. ``None`` during warm-up. |
| `regime` | `Literal['strong_trend', 'weak_trend', 'ranging', 'transition']` | no | Classified regime for this bar. |
| `regime_changed` | `bool` | no | ``True`` when this bar's regime differs from the previous bar's. |

## Multi-Symbol and Utility

Cross-sectional, composition, and discovery endpoints.

### `correlation`

_Query parameters for the rolling pairwise correlation endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `target` | `str` | `close` |  | Column to compute correlation on. |
| `window` | `int` | `60` | `gt=0` | Rolling window length in bars. |
| `method` | `Literal["pearson", "spearman", "kendall"]` | `pearson` |  | Correlation method passed through to ``pandas.DataFrame.corr``. |
| `pairs` | `list[tuple[str, str]] \| None` | *required* |  | Optional explicit list of ``(symbol_a, symbol_b)`` pairs. Defaults to all unique pairs. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `datetime \| date \| str` | no | Observation date. |
| `symbol_a` | `str` | no | First symbol of the pair. |
| `symbol_b` | `str` | no | Second symbol of the pair. |
| `correlation` | `float \| None` | yes | Rolling correlation between ``symbol_a`` and ``symbol_b``. |

### `correlation_matrix`

_Query parameters for the snapshot correlation-matrix endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `target` | `str` | `close` |  | Column to correlate. |
| `window` | `Annotated[int, Gt(gt=0)] \| None` | *required* |  | If set, restrict correlation to the trailing ``window`` rows before ``as_of_date``. ``None`` uses every available row. |
| `method` | `Literal["pearson", "spearman", "kendall"]` | `pearson` |  |  |
| `as_of_date` | `datetime \| date \| str \| None` | *required* |  | Anchor date for the snapshot. ``None`` uses the last available row in the input. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `as_of_date` | `datetime \| date \| str` | no | Anchor date used for the snapshot. |
| `symbols` | `list[str]` | no | Symbols, in matrix order. |
| `matrix` | `list[list[float]]` | no | Correlation values. |

### `indicators`

_Query parameters for the catalogue endpoint._

**Required input columns**: `volume`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `category` | `Literal["overlay", "oscillator", "volatility", "volume", "trend", "signal", "structure", "stats", "multi", "all"]` | `all` |  | Filter to a single family, or ``all`` to return everything. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `indicators` | `str` | no |  |

### `multi`

_Query parameters for the multi-indicator composition endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `indicators` | `list[openbb_technical.multi.compose.MultiIndicatorRequest]` | *required* |  | Indicators to compute, in arbitrary order. |
| `target` | `str` | `close` |  | Target column forwarded to indicators that accept one. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | `str` | no |  |
| `values` | `str` | no |  |

### `relative_rotation`

_Relative Rotation Query Parameters._

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `benchmark` | `str` | *required* |  | The symbol to be used as the benchmark. |
| `study` | `Literal["price", "volume", "volatility"]` | `price` |  | The data point for the calculations. If 'price', the closing price will be used. If 'volatility', the standard deviation of the closing price will be used. If 'data' is supplied as a pivot table, the 'study' will assume the values are the closing price and 'volume' will be ignored. |
| `long_period` | `int \| None` | `252` |  | The length of the long period for momentum calculation, by default is 252. Adjust this value, to 365, when supplying assets such as crypto. |
| `short_period` | `int \| None` | `21` |  | The length of the short period for momentum calculation, by default is 21. Adjust this value, to 30, when supplying assets such as crypto. |
| `window` | `int \| None` | `21` |  | The length of window for the standard deviation calculation, by default is 21. Adjust this value, to 30, when supplying assets such as crypto. |
| `trading_periods` | `int \| None` | `252` |  | The number of trading periods per year, for the standard deviation calculation, by default is 252. Adjust this value, to 365, when supplying assets such as crypto. |
| `chart_params` | `dict[str, Any] \| None` | *required* |  | Additional parameters to pass when `chart=True` and the `openbb-charting` extension is installed. Parameters can be passed again to redraw the chart using the charting.to_chart() method of the response.              ChartParams             -----------             date: Optional[str]                 A target end date within the data, by default is the last date in the data.             show_tails: bool                 Show the tails on the chart, by default is True.             tail_periods: Optional[int]                 Number of periods to show in the tails, by default is 16.             tail_interval: Literal['day', 'week', 'month']                 Interval to show the tails, by default is 'week'.             title: Optional[str]                 Title of the chart. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `symbols` | `str` | no |  |
| `benchmark` | `str` | no |  |
| `study` | `str` | no |  |
| `rs_ratios` | `str` | no |  |
| `rs_momentum` | `str` | no |  |

### `screen`

_Query parameters for the multi-symbol screen endpoint._

**Required input columns**: `close`

**Parameters** (in addition to `data`):

| Name | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `index` | `str` | `date` |  | Index column name in ``data``. |
| `target` | `str` | `close` |  | Default target column. |
| `conditions` | `list[openbb_technical.multi.screen.ScreenCondition]` | *required* |  | Predicates to evaluate against each symbol's indicators. |
| `combine` | `Literal["and", "or"]` | `and` |  | ``and`` returns symbols matching every condition; ``or`` returns symbols matching at least one. |
| `as_of_date` | `datetime \| date \| str \| None` | *required* |  | Anchor date. Defaults to the latest date per symbol when unset. |

**Returns** — `OBBject` with `results` list of rows containing:

| Column | Type | Nullable | Description |
|---|---|---|---|
| `symbol` | `str` | no |  |
| `as_of_date` | `str` | no |  |
| `matched_conditions` | `str` | no |  |
| `values` | `str` | no |  |

