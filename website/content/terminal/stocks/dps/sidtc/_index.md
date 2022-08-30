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

Example:

```
2022 Feb 15, 11:07 (✨) /stocks/dps/ $ sidtc
                      Data for: 2022-01-31
┌────────┬───────────────┬───────────────┬─────────────────────┐
│ Ticker │ Float Short % │ Days to Cover │ Short Interest [1M] │
├────────┼───────────────┼───────────────┼─────────────────────┤
│ VIEW   │ 40.70         │ 14.92         │ 21.46               │
├────────┼───────────────┼───────────────┼─────────────────────┤
│ HRTX   │ 34.06         │ 14.92         │ 34.64               │
├────────┼───────────────┼───────────────┼─────────────────────┤
│ IRBT   │ 24.47         │ 13.85         │ 6.47                │
├────────┼───────────────┼───────────────┼─────────────────────┤
│ ZYXI   │ 24.13         │ 14.43         │ 4.77                │
├────────┼───────────────┼───────────────┼─────────────────────┤
│ TDUP   │ 22.94         │ 14.14         │ 11.93               │
├────────┼───────────────┼───────────────┼─────────────────────┤
│ GOGO   │ 22.44         │ 25.02         │ 17.84               │
├────────┼───────────────┼───────────────┼─────────────────────┤
│ SATS   │ 19.49         │ 23.27         │ 7.14                │
├────────┼───────────────┼───────────────┼─────────────────────┤
│ RLAY   │ 19.32         │ 20.15         │ 14.88               │
├────────┼───────────────┼───────────────┼─────────────────────┤
│ OMER   │ 18.89         │ 13.36         │ 11.32               │
├────────┼───────────────┼───────────────┼─────────────────────┤
│ AXDX   │ 18.75         │ 19.71         │ 7.00                │
└────────┴───────────────┴───────────────┴─────────────────────┘
```
