---
title: Changing Sources
sidebar_position: 2
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

| date                |    Open |   High |    Low |   Close | Adj Close |      Volume |
| :------------------ | ------: | -----: | -----: | ------: | --------: | ----------: |
| 2022-11-15 15:00:00 |  398.68 |  399.4 | 398.13 |  398.47 |    398.47 | 2.46198e+06 |
| 2022-11-15 15:15:00 | 398.475 | 399.52 | 398.46 | 398.913 |   398.913 |  2.8631e+06 |
| 2022-11-15 15:30:00 |  398.93 | 399.27 | 397.82 |  399.11 |    399.11 | 3.03659e+06 |
| 2022-11-15 15:45:00 | 399.114 | 399.13 | 397.46 |  398.53 |    398.53 | 6.46879e+06 |
| 2022-11-15 16:00:00 |  398.54 | 399.06 | 395.01 | 398.175 |   398.175 | 1.99462e+06 |

The choices for `source` within this functionality are:

- YahooFinance (default)
- IEXCloud
- AlphaVantage
- Polygon
- EODHD

Note that for each function, the variable can have sources that are not described as above. As an example, `openbb.stocks.fa.income` has the following sources:

- Polygon
- YahooFinance
- AlphaVantage
- FinancialModelingPrep
- EODHD

Also note that some sources allow you to use certain variables while other do not. For example, `YahooFinance` doesn't provide you with quarterly data whereas `AlphaVantage` does. Therefore, `quarterly=True` can not be used in combination with `source=YahooFinance`.
