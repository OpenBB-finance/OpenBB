```text
usage: load [-t S_TICKER] [-s S_START_DATE] [-i {1,5,15,30,60}] [--source {yf,av,iex}] [-p] [-h]
```

Shortcut to the [load](https://gamestonkterminal.github.io/stocks/load/) feature.

```
optional arguments:
  -t S_TICKER, --ticker S_TICKER
                        Stock ticker (default: None)
  -s S_START_DATE, --start S_START_DATE
                        The starting date (format YYYY-MM-DD) of the stock (default: 2020-09-15)
  -i {1,5,15,30,60}, --interval {1,5,15,30,60}
                        Intraday stock minutes (default: 1440)
  --source {yf,av,iex}  Source of historical data. (default: yf)
  -p, --prepost         Pre/After market hours. Only works for 'yf' source, and intraday data (default: False)
  -h, --help            show this help message (default: False)
```
