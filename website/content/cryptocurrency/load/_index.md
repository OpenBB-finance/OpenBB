```
usage: load [-c COIN] [-s {cp,cg,bin,cb}] [-h]
```

Load crypto currency to perform analysis on. Available data sources are CoinGecko, CoinPaprika, Binance, CoinbaseBy default main source used for
analysis is CoinGecko (cg). To change it use --source flag

```
optional arguments:
  -c COIN, --coin COIN  Coin to get (default: None)
  -s {cp,cg,bin,cb}, --source {cp,cg,bin,cb}
                        Source of data (default: cg)
  -h, --help            show this help message (default: False)
```
