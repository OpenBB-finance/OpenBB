```
usage: candle [-m] [--export {csv,json,xlsx}] [--sort {AdjClose,Open,Close,High,Low,Volume,Returns,LogRet}] [-d] [--raw] [-n NUM] [-h]
```

Shows historic data for the loaded ticker in an interactive chart that loads in a web browser. Static charts are also available through the optional '-m' argument. There is also the ability to retrieve and sort raw data sets based on the intraday interval and date window selected through the load command.

```
optional arguments:
  -m, --matplotlib      Flag to show matplotlib instead of interactive plot using plotly. (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  --sort {AdjClose,Open,Close,High,Low,Volume,Returns,LogRet}
                        Choose a column to sort by (default: )
  -d, --descending      Sort selected column descending (default: True)
  --raw                 Shows raw data instead of chart (default: False)
  -n NUM, --num NUM     Number to show if raw selected (default: 20)
  -h, --help            show this help message (default: False)
```

![candle](https://user-images.githubusercontent.com/46355364/154072214-f4b49833-157f-44a7-be2d-d558ffc6f945.png)
