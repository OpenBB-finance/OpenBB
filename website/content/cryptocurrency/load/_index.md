```
usage: load [-c COIN] [--source {cp,cg,bin,cb}] [-s  --start S_START_DATE] [-i --interval {1day,1hour,...}] [--vs {USD,BTC,...}] [-h]
```

Load crypto currency to perform analysis on. Available data sources are CoinGecko, CoinPaprika, Binance, Coinbase. By default main source used for analysis is CoinGecko (cg). To change it use --source flag.

```
arguments:
  -c COIN, --coin COIN  Coin to get (default: None)
  -s {cp,cg,bin,cb}, --source {cp,cg,bin,cb}
                        Source of data (default: cg)
  -s/--start: The starting date (format YYYY-MM-DD) of the crypto (e.g.,: 2020-11-07)
  -h, --help            show this help message (default: False)
```

All the sources share the arguments specified above but `--interval` and `--vs` differ from source to source.

For CoinPaprika and CoinGecko are similar:

```
  --vs VS              The currency to look the loaded coin against. Both USD and BTC are supported. Default: `USD`
  -i/--interval        Interval to look data for. These two sources only support daily data. Default: `1day`
```

For Coinbase:

```
  --vs VS              The currency to look the loaded coin against. Depends on the crypto loaded. Default: `USDT`
  -i/--interval        Interval to look data for. Default is `1day` but support all of the following: ['1min', '5min', '15min', '1hour', '6hour', '24hour', '1day']
```

For Binance:

```
  --vs VS             The currency to look the loaded coin against. Depends on the crypto loaded. Default: `USDT`
  -i/--interval       Interval to look data for. Default is `1day` but support all of the following: ['1day', '3day', '1hour', '2hour', '4hour', '6hour', '8hour', '12hour', '1week', '1min', '3min', '5min', '15min', '30min', '1month']
```
