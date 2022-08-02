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
2022 Jun 01, 06:47 (🦋) /econometrics/ $ load fair

2022 Jun 01, 06:47 (🦋) /econometrics/ $ root fair.yrs_married

Unitroot from dataset 'fair of 'yrs_married'
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┓
┃                ┃ ADF      ┃ KPSS  ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━┩
│ Test Statistic │ -8.08    │ 7.01  │
├────────────────┼──────────┼───────┤
│ P-Value        │ 0.00     │ 0.01  │
├────────────────┼──────────┼───────┤
│ NLags          │ 34.00    │ 26.00 │
├────────────────┼──────────┼───────┤
│ Nobs           │ 6331.00  │ 0.00  │
├────────────────┼──────────┼───────┤
│ ICBest         │ 42958.72 │ 0.00  │
└────────────────┴──────────┴───────┘
```