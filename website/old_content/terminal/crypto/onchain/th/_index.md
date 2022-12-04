```
usage: th [-l N] [-s {value}] [--reverse] [--hash] [--export {csv,json,xlsx}] [-h]
```

Displays info about token history. e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984 [Source: Ethplorer]

```
optional arguments:
  -l N, --limit N     display N number records (default: 10)
  -s {value}, --sort {value}
                        Sort by given column. Default: value (default: value)
  -r, --reverse         Data is sorted in descending order by default.
                        Reverse flag will sort it in an ascending way.
                        Only works when raw data is displayed. (default: False)
  --hash                Flag to show transaction hash (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
