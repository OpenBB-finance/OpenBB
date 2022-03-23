```
usage: index [-i INDICES [INDICES ...]] [-si] [-iv {1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo}] [-s START_DATE] [-e END_DATE] [-c COLUMN] [-q QUERY [QUERY ...]] [-st] [-h] [--export {csv,json,xlsx}] [--raw] [-l LIMIT]
```

Obtain any set of indices and plot them together. With the -si argument the major indices are shown. By using the arguments (for example 'nasdaq' and 'sp500') you can collect data and plot the graphs together. [Source: Yahoo finance / FinanceDatabase]

```
optional arguments:
  -i INDICES [INDICES ...], --indices INDICES [INDICES ...]
                        One or multiple indices (default: None)
  -si, --show_indices   Show the major indices, their arguments and ticker (default: False)
  -iv {1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo}, --interval {1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo}
                        The preferred interval data is shown at. This can be 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo or 3mo (default: 1d)
  -s START_DATE, --start_date START_DATE
                        The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31) (default: 2000-01-01)
  -e END_DATE, --end_date END_DATE
                        The end date of the data (format: YEAR-MONTH-DAY, i.e. 2021-06-20) (default: None)
  -c COLUMN, --column COLUMN
                        The column you wish to load in, by default this is the Adjusted Close column (default: Adj Close)
  -q QUERY [QUERY ...], --query QUERY [QUERY ...]
                        Search for indices with given keyword (default: None)
  -st, --store          Store the data to be used for plotting with the 'plot' command. (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
  --raw                 Flag to display raw data (default: False)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 10)
```

Example:
```
2022 Mar 15, 07:29 (✨) /economy/ $ index nasdaq dowjones
```
![index nasdaq dowjones](https://user-images.githubusercontent.com/46355364/158573612-f2e4b04c-b833-4899-9817-62e40b9fe1d2.png)

```
2022 Mar 15, 07:29 (✨) /economy/ $ index vix
```
![index vix](https://user-images.githubusercontent.com/46355364/158573676-9871c58e-3ffd-44d5-888a-c1d76ec98251.png)

```
2022 Mar 15, 07:30 (✨) /economy/ $ index -si
                     Major Indices                     
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Argument ┃ Name                         ┃ Ticker    ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ sp500    │ S&P 500                      │ ^GSPC     │
├──────────┼──────────────────────────────┼───────────┤
│ nasdaq   │ Nasdaq Composite             │ ^IXIC     │
├──────────┼──────────────────────────────┼───────────┤
│ dowjones │ Dow Jones Industrial Average │ ^DJI      │
├──────────┼──────────────────────────────┼───────────┤
│ vix      │ CBOE Volatility Index        │ ^VIX      │
├──────────┼──────────────────────────────┼───────────┤
│ russel   │ Russel 2000 Index            │ ^RUT      │
├──────────┼──────────────────────────────┼───────────┤
│ tsx      │ TSX Composite                │ ^GSPTSE   │
├──────────┼──────────────────────────────┼───────────┤
│ nikkei   │ Nikkei 255 Stock Average     │ ^N225     │
├──────────┼──────────────────────────────┼───────────┤
│ shanghai │ Shanghai Composite Index     │ 000001.SS │
├──────────┼──────────────────────────────┼───────────┤
│ ftse100  │ FTSE 100 Index ('footsie')   │ ^FTSE     │
├──────────┼──────────────────────────────┼───────────┤
│ stoxx50  │ Euro STOXX 50                │ ^STOXX50E │
├──────────┼──────────────────────────────┼───────────┤
│ dax      │ DAX Performance Index        │ ^GDAXI    │
├──────────┼──────────────────────────────┼───────────┤
│ cac40    │ CAC 40 Index                 │ ^FCHI     │
└──────────┴──────────────────────────────┴───────────┘
```
