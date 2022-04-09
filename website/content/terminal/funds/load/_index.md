```
usage: load [-f FUND [FUND ...]] [--name] [-s START] [-e END] [-h]
```

Get historical data.
```
optional arguments:
  -f FUND [FUND ...], --fund FUND [FUND ...]
                        Fund string to search for (default: None)
  --name                Flag to indicate name provided instead of symbol. (default: False)
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the fund (default: 2020-12-27)
  -e END, --end END     The ending date (format YYYY-MM-DD) of the fund (default: 2021-12-28)
  -h, --help            show this help message (default: False)
```