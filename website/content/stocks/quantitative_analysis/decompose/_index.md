```
usage: decompose [-m] [-h] [--export {csv,json,xlsx}]
```

Decompose time series as: - Additive Time Series = Level + CyclicTrend + Residual + Seasonality - Multiplicative Time
Series = Level * CyclicTrend * Residual * Seasonality

```
optional arguments:
  -m, --multiplicative  decompose using multiplicative model instead of additive (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```
