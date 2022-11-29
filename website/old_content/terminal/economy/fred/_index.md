```
usage: fred [-p PARAMETER [PARAMETER ...]] [-s START_DATE] [-e END_DATE] [-q QUERY [QUERY ...]] [-st] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}] [--raw] [-l LIMIT]
```

Query the FRED database and plot data based on the Series ID. [Source: FRED]

```
optional arguments:
  -p PARAMETER [PARAMETER ...], --parameter PARAMETER [PARAMETER ...]
                        Series ID of the Macro Economic data from FRED (default: None)
  -s START_DATE, --start_date START_DATE
                        Starting date (YYYY-MM-DD) of data (default: None)
  -e END_DATE, --end_date END_DATE
                        Ending date (YYYY-MM-DD) of data (default: None)
  -q QUERY [QUERY ...], --query QUERY [QUERY ...]
                        Query the FRED database to obtain Series IDs given the query search term. (default: None)
  -st, --store          Store the data to be used for plotting with the 'plot' command. (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  --raw                 Flag to display raw data (default: False)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 5)
```

Example:

```
2022 Mar 15, 07:08 (🦋) /economy/ $ fred -q treasuries
                                                                    Search results for treasuries
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Series ID ┃ Title                                           ┃ Description                                                                                         ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ T10Y2Y    │ 10-Year Treasury Constant Maturity Minus 2-Year │ Starting with the update on June 21, 2019, the Treasury bond data used in calculating interest rate │
│           │ Treasury Constant Maturity                      │ spreads is obtained directly from the U.S. Treasury Department (https://www.treasury.gov/resource-  │
│           │                                                 │ center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield).  Series is calculated as   │
│           │                                                 │ the spread between 10-Year Treasury Constant Maturity (BC_10YEAR) and 2-Year Treasury Constant      │
│           │                                                 │ Maturity (BC_2YEAR). Both underlying series are published at the U.S. Treasury Department           │
│           │                                                 │ (https://www.treasury.gov/resource-center/data-chart-center/interest-                               │
│           │                                                 │ rates/Pages/TextView.aspx?data=yield).                                                              │
├───────────┼─────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ T10Y2YM   │ 10-Year Treasury Constant Maturity Minus 2-Year │ Series is calculated as the spread between 10-Year Treasury Constant Maturity (BC_10YEARM) and      │
│           │ Treasury Constant Maturity                      │ 2-Year Treasury Constant Maturity (BC_2YEARM). Starting with the update on June 21, 2019, the       │
│           │                                                 │ Treasury bond data used in calculating interest rate spreads is obtained directly from the U.S.     │
│           │                                                 │ Treasury Department (https://www.treasury.gov/resource-center/data-chart-center/interest-           │
│           │                                                 │ rates/Pages/TextView.aspx?data=yield).                                                              │
├───────────┼─────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DFII10    │ Market Yield on U.S. Treasury Securities at     │ For further information regarding treasury constant maturity data, please refer to the Board of     │
│           │ 10-Year Constant Maturity, Inflation-Indexed    │ Governors ( http://www.federalreserve.gov/releases/h15/current/h15.pdf) and the Treasury            │
│           │                                                 │ (http://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/yieldmethod.aspx).  │
├───────────┼─────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ FII10     │ Market Yield on U.S. Treasury Securities at     │ For further information regarding treasury constant maturity data, please refer to                  │
│           │ 10-Year Constant Maturity, Inflation-Indexed    │ http://www.federalreserve.gov/releases/h15/current/h15.pdf and http://www.treasury.gov/resource-    │
│           │                                                 │ center/data-chart-center/interest-rates/Pages/yieldmethod.aspx.                                     │
├───────────┼─────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ WFII10    │ Market Yield on U.S. Treasury Securities at     │ For further information regarding treasury constant maturity data, please refer to                  │
│           │ 10-Year Constant Maturity, Inflation-Indexed    │ http://www.federalreserve.gov/releases/h15/current/h15.pdf and http://www.treasury.gov/resource-    │
│           │                                                 │ center/data-chart-center/interest-rates/Pages/yieldmethod.aspx.                                     │
└───────────┴─────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

```
2022 Mar 15, 07:09 (🦋) /economy/ $ fred T10Y2Y,DFII10 -s 2019-01-01 -e 2022-01-01
```

![fred](https://user-images.githubusercontent.com/46355364/158575129-1d4b26de-8bd8-49b3-b1b9-e349afaf8a50.png)
