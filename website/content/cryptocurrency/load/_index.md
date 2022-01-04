```
usage: load [-c COIN] [--source {cp,cg,bin,cb}] [-s  --start S_START_DATE] [-i --interval {1day,1hour,...}] [-d --days DAYS] [--vs {USD,BTC,...}] [-h]
```

Load crypto currency to perform analysis on. Available data sources are CoinGecko, CoinPaprika, Binance, Coinbase. By default main source used for
analysis is CoinGecko (cg). To change it use --source flag

TODO: improve loading docs

```
arguments:
  -c COIN, --coin COIN  Coin to get (default: None)
  -s {cp,cg,bin,cb}, --source {cp,cg,bin,cb}
                        Source of data (default: cg)
  --vs: The currency to look against. Default: `usd`
  -s/--start: The starting date (format YYYY-MM-DD) of the crypto (e.g.,: 2020-11-07)
  -i/--interval. Interval for candles. One of [1day,3day,1hour,2hour,4hour,6hour,8hour,12hour,1week,1min,3min,5min,15min,30min,1month].
  Defaults to 1day.
  -h, --help            show this help message (default: False)
```
