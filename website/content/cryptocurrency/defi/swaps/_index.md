```
usage: pairs [-t TOP] [-s {timestamp,token0,token1,amountUSD}] [--descend]
             [--export {csv,json,xlsx}] [-h]
```
Display last swaps done on Uniswap DEX. [Source: https://thegraph.com/en/]

```
optional arguments:
  -t TOP, --top TOP     Number of records (default: 10)
  -s {timestamp,token0,token1,amountUSD}, --sort {timestamp,token0,token1,amountUSD}
                        Sort by given column. Default: timestamp (default:
                        timestamp)
  --descend             Flag to sort in descending order (lowest first)
                        (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default:
                        )
  -h, --help            show this help message (default: False)
```
