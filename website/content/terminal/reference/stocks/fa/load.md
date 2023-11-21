---
title: load
description: This page provides comprehensive instructions on how to load stock tickers
  to perform analysis. It highlights how to load Indian market stocks with '.NS' and
  provides a link to the Yahoo finance available markets. The page features various
  parameters to tailor analysis including adjustments for start and end dates, interval
  times, and loading custom files.
keywords:
- Load stock ticker
- Perform analysis
- India stock market
- .NS
- Yahoo finance
- Exchanges data providers
- Parameters
- Stock interval
- Intraday stock minutes
- Load monthly data
- Load weekly data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/fa/load - Reference | OpenBB Terminal Docs" />

Load stock ticker to perform analysis on. When the data source is syf', an Indian ticker can be loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html.

### Usage

```python
load -t TICKER [-s START] [-e END] [-i {1,5,15,30,60}] [-p] [-f FILEPATH] [-m] [-w] [-r {ytd,1y,2y,5y,6m}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| ticker | Stock ticker | None | False | None |
| start | The starting date (format YYYY-MM-DD) of the stock | 2019-11-21 | True | None |
| end | The ending date (format YYYY-MM-DD) of the stock | 2022-11-25 | True | None |
| interval | Intraday stock minutes | 1440 | True | 1, 5, 15, 30, 60 |
| prepost | Pre/After market hours. Only works for 'yf' source, and intraday data | False | True | None |
| filepath | Path to load custom file. | None | True | None |
| monthly | Load monthly data | False | True | None |
| weekly | Load weekly data | False | True | None |

---
