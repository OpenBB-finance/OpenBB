---
title: pick
description: This page provides detailed information on how to use the 'pick' function
  for changing the target variable for analysis. It includes usage instructions, the
  various parameters used, and specific examples dealing primarily with stock analysis.
keywords:
- target variable change
- usage of pick
- parameters of pick
- examples of pick
- stock analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex/qa/pick - Reference | OpenBB Terminal Docs" />

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
