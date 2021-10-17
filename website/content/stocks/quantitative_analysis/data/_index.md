```
usage: data [-p {1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max}] [-i {1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo}]
                [-e {csv, json, xlsx}] [-s {Date, Open, Close, High, Low, Volume, Dividend, Stock Splits}] [-d]
```

Shows a table of historical information for a stock with the option to export the data [Source: Yahoo Finance]

```
optional arguments:
  -p, --period          The period to show information for
  -i, --interval        The interval between each item of financial information
  -e, --export          The format to export the information into
  -s, --sort            Which column to sort the information by
  -d, --descending      Show the information in descending order
```
