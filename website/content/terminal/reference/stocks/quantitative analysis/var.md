---
title: var
description: OpenBB Terminal Function
---

# var

Provides value at risk (short: VaR) of the selected stock.

### Usage

```python
usage: var [-m] [-a] [-s] [-p PERCENTILE] [-d DATA_RANGE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| use_mean | If one should use the mean of the stocks return | False | True | None |
| adjusted | If the VaR should be adjusted for skew and kurtosis (Cornish-Fisher-Expansion) | False | True | None |
| student_t | If one should use the student-t distribution | False | True | None |
| percentile | Percentile used for VaR calculations, for example input 99.9 equals a 99.9 Percent VaR | 99.9 | True | None |
| data_range | Number of rows you want to use VaR over, ex: if you are using days, 30 would show VaR for the last 30 TRADING days | 0 | True | None |
---

