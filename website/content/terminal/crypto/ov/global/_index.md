```
usage: global [--pie] [-h] [--export EXPORT] [--source {CoinGecko,CoinPaprika}]
```

Shows global statistics about Crypto Market

```
optional arguments:
  --pie                 Flag to show pie chart with market cap distribution. Works only with CoinGecko source (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --source {CoinGecko,CoinPaprika}
                        Data source to select from (default: CoinGecko)
```

Example:
```
2022 Feb 15, 08:13 (✨) /crypto/ov/ $ global
                 Global Statistics
┌──────────────────────────────────────┬──────────┐
│ Metric                               │ Value    │
├──────────────────────────────────────┼──────────┤
│ Active Cryptocurrencies              │ 12589.00 │
├──────────────────────────────────────┼──────────┤
│ Upcoming Icos                        │ 0.00     │
├──────────────────────────────────────┼──────────┤
│ Ongoing Icos                         │ 49.00    │
├──────────────────────────────────────┼──────────┤
│ Ended Icos                           │ 3376.00  │
├──────────────────────────────────────┼──────────┤
│ Markets                              │ 741.00   │
├──────────────────────────────────────┼──────────┤
│ Market Cap Change Percentage 24H Usd │ 5.08     │
├──────────────────────────────────────┼──────────┤
│ Btc Market Cap In Pct                │ 40.46    │
├──────────────────────────────────────┼──────────┤
│ Eth Market Cap In Pct                │ 17.95    │
├──────────────────────────────────────┼──────────┤
│ Altcoin Market Cap In Pct            │ 41.59    │
└──────────────────────────────────────┴──────────┘
```
