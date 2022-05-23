```
usage: summary [-p {mtd,qtd,ytd,3m,6m,1y,3y,5y,10y,all}] [-r RISK_FREE_RATE] [-h] [--export EXPORT]
```

Display summary of portfolio vs benchmark

```
optional arguments:
  -p {mtd,qtd,ytd,3m,6m,1y,3y,5y,10y,all}, --period {mtd,qtd,ytd,3m,6m,1y,3y,5y,10y,all}
                        The file to be loaded (default: all)
  -r RISK_FREE_RATE, --rfr RISK_FREE_RATE
                        Set risk free rate for calculations. (default: 0.0)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
```

```
Summary of Portfolio vs Benchmark for all period
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┓
┃                   ┃ Portfolio ┃ Benchmark ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Volatility        │ 0.01      │ 0.01      │
├───────────────────┼───────────┼───────────┤
│ Skew              │ -0.40     │ -0.58     │
├───────────────────┼───────────┼───────────┤
│ Kurtosis          │ 16.45     │ 12.31     │
├───────────────────┼───────────┼───────────┤
│ Maximum Drawdowwn │ -0.34     │ -0.34     │
├───────────────────┼───────────┼───────────┤
│ Sharpe ratio      │ 0.02      │ 0.05      │
├───────────────────┼───────────┼───────────┤
│ Sortino ratio     │ 0.03      │ 0.06      │
├───────────────────┼───────────┼───────────┤
│ R2 Score          │ -0.81     │ -0.81     │
└───────────────────┴───────────┴───────────┘
```
