---
title: load
description: This documentation page provides information on the 'load' function used
  to get portfolio from predefined csv/json/xlsx files. It includes usage instructions
  as well as details on parameters like 'sector', 'country', 'last_price', 'show_nan'
  and 'path'.
keywords:
- load function
- predefined portfolio files
- csv portfolio
- json portfolio
- xlsx portfolio
- sector parameter
- country parameter
- last_price parameter
- show_nan parameter
- path parameter
- portfolio retrieval
- portfolio documentation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio/portfolio_analysis/load - Reference | OpenBB Terminal Docs" />

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
