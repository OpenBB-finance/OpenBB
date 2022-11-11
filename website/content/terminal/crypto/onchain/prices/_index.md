```
usage: prices [-l N] [-s {date,cap,volumeConverted,open,high,close,low}] [--reverse] [--export {csv,json,xlsx}] [-h]
```

Display token historical prices. e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984 [Source: Ethplorer]

```
optional arguments:
  -l N, --limit N     display N number records (default: 10)
  -s {date,cap,volumeConverted,open,high,close,low}, --sort {date,cap,volumeConverted,open,high,close,low}
                        Sort by given column. Default: date (default: date)
  -r, --reverse         Data is sorted in descending order by default.
                        Reverse flag will sort it in an ascending way.
                        Only works when raw data is displayed. (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
