---
title: pick
description: OpenBB Terminal Function
---

# pick

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
