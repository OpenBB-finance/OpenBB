```
usage: series [-i SERIES_ID] [-s START_DATE] [--raw] [--export {png,jpg,pdf,svg}] [-h]
```

Display (multiple) series from https://fred.stlouisfed.org. [Source: FRED]

```
optional arguments:
  -i SERIES_ID, --id SERIES_ID
                        FRED Series from https://fred.stlouisfed.org. For multiple series use: series1,series2,series3
  -s START_DATE         Starting date (YYYY-MM-DD) of data
  --raw                 Only output raw data
  --export {png,jpg,pdf,svg}
                        Export data to csv,json,xlsx or png,jpg,pdf,svg file
  -h, --help            show this help message
```
