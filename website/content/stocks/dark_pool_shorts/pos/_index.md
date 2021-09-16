```
usage: pos [-n NUM] [-s {sv,sv_pct,nsv,nsv_dollar,dpp,dpp_dollar}] [-a] [--export {csv,json,xlsx}] [-h]
```

Get dark pool short positions. [Source: Stockgrid]

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
