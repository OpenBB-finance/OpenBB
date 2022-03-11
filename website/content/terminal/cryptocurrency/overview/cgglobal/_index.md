```
usage: cgglobal [--pie] [--export {csv,json,xlsx}] [-h]
```

Shows global statistics about Crypto Market

```
optional arguments:
  --pie               Show pie chart with market cap distribution of BTC, ETH, Altcoins
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:13 (✨) /crypto/ov/ $ cgglobal
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
