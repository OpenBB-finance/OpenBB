```
usage: tokens [--skip SKIP] [--limit LIMIT]
              [-s {index,symbol,name,tradeVolumeUSD,totalLiquidity,txCount}]
              [--descend] [--export {csv,json,xlsx}] [-h]
```
Display tokens trade-able on Uniswap DEX [Source: https://thegraph.com/en/]

```
optional arguments:
  --skip SKIP           Number of records to skip (default: 0)
  --limit LIMIT         Number of records to display (default: 20)
  -s {index,symbol,name,tradeVolumeUSD,totalLiquidity,txCount}, --sort {index,symbol,name,tradeVolumeUSD,totalLiquidity,txCount}
                        Sort by given column. Default: index (default: index)
  --descend             Flag to sort in descending order (lowest first)
                        (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default:
                        )
  -h, --help            show this help message (default: False)
```
