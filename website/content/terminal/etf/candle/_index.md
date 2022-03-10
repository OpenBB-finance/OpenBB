```text
usage: candle [-p] [--sort {AdjClose,Open,Close,High,Low,Volume,Returns,LogRet}] [-d] [--raw] [-n NUM] [-t] [--ma MOV_AVG] [-h] [--export {csv,json,xlsx}]
```

Shows historic data for an ETF
```
optional arguments:
  -p, --plotly          Flag to show interactive plotly chart. (default: True)
  --sort {AdjClose,Open,Close,High,Low,Volume,Returns,LogRet}
                        Choose a column to sort by (default: )
  -d, --descending      Sort selected column descending (default: True)
  --raw                 Shows raw data instead of chart (default: False)
  -n NUM, --num NUM     Number to show if raw selected (default: 20)
  -t, --trend           Flag to add high and low trends to candle. (default: False)
  --ma MOV_AVG          Add moving averaged to plot (default: )
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

![candle](https://user-images.githubusercontent.com/46355364/154031063-090a4419-c3b1-4707-8f8e-b41c872a783a.png)
