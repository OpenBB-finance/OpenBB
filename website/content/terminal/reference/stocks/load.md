---
title: load
description: This documentation page provides detailed information on how to load
  stock tickers using various parameters for analysis. Users can customize their usage
  through options like start and end dates, interval, pre/after market hours, load
  monthly or weekly data, among others.
keywords:
- Stock Analysis
- Load Stock Tickers
- Investment Analysis
- Financial Data
- Stock Market
- Yahoo Finance
- Custom Stock Data
- Intraday Stock
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /load - Reference | OpenBB Terminal Docs" />

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

## Examples

```python
txt
2022 Feb 16, 08:29 (🦋) /stocks/ $ load TSLA

Loading Daily TSLA stock with starting period 2019-02-11 for analysis.

Datetime: 2022 Feb 16 08:30
Timezone: America/New_York
Currency: USD
Market:   OPEN

2022 Feb 16, 08:30 (🦋) /stocks/ $ load AAPL

Loading Daily AAPL stock with starting period 2019-02-11 for analysis.

Datetime: 2022 Feb 16 08:30
Timezone: America/New_York
Currency: USD
Market:   OPEN

2022 Feb 16, 08:30 (🦋) /stocks/ $ load AMZN

Loading Daily AMZN stock with starting period 2019-02-11 for analysis.

Datetime: 2022 Feb 16 08:30
Timezone: America/New_York
Currency: USD
Market:   OPEN
```
---
