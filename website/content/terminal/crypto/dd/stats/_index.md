```
usage: stats [--vs {UST,EUR,USDC,USDT,GBP,USD}] [--export {csv,json,xlsx}] [-h]
```

Display coin stats

```
optional arguments:
  --vs {UST,EUR,USDC,USDT,GBP,USD}
                        Quote currency (what to view coin vs) (default: USDT)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 07:47 (✨) /crypto/dd/ $ stats

       24 hr Product Stats
┌──────────────┬────────────────┐
│ Metric       │ Value          │
├──────────────┼────────────────┤
│ open         │ 42551.99       │
├──────────────┼────────────────┤
│ high         │ 44428.47       │
├──────────────┼────────────────┤
│ low          │ 41800          │
├──────────────┼────────────────┤
│ volume       │ 743.03129474   │
├──────────────┼────────────────┤
│ last         │ 44183.84       │
├──────────────┼────────────────┤
│ volume_30day │ 22665.06104665 │
└──────────────┴────────────────┘
```
