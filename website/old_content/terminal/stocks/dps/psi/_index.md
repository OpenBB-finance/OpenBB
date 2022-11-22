```
usage: psi [--source {quandl,stockgrid}] [--nyse] [-n NUM] [-r] [--export {csv,json,xlsx}] [-h]
```

Shows a graph of price vs short interest volume over a variable number of days, selectable from two sources: [StockGrid](https://Stockgrid.io) and [Quandl API](https://data.nasdaq.com/publishers/qdl). Print the raw data using the '-r' argument for closer scrutiny of the data. Data is updated daily after market close. 

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

![Figure_2](https://user-images.githubusercontent.com/46355364/154076731-e1f5ad9c-71c7-4c56-93b1-613985057951.png)
