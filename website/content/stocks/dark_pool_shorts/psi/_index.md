```
usage: psi [--source {quandl,stockgrid}] [--nyse] [-n NUM] [-r] [--export {csv,json,xlsx}] [-h]
```

Shows price vs short interest volume. [Source: Quandl/Stockgrid]

```
optional arguments:
  --source {quandl,stockgrid}
                        Source of short interest volume
  --nyse                ONLY QUANDL SOURCE. Data from NYSE flag. Otherwise comes from NASDAQ.
  -n NUM, --number NUM  Number of last open market days to show
  -r                    Flag to print raw data instead
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file
  -h, --help            show this help message
```
