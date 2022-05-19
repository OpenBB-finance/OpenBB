```
usage: metric [-m {volatility,sharpe,sortino,maxdrawdown,rsquare,skew,kurtosis}] [-r RISK_FREE_RATE] [-h] [--export EXPORT]
```

Display metric of choice for different periods

```
optional arguments:
  -m {volatility,sharpe,sortino,maxdrawdown,rsquare,skew,kurtosis}, --metric {volatility,sharpe,sortino,maxdrawdown,rsquare,skew,kurtosis}
                        Period to apply rolling window (default: False)
  -r RISK_FREE_RATE, --rfr RISK_FREE_RATE
                        Set risk free rate for calculations. (default: 0.0)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
```

E.g. `metric sharpe`
```
Sharpe ratio for Portfolio and Benchmark
┏━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┓
┃     ┃ Portfolio ┃ Benchmark ┃
┡━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━┩
│ mtd │ -0.057    │ -0.027    │
├─────┼───────────┼───────────┤
│ qtd │ -0.220    │ -0.172    │
├─────┼───────────┼───────────┤
│ ytd │ -0.123    │ -0.098    │
├─────┼───────────┼───────────┤
│ 3m  │ -0.103    │ -0.052    │
├─────┼───────────┼───────────┤
│ 6m  │ -0.127    │ -0.070    │
├─────┼───────────┼───────────┤
│ 1y  │ -0.038    │ 0.007     │
├─────┼───────────┼───────────┤
│ 3y  │ 0.018     │ 0.044     │
├─────┼───────────┼───────────┤
│ 5y  │ 0.025     │ 0.046     │
├─────┼───────────┼───────────┤
│ 10y │ 0.026     │ 0.056     │
├─────┼───────────┼───────────┤
│ all │ 0.024     │ 0.050     │
└─────┴───────────┴───────────┘
```
