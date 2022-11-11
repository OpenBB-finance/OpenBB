```
usage: tv [-c COIN] [-vs {ETH,USD,BTC,USDT}] [-l N]
          [-s {exchange,tradeAmount,trades}] [--reverse] [-h]
          [--export {csv,json,xlsx}]
```

Display daily volume for given crypto pair [Source: https://graphql.bitquery.io/]

```
optional arguments:
  -c COIN, --coin COIN  ERC20 token symbol or address. (default: None)
  -vs {ETH,USD,BTC,USDT}, --vs {ETH,USD,BTC,USDT}
                        Currency of displayed trade amount. (default: USD)
  -l N, --limit N     display N number records (default: 10)
  -s {exchange,tradeAmount,trades}, --sort {exchange,tradeAmount,trades}
                        Sort by given column. (default: trades)
  -r, --reverse         Data is sorted in descending order by default.
                        Reverse flag will sort it in an ascending way.
                        Only works when raw data is displayed. (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```
