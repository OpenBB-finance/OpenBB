```text
usage: unitroot [-r {c,ct,ctt,nc}] [-k {c,ct}] [--export {csv,json,xlsx}] [-h]
```

Unit root test / stationarity (ADF, KPSS)

In statistics, a unit root test tests whether a time series variable is non-stationary and possesses a unit root. The null hypothesis is generally defined as the presence of a unit root and the alternative hypothesis is either stationarity, trend stationarity or explosive root depending on the test used. 

See the Wiki page on this subject for more information: https://en.wikipedia.org/wiki/Unit_root_test

```
optional arguments:
  -r {c,ct,ctt,nc}, --fuller_reg {c,ct,ctt,nc}
                        Type of regression. Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order (default: c)
  -k {c,ct}, --kps_reg {c,ct}
                        Type of regression. Can be ‘c’,’ct' (default: c)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 16, 11:16 (✨) /stocks/qa/ $ unitroot
         Unit Root Calculation
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┓
┃                ┃ ADF        ┃ KPSS   ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━┩
│ Test Statistic │ -28.9536   │ 0.2928 │
├────────────────┼────────────┼────────┤
│ P-Value        │ 0.0000     │ 0.1000 │
├────────────────┼────────────┼────────┤
│ NLags          │ 0.0000     │ 3      │
├────────────────┼────────────┼────────┤
│ Nobs           │ 759.0000   │        │
├────────────────┼────────────┼────────┤
│ ICBest         │ -3339.2013 │        │
└────────────────┴────────────┴────────┘
```
