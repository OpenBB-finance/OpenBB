```
usage: pos [-n NUM] [-s {sv,sv_pct,nsv,nsv_dollar,dpp,dpp_dollar}] [-a] [--export {csv,json,xlsx}] [-h]
```

Request a list of up to 200 (either positive or negative using the -a argument) Dark Pool Positions using the optional arguments to the feature command as described below. Source: https://www.stockgrid.io/darkpools

Volume and short sale data for tickers trading on US-regulated public markets is updated daily on the [FINRA website](https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data/daily-short-sale-volume-files) at approximately 6PM EST. 

A 'position' is the result of the net aggregagte short sale volume over a rolling twenty day period. The available daily data sets currently go back as far as 2020. For an explanation on reading this data, consult the white paper from SqueezeMetrics: https://squeezemetrics.com/monitor/download/pdf/short_is_long.pdf?

```
optional arguments:
  -n NUM, --number NUM  Number of top tickers to show (default: 10)
  -s {sv,sv_pct,nsv,nsv_dollar,dpp,dpp_dollar}, --sort {sv,sv_pct,nsv,nsv_dollar,dpp,dpp_dollar}
                        Field for which to sort by, where 'sv': Short Vol. (1M), 'sv_pct': Short Vol. %, 'nsv': Net Short Vol. (1M), 'nsv_dollar': Net Short
                        Vol. ($100M), 'dpp': DP Position (1M), 'dpp_dollar': DP Position ($1B) (default: dpp_dollar)
  -a, --ascending       Data in ascending order (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:51 (✨) /stocks/dps/ $ pos
                                                      Data for: 2022-02-14
┌────────┬─────────────────┬──────────────┬─────────────────────┬────────────────────────┬──────────────────┬───────────────────┐
│ Ticker │ Short Vol. (1M) │ Short Vol. % │ Net Short Vol. (1M) │ Net Short Vol. ($100M) │ DP Position (1M) │ DP Position ($1B) │
├────────┼─────────────────┼──────────────┼─────────────────────┼────────────────────────┼──────────────────┼───────────────────┤
│ QQQ    │ 12.80           │ 66.45        │ 6.34                │ 22.02                  │ 117.89           │ 42.14             │
├────────┼─────────────────┼──────────────┼─────────────────────┼────────────────────────┼──────────────────┼───────────────────┤
│ AMD    │ 45.65           │ 66.50        │ 22.65               │ 25.88                  │ 171.23           │ 21.13             │
├────────┼─────────────────┼──────────────┼─────────────────────┼────────────────────────┼──────────────────┼───────────────────┤
│ SPY    │ 12.74           │ 53.08        │ 1.48                │ 6.49                   │ 42.46            │ 19.11             │
├────────┼─────────────────┼──────────────┼─────────────────────┼────────────────────────┼──────────────────┼───────────────────┤
│ NVDA   │ 12.36           │ 55.73        │ 2.54                │ 6.17                   │ 73.21            │ 18.07             │
├────────┼─────────────────┼──────────────┼─────────────────────┼────────────────────────┼──────────────────┼───────────────────┤
│ IWM    │ 3.33            │ 72.64        │ 2.07                │ 4.16                   │ 33.92            │ 6.74              │
├────────┼─────────────────┼──────────────┼─────────────────────┼────────────────────────┼──────────────────┼───────────────────┤
│ LQD    │ 8.18            │ 83.55        │ 6.57                │ 8.13                   │ 52.24            │ 6.62              │
├────────┼─────────────────┼──────────────┼─────────────────────┼────────────────────────┼──────────────────┼───────────────────┤
│ HYG    │ 8.20            │ 70.11        │ 4.70                │ 3.88                   │ 59.81            │ 5.04              │
├────────┼─────────────────┼──────────────┼─────────────────────┼────────────────────────┼──────────────────┼───────────────────┤
│ NFLX   │ 1.28            │ 47.61        │ -0.13               │ -0.51                  │ 11.19            │ 4.76              │
├────────┼─────────────────┼──────────────┼─────────────────────┼────────────────────────┼──────────────────┼───────────────────┤
│ SNAP   │ 13.34           │ 61.82        │ 5.10                │ 2.02                   │ 105.93           │ 4.34              │
├────────┼─────────────────┼──────────────┼─────────────────────┼────────────────────────┼──────────────────┼───────────────────┤
│ SMH    │ 1.04            │ 62.44        │ 0.41                │ 1.10                   │ 13.29            │ 3.67              │
└────────┴─────────────────┴──────────────┴─────────────────────┴────────────────────────┴──────────────────┴───────────────────┘
```
