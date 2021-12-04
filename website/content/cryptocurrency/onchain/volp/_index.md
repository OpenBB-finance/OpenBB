```
usage: volp [-c COIN] [-t TOP] [-vs VS] [-d DAYS]
            [-s {date,exchange,base,quote,open,high,low,close,tradeAmountUSD,trades}]
            [--descend] [-h] [--export {csv,json,xlsx}]
```

Display daily volume for given crypto pair [Source: https://graphql.bitquery.io/]

```
optional arguments:
  -c COIN, --coin COIN  ERC20 token symbol or address. (default: ETH)
  -t TOP, --top TOP     top N number records (default: 10)
  -vs VS, --vs VS       Quote currency (default: USDT)
  -d DAYS, --days DAYS  Number of days to display data for. (default: 10)
  -s {date,exchange,base,quote,open,high,low,close,tradeAmountUSD,trades}, --sort {date,exchange,base,quote,open,high,low,close,tradeAmountUSD,trades}
                        Sort by given column. (default: date)
  --descend             Flag to sort in descending order (lowest first)
                        (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```
