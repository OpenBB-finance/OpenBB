```
usage: candle [-s S_START] [--plotly] [-h] [--raw] [-p {1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max}]
              [-i {1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo}] [-e {csv, json, xlsx}]
              [-s {Date, Open, Close, High, Low, Volume, Dividend, Stock Splits}] [-d]
```

Displays candle chart of loaded ticker, or shows raw data with --raw

```
optional arguments:
  -s S_START, --start_date S_START
                        Start date for candle data (default: 2021-03-19)
  --plotly              Flag to show interactive plot using plotly. (default: False)
  --raw                 shows the raw data instead of a chart
  -p, --period          The period to show information for
  -i, --interval        The interval between each item of financial information
  -e, --export          The format to export the information into
  -s, --sort            Which column to sort the information by
  -d, --descending      Show the information in descending order
  -h, --help            show this help message (default: False)
```

![nio](https://user-images.githubusercontent.com/25267873/111053397-4d609e00-845b-11eb-9c94-89b8892a8e81.png)
