```
usage: trades [--vs {EUR,USDC,GBP,USD,USDT,UST}] [--side {all,buy,sell}] [-t TOP] [--export {csv,json,xlsx}] [-h]
```

Show last trades on Coinbase

```
optional arguments:
  --vs {EUR,USDC,GBP,USD,USDT,UST}
                        Quote currency (what to view coin vs) (default: USDT)
  --side {all,buy,sell}
                        Side of trade: buy, sell, all (default: all)
  -t TOP, --top TOP     Limit of records (default: 15)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
