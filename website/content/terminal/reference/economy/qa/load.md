---
title: load
description: This page provides a guide on how to load a stock ticker for analysis.
  It explains the parameters for loading data, including options for Indian tickers,
  intraday stock minutes, and custom file paths. Additionally, users can find information
  on how to load monthly and weekly data.
keywords:
- load
- stock ticker
- analysis
- syf
- Indian ticker
- exchanges data providers
- Yahoo finance
- starting date
- ending date
- intraday stock minutes
- pre/after market hours
- custom file path
- monthly data
- weekly data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /qa/load - Reference | OpenBB Terminal Docs" />

Load stock ticker to perform analysis on. When the data source is yf, an Indian ticker can be loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html.

### Usage

```python wordwrap
load [-t TICKER] [-s START] [-e END] [-i {1,5,15,30,60}] [-p] [-f FILEPATH] [-m] [-w] [--performance] [--india]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| ticker | -t  --ticker | Stock ticker | None | True | None |
| start | -s  --start | The starting date (format YYYY-MM-DD) of the stock | 2020-11-16 | True | None |
| end | -e  --end | The ending date (format YYYY-MM-DD) of the stock | 2023-11-21 | True | None |
| interval | -i  --interval | Intraday stock minutes | 1440 | True | 1, 5, 15, 30, 60 |
| prepost | -p  --prepost | Pre/After market hours. Only reflected in 'YahooFinance' intraday data. | False | True | None |
| filepath | -f  --file | Path to load custom file. | None | True | None |
| monthly | -m  --monthly | Load monthly data | False | True | None |
| weekly | -w  --weekly | Load weekly data | False | True | None |
| performance | --performance | Show performance information. | False | True | None |
| india | --india | Only works for yf source, when the ticker has .NS suffix as part of it. | False | True | None |

---
