```
usage: lt [-k {dex,time}] [-vs {ETH,USD,BTC,USDT}] [-l N] [-d DAYS]
          [-s {trades,tradeAmount,exchange}] [--reverse] [-h]
          [--export {csv,json,xlsx}]
```

Display Trades on Decentralized Exchanges aggregated by DEX or Month [Source: https://graphql.bitquery.io/]

```
optional arguments:
  -k {dex,time}, --kind {dex,time}
                        Aggregate trades by dex or time Default: dex (default:
                        dex)
  -vs {ETH,USD,BTC,USDT}, --vs {ETH,USD,BTC,USDT}
                        Currency of displayed trade amount. (default: USD)
  -l N, --limit N     display N number records (default: 10)
  -d DAYS, --days DAYS  Number of days to display data for. (default: 90)
  -s {trades,tradeAmount,exchange}, --sort {trades,tradeAmount,exchange}
                        Sort by given column. Default: tradeAmount. For
                        monthly trades date. (default: tradeAmount)
  -r, --reverse         Data is sorted in descending order by default.
                        Reverse flag will sort it in an ascending way.
                        Only works when raw data is displayed. (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```
