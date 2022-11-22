---
title: Changing Sources
---

Some functions have the built-in capability of requesting data from multiple sources. `obb.stocks.load` is one example of this type feature:

```python
obb.stocks.load(
    symbol = 'SPY',
    start_date = '2022-10-01',
    end_date = '2022-11-11',
    interval = 15,
    prepost = True,
    source = 'YahooFinance',
    weekly = False,
    monthly = False,
)
```

| date                |    Open |   High |    Low |   Close |   Adj Close |      Volume |
|:--------------------|--------:|-------:|-------:|--------:|------------:|------------:|
| 2022-11-15 15:00:00 | 398.68  | 399.4  | 398.13 | 398.47  |     398.47  | 2.46198e+06 |
| 2022-11-15 15:15:00 | 398.475 | 399.52 | 398.46 | 398.913 |     398.913 | 2.8631e+06  |
| 2022-11-15 15:30:00 | 398.93  | 399.27 | 397.82 | 399.11  |     399.11  | 3.03659e+06 |
| 2022-11-15 15:45:00 | 399.114 | 399.13 | 397.46 | 398.53  |     398.53  | 6.46879e+06 |
| 2022-11-15 16:00:00 | 398.54  | 399.06 | 395.01 | 398.175 |     398.175 | 1.99462e+06 |


The choices for the `source` are currently:

  -  YahooFinance (default)
  -  IEXCloud
  -  AlphaVantage
  -  Polygon
  -  EODHD

Each source may have unique arguments, consult the docstrings for specfic details. If the command syntax is not framed as a variable assignment, results are printed as a table. When assigned to a variable, the table is not displayed.

There are functions which return a Tuple, and they can be identified through the docstrings. It will also be evident when the returned data is not presented as a DataFrame. The list, highlighted in the right frame of the image below, provides guidance for unpacking the results.

![Tuples](https://user-images.githubusercontent.com/85772166/201582221-8203a240-aa74-4755-989d-8cac167e40c6.png "Tuples")

The two elements within this Tuple are a DataFrame, and a String. Variables are assigned in the order described by the docstrings.

```python
data,title = obb.crypto.dd.mt(symbol = 'ETH', timeseries_id = 'act.addr.cnt', start_date = '2019-01-01')
```

Data need not be collected by the OpenBB SDK in order for it to be passed through the functions. Local files can be read with Pandas functions such as, `pd.read_csv()`. Importing an additional module, `pandas_datareader`, is a low-code method for requesting data from alternate sources.

```python
import pandas_datareader as pdr

spx_daily = pdr.get_data_stooq('^SPX', start = '1990-11-11')

spx_daily.tail(5)
```

| Date                |   Open |   High |    Low |   Close |      Volume |
|:--------------------|-------:|-------:|-------:|--------:|------------:|
| 1990-11-16 00:00:00 | 317.02 | 318.8  | 314.99 |  317.12 | 9.19111e+07 |
| 1990-11-15 00:00:00 | 320.4  | 320.4  | 316.13 |  317.02 | 8.40944e+07 |
| 1990-11-14 00:00:00 | 317.66 | 321.7  | 317.23 |  320.4  | 9.96167e+07 |
| 1990-11-13 00:00:00 | 319.48 | 319.48 | 317.26 |  317.67 | 8.90222e+07 |
| 1990-11-12 00:00:00 | 313.74 | 319.77 | 313.73 |  319.48 | 8.96611e+07 |

