```
usage: cpglobal [--export {csv,json,xlsx}] [-h]
```

Show most important global crypto statistics like: Market Cap, Volume, Number of cryptocurrencies, All Time High, All Time Low

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:18 (✨) /crypto/ov/ $ cpglobal
Parser must be a string or character stream, not datetime
               Global Crypto Statistics
┌──────────────────────────────┬─────────────────────┐
│ Metric                       │ Value               │
├──────────────────────────────┼─────────────────────┤
│ market_cap_usd               │ 2.048 T             │
├──────────────────────────────┼─────────────────────┤
│ volume_24h_usd               │ 1.086 T             │
├──────────────────────────────┼─────────────────────┤
│ bitcoin_dominance_percentage │ 41.010              │
├──────────────────────────────┼─────────────────────┤
│ cryptocurrencies_number      │ 10.114 K            │
├──────────────────────────────┼─────────────────────┤
│ market_cap_ath_value         │ 3.629 T             │
├──────────────────────────────┼─────────────────────┤
│ market_cap_ath_date          │ 2021-10-27 07:40:00 │
├──────────────────────────────┼─────────────────────┤
│ volume_24h_ath_value         │ 1.388 T             │
├──────────────────────────────┼─────────────────────┤
│ volume_24h_ath_date          │ 2021-05-02 17:00:00 │
├──────────────────────────────┼─────────────────────┤
│ volume_24h_percent_from_ath  │ -21.790             │
├──────────────────────────────┼─────────────────────┤
│ volume_24h_percent_to_ath    │ 27.860              │
├──────────────────────────────┼─────────────────────┤
│ market_cap_change_24h        │ 4.480               │
├──────────────────────────────┼─────────────────────┤
│ volume_24h_change_24h        │ 2.050               │
├──────────────────────────────┼─────────────────────┤
│ last_updated                 │ 2022-02-15 14:18:22 │
└──────────────────────────────┴─────────────────────┘
```
