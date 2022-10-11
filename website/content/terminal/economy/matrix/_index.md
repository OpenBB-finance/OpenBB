```
usage: matrix [-g {G7,PIIGS,EUROZONE}] [-c COUNTRIES] [-m MATURITY] [--change CHANGE] [-h] [--export EXPORT] [--raw]
```

Generate bond rates matrix.

```
optional arguments:
  -g {G7,PIIGS,EUROZONE}, --group {G7,PIIGS,EUROZONE}
                        Show bond rates matrix for group of countries. (default: G7)
  -c COUNTRIES, --countries COUNTRIES
                        Show bond rates matrix for explicit list of countries. (default: None)
  -m MATURITY, --maturity MATURITY
                        Specify maturity to compare rates. (default: 10Y)
  --change CHANGE       Get matrix of 1 day change in rates. (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --raw                 Flag to display raw data (default: False)
```
