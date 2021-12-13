```
usage: pairs [-l N] [-v VOL] [-tx TX] [--days DAYS]
             [-s {created,pair,token0,token1,volumeUSD,txCount,totalSupply}]
             [--descend] [--export {csv,json,xlsx}] [-h]
```

Display Lastly added pairs on Uniswap DEX. [Source: https://thegraph.com/en/]

```
optional arguments:
  -l N, --limit N       display N records (default: 10)
  -v VOL, --vol VOL     Minimum trading volume (default: 100)
  -tx TX, --tx TX       Minimum number of transactions (default: 100)
  --days DAYS           Number of days the pair has been active, (default: 10)
  -s {created,pair,token0,token1,volumeUSD,txCount,totalSupply}, --sort {created,pair,token0,token1,volumeUSD,txCount,totalSupply}
                        Sort by given column. Default: created (default:
                        created)
  --descend             Flag to sort in descending order (lowest first)
                        (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default:
                        )
  -h, --help            show this help message (default: False)
```
