```
usage: ath [--export {csv,json,xlsx}] [--vs {usd,btc}] [-h]
```

All time high data for loaded coin

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  --vs {usd,btc}        currency (default: usd)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 07:04 (✨) /crypto/dd/ $ ath
                            Coin Highs
┌─────────────────────────────────────┬──────────────────────────┐
│ Metric                              │ Value                    │
├─────────────────────────────────────┼──────────────────────────┤
│ Current Price USD                   │ 44302                    │
├─────────────────────────────────────┼──────────────────────────┤
│ All Time High USD                   │ 69045                    │
├─────────────────────────────────────┼──────────────────────────┤
│ All Time High Date USD              │ 2021-11-10T14:24:11.849Z │
├─────────────────────────────────────┼──────────────────────────┤
│ All Time High Change Percentage USD │ -35.75                   │
└─────────────────────────────────────┴──────────────────────────┘
```
