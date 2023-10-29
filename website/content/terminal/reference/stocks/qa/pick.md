---
title: pick
description: This page provides information on how to select different parameters
  (like high, low, close etc.) for daily stock analysis, especially for TSLA stocks.
  It explains the usage of the 'pick' command within the Python environment for stock
  parameter selection.
keywords:
- target variable
- stock analysis
- daily stock
- tsla stock
- pick
- stock parameter selection
- stock market
- stock data manipulation
- market data
- financial data analysis
- time series data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/qa/pick - Reference | OpenBB Terminal Docs" />

Change target variable

### Usage

```python
pick [-t {open,high,low,close,adjclose,volume,date_id,oc_high,oc_low,returns,logret,logprice}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| target | Select variable to analyze | None | True | open, high, low, close, adjclose, volume, date_id, oc_high, oc_low, returns, logret, logprice |


---

## Examples

```python
2022 Feb 16, 11:12 (🦋) /stocks/qa/ $ load tsla

Loading Daily TSLA stock with starting period 2019-02-11 for analysis.

Datetime: 2022 Feb 16 11:12
Timezone: America/New_York
Currency: USD
Market:   CLOSED


2022 Feb 16, 11:12 (🦋) /stocks/qa/ $ pick adjclose
```
---
