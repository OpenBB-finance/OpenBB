```
usage: candle [--ma MOV_AVG] [-h]
```

Show candle for loaded fx data

```
optional arguments:
  -p, --plotly          Flag to show interactive plotly chart (default: True)
  --sort {adjclose,open,close,high,low,volume,logret}
                        Choose a column to sort by. Only works when raw data is displayed. (default: )
  -r, --reverse         Data is sorted in descending order by default.
                        Reverse flag will sort it in an ascending way.
                        Only works when raw data is displayed. (default: False)
  --raw                 Shows raw data instead of chart. (default: False)
  -t, --trend           Flag to add high and low trends to candle (default: False)
  --ma MOV_AVG          Add moving average in number of days to plot and separate by a comma. Value for ma (moving average) keyword needs to be greater than 1. (default: None)
  --log                 Plot with y axis on log scale (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 20)
```

![candle](https://user-images.githubusercontent.com/46355364/154029283-2e5e472b-4c2b-4e88-8fbe-f6a0925898b8.png)
