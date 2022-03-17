```
usage: balance [-l N] [-s {index,balance,tokenName,tokenSymbol}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Display info about tokens on given ethereum blockchain address. [Source:
Ethplorer]

```
optional arguments:
  -l N, --limit N         display N number records (default: 10)
  -s {index,balance,tokenName,tokenSymbol}, --sort {index,balance,tokenName,tokenSymbol}
                        Sort by given column. Default: index (default: index)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)

```
