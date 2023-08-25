---
title: pick
description: OpenBB Terminal Function
---

# pick

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
