```
usage: top [-l N]
           [-s {rank,name,symbol,price,txsCount,transfersCount,holdersCount,address}]
           [--descend] [--export {csv,json,xlsx}] [-h]
```

Display top ERC20 tokens. [Source: Ethplorer]

```
optional arguments:
  -l N, --limit N     display N number records (default: 10)
  -s {rank,name,symbol,price,txsCount,transfersCount,holdersCount,address}, --sort {rank,name,symbol,price,txsCount,transfersCount,holdersCount,address}
                        Sort by given column. Default: rank (default: rank)
  --descend             Flag to sort in descending order (lowest first)
                        (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default:
                        )
  -h, --help            show this help message (default: False)
```
