# Multi-Symbol Analysis

Five endpoints take a long-format multi-symbol price series (one DataFrame with a `symbol` column) and produce cross-sectional or relative-strength output.

Example input shape:

```python
import pandas as pd

df = pd.read_csv("dow30.csv")          # columns: date, symbol, open, high, low, close, volume
print(df.head())
#         date open    high    low    close   volume    symbol
# 0 2024-01-02 187.15  188.44  183.89 185.64  82488700  AAPL
# 1 2024-01-02 376.04  376.04  370.66 370.87  25258600  MSFT
# ...

data = df.to_dict(orient="records")
```

## Correlation (paired)

Returns the rolling Pearson, Spearman, or Kendall correlation of returns for specific symbol pairs.

```python
result = obb.technical.correlation(
    data=data,
    pairs=[("AAPL", "MSFT"), ("AAPL", "NVDA"), ("NVDA", "MSFT")],
    window=60,
    method="pearson",
).to_df()
```

Output is a long-format frame with one row per `(symbol_a, symbol_b, date)` tuple. With `window=None`, returns the single full-sample correlation per pair.

## Correlation Matrix (snapshot)

Builds a single point-in-time correlation matrix across every symbol in the input.

```python
result = obb.technical.correlation_matrix(
    data=data,
    window=60,                       # rolling window ending at as_of_date
    method="spearman",
    as_of_date="2024-06-28",         # None = most recent date in input
).results[0]
print(result.symbols)                # ['AAPL', 'AMZN', 'MSFT', ...]
print(result.matrix)                 # nested list, indexed by symbols order
```

## Screen

Filters a universe by indicator-driven predicates. Each condition specifies an indicator endpoint, the column to read, an operator, and a threshold.

```python
matches = obb.technical.screen(
    data=data,
    conditions=[
        {
            "indicator": "rsi",
            "column": "close_RSI_14",
            "operator": "lt",
            "value": 30.0,
        },
        {
            "indicator": "sma",
            "column": "close_SMA_50",
            "operator": "gt",
            "value": 0.0,
        },
    ],
    combine="and",                   # "or" for union semantics
    as_of_date="2024-06-28",         # None = each symbol's latest bar
).results
```

Supported operators:

| Operator | `value` shape | Fires when |
|---|---|---|
| `gt`, `gte`, `lt`, `lte`, `eq` | scalar | latest value matches |
| `between` | `(low, high)` | `low <= latest <= high` |
| `crossed_above`, `crossed_below` | `(threshold, lookback)` | series crosses the threshold within the trailing `lookback` bars |
| `made_high`, `made_low` | `(0, lookback)` | latest is the max/min over the trailing `lookback` bars |

Each matched row carries the symbol, the as-of date used, how many conditions fired, and the indicator values at the trigger.

## Relative Rotation Graph

Computes the JdK RS-Ratio (relative-strength level) and RS-Momentum (relative-strength rate of change) for every constituent against a benchmark. Used to locate symbols in one of four rotational quadrants.

```python
# The benchmark symbol must be present in `data`. The canonical RRG setup is
# the benchmark (e.g. an index ETF) plus the constituents you want to rotate
# against it. If you load Dow 30 OHLCV, append SPY rows to `data` before this
# call, or pick one of the constituents as the benchmark.
rrg = obb.technical.relative_rotation(
    data=data,
    benchmark="AAPL",                # any symbol present in `data`
    study="price",                   # or "volume", "volatility"
    long_period=252,                 # RS-Ratio standardisation window
    short_period=21,                 # RS-Momentum standardisation window
    window=21,                       # trail length retained in the output
    trading_periods=252,             # used by the volatility study
)

rrg.results.rs_ratios               # one frame per symbol, indexed by date
rrg.results.rs_momentum             # same shape
rrg.results.benchmark               # echoed for charting
```

Quadrant interpretation (`x = RS-Ratio`, `y = RS-Momentum`, both centred at 100):

| RS-Ratio | RS-Momentum | Quadrant | Interpretation |
|---|---|---|---|
| > 100 | > 100 | Leading | Outperforming and accelerating |
| > 100 | < 100 | Weakening | Still outperforming but momentum is fading |
| < 100 | < 100 | Lagging | Underperforming with negative momentum |
| < 100 | > 100 | Improving | Underperforming but momentum is turning up |

Symbols rotate clockwise through the quadrants over time. The `window=21` trail draws the rotation arc on a chart.

## Input format constraints

- **`symbol` column required.** All multi-symbol endpoints group by it.
- **Long format only.** Each row is one (symbol, date) observation. Don't pre-pivot.
- **Daily data is the default assumption for `relative_rotation`.** It requires at least `long_period + window` bars per symbol (default ~273 daily bars). The volatility study needs roughly twice as much.
- **Identical date grids preferred.** Symbols whose date series don't fully overlap will be intersected pairwise; the correlation/RRG endpoints work on the intersection.
