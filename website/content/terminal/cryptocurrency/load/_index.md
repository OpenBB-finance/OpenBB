```
usage: load [-c COIN] [--source {cp,cg,bin,cb}] [-s START] [--vs VS] [-i INTERVAL] [-h]
```

Load crypto currency to perform analysis on. Available data sources are CoinGecko, CoinPaprika, Binance, Coinbase. By default main source used for analysis is CoinGecko (cg). To change it use --source flag.

```
optional arguments:
  -c COIN, --coin COIN  Coin to get (default: None)
  --source {cp,cg,bin,cb}
                        Source of data (default: cg)
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the crypto (default: 2021-02-14)
  --vs VS               Quote currency (what to view coin vs) (default: usd)
  -i INTERVAL, --interval INTERVAL
                        Interval to get data (Only available on binance/coinbase) (default: 1day)
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

An example:
```
2022 Feb 15, 05:51 (✨) /crypto/ $ load BTC

Loaded bitcoin against usd from CoinGecko source

Current Price: 44225.18 USD
Performance in interval (1day): 4.68%
Performance since 2021-02-14: -9.02%
```
