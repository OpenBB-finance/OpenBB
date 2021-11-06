```
usage: pos [-n NUM] [-s {sv,sv_pct,nsv,nsv_dollar,dpp,dpp_dollar}] [-a] [--export {csv,json,xlsx}] [-h]
```

Request a list of up to 200 (either positive or negative using the -a argument) Dark Pool Positions using the optional arguments to the feature command as described below. Source: https://www.stockgrid.io/darkpools

Volume and short sale data for tickers trading on US-regulated public markets is updated daily on the [FINRA website](https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data/daily-short-sale-volume-files) at approximately 6PM EST. 

A 'position' is the result of the net aggregagte short sale volume over a rolling twenty day period. The available daily data sets currently go back as far as 2020. For an explanation on reading this data, consult the white paper from SqueezeMetrics linked below. 

https://squeezemetrics.com/monitor/download/pdf/short_is_long.pdf?

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
<img width="1400" alt="Feature Screenshot - pos positive" src="https://user-images.githubusercontent.com/85772166/140590292-159e8aaa-5e01-4ccb-90af-d4e358d6805b.png">
<img width="1400" alt="Feature Screenshot - pos negative" src="https://user-images.githubusercontent.com/85772166/140590303-03f7f8f3-196b-4665-811b-62d908331bee.png">
