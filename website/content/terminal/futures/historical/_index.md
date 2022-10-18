```
usage: historical [-t TICKER] [-s START] [-e EXPIRY] [-h] [--export EXPORT] [--raw]
```

Display futures historical. [Source: YahooFinance]

```
optional arguments:
  -t TICKER, --ticker TICKER
                        Future ticker to display timeseries separated by comma when multiple, e.g.: BLK,QI (default: )
  -s START, --start START
                        Initial date. Default: 3 years ago (default: 2019-10-20 00:12:05.223144)
  -e EXPIRY, --expiry EXPIRY
                        Select future expiry date with format YYYY-MM (default: )
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  --raw                 Flag to display raw data (default: False)
```