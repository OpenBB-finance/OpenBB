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
<img width="1400" alt="Feature Screenshot - psi stockgrid" src="https://user-images.githubusercontent.com/85772166/140653536-7dd8e65c-ab74-4fd7-862e-03478ebde407.png">
<img width="1400" alt="Feature Screenshot - psi quandl nasdaq" src="https://user-images.githubusercontent.com/85772166/140653600-4a187b96-3d27-4529-aad7-2c1b01daf351.png">
<img width="1400" alt="Feature Screenshot - quandl nyse" src="https://user-images.githubusercontent.com/85772166/140653651-59251eb9-5c08-4a4f-a570-45439e56b078.png">

<img width ="1400" alt="Feature Screenshot - psi raw" src="https://user-images.githubusercontent.com/85772166/140653831-db2ab699-c6a3-4755-9d81-ed5728622265.png">
