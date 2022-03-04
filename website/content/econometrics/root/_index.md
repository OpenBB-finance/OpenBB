```
usage: root [-c {OPTIONS}] [-r {c,ct,ctt,nc}] [-k {c,ct}] [-h] [--export {csv,json,xlsx}]
```

Show unit root tests of a column of a dataset.

In probability theory and statistics, a unit root is a feature of some stochastic processes (such as random walks) that can cause problems in statistical inference involving time series models. A linear stochastic process has a unit root if 1 is a root of the process's characteristic equation. Such a process is non-stationary but does not always have a trend. [Source: Wikipedia]

```
optional arguments:
  -c {OPTIONS}, --column {OPTIONS}
                        The column and name of the database you want test unit root for (default: None)
  -r {c,ct,ctt,nc}, --fuller_reg {c,ct,ctt,nc}
                        Type of regression. Can be ‘c’,’ct’,’ctt’,’nc’. c - Constant and t - trend order (default: c)
  -k {c,ct}, --kps_reg {c,ct}
                        Type of regression. Can be ‘c’,’ct'. c - Constant and t - trend order (default: c)
  -h, --help            show this help message (default: False)
   --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 24, 05:37 (✨) /econometrics/ $ root return-msft
Unitroot Test [Column: return | Dataset: msft]
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━┓
┃                ┃ ADF      ┃ KPSS ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━┩
│ Test Statistic │ -22.31   │ 0.09 │
├────────────────┼──────────┼──────┤
│ P-Value        │ 0.00     │ 0.10 │
├────────────────┼──────────┼──────┤
│ NLags          │ 1.00     │ 5    │
├────────────────┼──────────┼──────┤
│ Nobs           │ 757.00   │      │
├────────────────┼──────────┼──────┤
│ ICBest         │ -3902.73 │      │
└────────────────┴──────────┴──────┘

2022 Feb 24, 05:38 (✨) /econometrics/ $ root adj_close-aapl
Unitroot Test [Column: adj_close | Dataset: aapl]
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━┓
┃                ┃ ADF     ┃ KPSS ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━┩
│ Test Statistic │ -0.46   │ 4.20 │
├────────────────┼─────────┼──────┤
│ P-Value        │ 0.90    │ 0.01 │
├────────────────┼─────────┼──────┤
│ NLags          │ 1.00    │ 17   │
├────────────────┼─────────┼──────┤
│ Nobs           │ 757.00  │      │
├────────────────┼─────────┼──────┤
│ ICBest         │ 3214.33 │      │
└────────────────┴─────────┴──────┘
```