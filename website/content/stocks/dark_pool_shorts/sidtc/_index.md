```
usage: sidtc [-n NUM] [-s {float,dtc,si}] [--export {csv,json,xlsx}] [-h]
```

Request a list of shorted stocks, sorted by the optional arguments described below. Source: https://www.stockgrid.io/shortinterest

Note: This data is delayed as per the short interest reporting schedule dictated by FINRA. https://www.nasdaqtrader.com/trader.aspx?id=shortintpubsch

```
optional arguments:
  -n NUM, --number NUM  Number of top tickers to show (default: 10)
  -s {float,dtc,si}, --sort {float,dtc,si}
                        Field for which to sort by, where 'float': Float Short %, 'dtc': Days to Cover, 'si': Short Interest (default: float)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
<img width ="1400" alt="Feature Screenshot - sidtc" src="https://user-images.githubusercontent.com/85772166/140654378-1fc8672c-221a-4ccd-8e14-b294a2c2fef8.png">
