---
title: load
description: This documentation page supports users in stock analysis by guiding them
  on how to load a stock ticker. It explains various parameters such as market source,
  date ranges, pre/after market hours, and periodicity of data. It also includes guidance
  for loading custom files and managing data at different frequencies.
keywords:
- Load stock ticker
- Stock analysis
- Data source
- Indian ticker
- Market analysis
- Intraday stock minutes
- Pre/After market hours
- Load custom file
- Monthly data
- Weekly data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex/ta/load - Reference | OpenBB Terminal Docs" />

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
