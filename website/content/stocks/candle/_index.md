```
usage: candle [-s S_START] [--plotly] [-h] [--raw] [-e {csv, json, xlsx}] -s SORT] [-d]
```

Displays candle chart of loaded ticker, or shows raw data with --raw (Test change)

```
optional arguments:
  -s S_START, --start_date S_START
                        Start date for candle data (default: 2021-03-19)
  --plotly              Flag to show interactive plot using plotly. (default: False)
  --raw                 shows the raw data instead of a chart
  -e, --export          The format to export the information into
  -s, --sort            Which column to sort the information by
  -d, --descending      Show the information in descending order
  -h, --help            show this help message (default: False)
``` 

![nio](https://user-images.githubusercontent.com/25267873/111053397-4d609e00-845b-11eb-9c94-89b8892a8e81.png)
