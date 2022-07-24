```
usage: holders [-l N] [-s {balance,balance,share}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Display top ERC20 token holders: e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984 [Source: Ethplorer]

```
optional arguments:
  -l N, --limit N     display N number records (default: 10)
  -s {balance,balance,share}, --sort {balance,balance,share}
                        Sort by given column. Default: share (default: share)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
