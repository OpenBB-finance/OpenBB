```
usage: coint [-ts {OPTIONS}] [-p] [-s SIGNIFICANT] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Show co-integration between timeseries.

Cointegration is a statistical property of a collection (X1, X2, ..., Xk) of time series variables. First, all of the series must be integrated of order d (see Order of integration). Next, if a linear combination of this collection is integrated of order less than d, then the collection is said to be co-integrated. Formally, if (X,Y,Z) are each integrated of order d, and there exist coefficients a,b,c such that aX + bY + cZ is integrated of order less than d, then X, Y, and Z are cointegrated. Cointegration has become an important property in contemporary time series analysis. Time series often have trends—either deterministic or stochastic. In an influential paper, Charles Nelson and Charles Plosser (1982) provided statistical evidence that many US macroeconomic time series (like GNP, wages, employment, etc.) have stochastic trends. [Source: Wikipedia]

```
optional arguments:
  -ts {OPTIONS}, --timeseries {OPTIONS}
                        The time series you wish to test co-integration on. Can hold multiple timeseries. (default: None)
  -p, --plot            Plot Z-Values (default: False)
  -s SIGNIFICANT, --significant SIGNIFICANT
                        Show only companies that have p-values lower than this percentage (default: 0)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

Example:

```
2022 Feb 24, 06:03 (🦋) /econometrics/ $ coint msft.adj_close,aapl.adj_close,tsla.adj_close,googl.adj_close -p
                                  Cointegration Tests
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Pairs                          ┃ Constant ┃ Gamma ┃ Alpha ┃ Dickey-Fuller ┃ P Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ adj_close-msft/adj_close-aapl  │ 46.62    │ 1.58  │ 0.00  │ -1.86         │ 0.35    │
├────────────────────────────────┼──────────┼───────┼───────┼───────────────┼─────────┤
│ adj_close-msft/adj_close-tsla  │ 130.28   │ 0.18  │ -0.01 │ -2.82         │ 0.06    │
├────────────────────────────────┼──────────┼───────┼───────┼───────────────┼─────────┤
│ adj_close-msft/adj_close-googl │ 21.38    │ 0.10  │ -0.01 │ -2.51         │ 0.11    │
├────────────────────────────────┼──────────┼───────┼───────┼───────────────┼─────────┤
│ adj_close-aapl/adj_close-tsla  │ 53.92    │ 0.11  │ -0.01 │ -2.94         │ 0.04    │
├────────────────────────────────┼──────────┼───────┼───────┼───────────────┼─────────┤
│ adj_close-aapl/adj_close-googl │ -7.83    │ 0.06  │ -0.00 │ -1.62         │ 0.47    │
├────────────────────────────────┼──────────┼───────┼───────┼───────────────┼─────────┤
│ adj_close-tsla/adj_close-googl │ -505.14  │ 0.51  │ -0.01 │ -2.28         │ 0.18    │
└────────────────────────────────┴──────────┴───────┴───────┴───────────────┴─────────┘
```

![error_terms_cointegrations](https://user-images.githubusercontent.com/46355364/155514964-dd75cf17-91ae-4326-96e8-45d9a2c7b24a.png)
