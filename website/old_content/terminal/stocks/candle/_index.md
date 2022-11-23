```
usage: candle [-p] [--sort {AdjClose,Open,Close,High,Low,Volume,Returns,LogRet}] [-d] [--raw] [-t] [--ma MOV_AVG] [--log] [-h] [--export EXPORT] [-l LIMIT]
```
Shows historic data for a stock
```
optional arguments:
  -p, --plotly          Flag to show interactive plotly chart (default: True)
  --sort {AdjClose,Open,Close,High,Low,Volume,Returns,LogRet}
                        Choose a column to sort by. Only works when raw data is displayed. (default: )
  -r, --reverse         Data is sorted in descending order by default. Reverse flag will sort it in an ascending way.
                        Only works when raw data is displayed. (default: False)
  --raw                 Shows raw data instead of chart. If sort is set those are the top ones, otherwise we grab latest data to date (default: False)
  -t, --trend           Flag to add high and low trends to candle (default: False)
  --ma MOV_AVG          Add moving average in number of days to plot and separate by a comma. Value for ma (moving average) keyword needs to be greater than 1. (default: None)
  --log                 Plot with y axis on log scale (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 20)
```
For more information and examples, use 'about candle' to access the related guide.


![candle](https://user-images.githubusercontent.com/46355364/154072214-f4b49833-157f-44a7-be2d-d558ffc6f945.png)
