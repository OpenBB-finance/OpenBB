---
title: pick
description: This page explains the usage of the load command for loading a FRED series
  to the current selection. This is useful for analyzing stock market data with various
  parameters such as Open, High, Low, Close, Adj Close, Volume, etc.
keywords:
- FRED series
- load command
- Stocks analysis
- TSLA
- Python commands
- Stock market
- Market data
- Open, High, Low, Close
- Adj Close, Volume
- date_id, OC_High, OC_Low
- Returns, LogRet
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy/qa/pick - Reference | OpenBB Terminal Docs" />

Load a FRED series to current selection

### Usage

```python
load [-c {Open,High,Low,Close,Adj Close,Volume,date_id,OC_High,OC_Low,Returns,LogRet}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| column | Which loaded source to get data from | None | True | Open, High, Low, Close, Adj Close, Volume, date_id, OC_High, OC_Low, Returns, LogRet |


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
