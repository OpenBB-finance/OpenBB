`usage: aprtoapy [--apr APR] [-c COMPOUNDING] [-n] [-h] [--export EXPORT]`

Tool to calculate APY from APR value. Compounding periods, i.e., the number of times compounded per year can be defined with -c argument.

```
optional arguments:
  --apr APR             APR value in percentage to convert (default: 100)
  -c COMPOUNDING, --compounding COMPOUNDING
                        Number of compounded periods in a year. 12 means compounding monthly (default: 12)
  -n, --narrative       Flag to show narra`ive instead of dataframe (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
```
