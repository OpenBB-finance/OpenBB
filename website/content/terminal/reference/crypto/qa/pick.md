---
title: pick
description: The page provides detailed information about the 'pick' command which
  is used to change target variables for stock market analysis, using Python. It lists
  the usage, parameters, and examples for easier understanding.
keywords:
- pick
- target variable
- parameters
- stock analysis
- stock market
- examples
- usage
- Open
- High
- Low
- Close
- Adj Close
- Volume
- date_id
- OC_High
- OC_Low
- Returns
- LogRet
- TSLA
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/qa/pick - Reference | OpenBB Terminal Docs" />

Change target variable

### Usage

```python
pick [-t {Open,High,Low,Close,Adj Close,Volume,date_id,OC_High,OC_Low,Returns,LogRet}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| target | Select variable to analyze | None | True | Open, High, Low, Close, Adj Close, Volume, date_id, OC_High, OC_Low, Returns, LogRet |


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
