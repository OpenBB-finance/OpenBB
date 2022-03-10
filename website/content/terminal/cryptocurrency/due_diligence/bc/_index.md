```
usage: bc [--export {csv,json,xlsx}] [-h]
```

Blockchain explorers URLs for loaded coin. Those are sites like etherescan.io or polkascan.io in which you can see all blockchain data e.g. all txs,
all tokens, all contracts...

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 07:10 (✨) /crypto/dd/ $ bc
              Blockchain URLs
┌────────┬─────────────────────────────────┐
│ Metric │ Value                           │
├────────┼─────────────────────────────────┤
│ 0      │ https://blockchair.com/bitcoin/ │
├────────┼─────────────────────────────────┤
│ 1      │ https://btc.com/                │
├────────┼─────────────────────────────────┤
│ 2      │ https://btc.tokenview.com/      │
└────────┴─────────────────────────────────┘
```
