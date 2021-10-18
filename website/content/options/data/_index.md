```
usage: data [--export {csv,json,xlsx}] [-s {Date,Open,Close,High,Low,Change,Volume,Open Interest, Change Since}]
            [-d] [-p] [-k STRIKE] [-h]
```

Show historical data for various options.

```
optional arguments:
  --export              export the data
  -s, --sort            choose a column to sort by
  -d, --descending      sort the columns descending
  -p, --put             use puts instead of calls
  -k STRIKE, --strike STRIKE
                        set the strike price for the history
  -h, --help            show this help message (default: False)
```
