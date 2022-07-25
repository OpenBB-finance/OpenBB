```
usage: load [-c COIN] [-d {1,7,14,30,90,180,365}] [--vs {usd,eur}] [-h]
```

Load crypto currency to perform analysis on CoinGecko is used as source for price and YahooFinance for volume.

```
optional arguments:
  -c COIN, --coin COIN  Coin to get. Must be coin symbol (e.g., btc, eth) (default: None)
  -d {1,7,14,30,90,180,365}, --days {1,7,14,30,90,180,365}
                        Data up to number of days ago (default: 365)
  --vs {usd,eur}        Quote currency (what to view coin vs) (default: usd)
  -h, --help            show this help message (default: False)
```
