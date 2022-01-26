```
usage: screen [-l LIMIT] [-s {Assets,NAV,Expense,PE,SharesOut,Div,DivYield,Volume,Open,PrevClose,YrLow,YrHigh,Beta,N_Hold}] [-a] [-h] [--export {csv,json,xlsx}]
```

Screens ETFs by the metrics listed below.

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Limit of etfs to display (default: 10)
  -s {Assets,NAV,Expense,PE,SharesOut,Div,DivYield,Volume,Open,PrevClose,YrLow,YrHigh,Beta,N_Hold}, --sort {Assets,NAV,Expense,PE,SharesOut,Div,DivYield,Volume,Open,PrevClose,YrLow,YrHigh,Beta,N_Hold}
                        Sort by given column. Default: Assets (default: Assets)
  -a, --ascend          Flag to sort in ascending order (lowest on top) (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

<img width="1400" alt="Feature Screenshot - etf-screen" src="https://user-images.githubusercontent.com/85772166/150078217-3880f207-4205-4b90-a19e-73465bbcf4df.png">