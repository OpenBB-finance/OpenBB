```
usage: ycrv [-s {FRED,investpy}] [-c COUNTRY [COUNTRY ...]] [-d DATE] [-h] [--export EXPORT] [--raw]
```

Generate country yield curve. The yield curve shows the bond rates at different maturities.

```
optional arguments:
  -s {FRED,investpy}, --source {FRED,investpy}
                        Source for the data. If not supplied, the most recent entry from investpy will be used. (default: investpy)
  -c COUNTRY [COUNTRY ...], --country COUNTRY [COUNTRY ...]
                        Display yield curve for specific country. (default: united states)
  -d DATE, --date DATE  Date to get data from FRED. If not supplied, the most recent entry will be used. (default: None)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --raw                 Flag to display raw data (default: False)
```
