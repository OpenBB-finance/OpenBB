---
title: load
description: OpenBB Terminal Function
---

# load

Function to get portfolio from predefined csv/json/xlsx file inside portfolios folder

### Usage

```python
load [-s] [-c] [--no_last_price] [--nan] [-p {}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| sector | Add sector to dataframe | False | True | None |
| country | Add country to dataframe | False | True | None |
| last_price | Don't add last price from yfinance | True | True | None |
| show_nan | Show nan entries | False | True | None |
| path | Path to portfolio file | my_portfolio.csv | True | None |

---
