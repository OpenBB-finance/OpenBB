```
usage: pairs [-l N]
             [-s {volumeUSD,token0.name,token0.symbol,token1.name,token1.symbol,volumeUSD,txCount}]
             [--descend] [--export {csv,json,xlsx}] [-h]
```

Display uniswap pools by volume. [Source: https://thegraph.com/en/]

```
optional arguments:
  -l N, --limit N       display N records (default: 10)
  -s {volumeUSD,token0.name,token0.symbol,token1.name,token1.symbol,volumeUSD,txCount}, --sort {volumeUSD,token0.name,token0.symbol,token1.name,token1.symbol,volumeUSD,txCount}
                        Sort by given column. Default: volumeUSD (default:
                        volumeUSD)
  --descend             Flag to sort in descending order (lowest first)
                        (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default:
                        )
  -h, --help            show this help message (default: False)
```
