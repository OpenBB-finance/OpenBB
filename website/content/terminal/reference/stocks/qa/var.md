---
title: var
description: OpenBB Terminal Function
---

# var

Provides value at risk (short: VaR) of the selected stock.

### Usage

```python
var [-m] [-a] [-s] [-p PERCENTILE] [-d DATA_RANGE]
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

## Examples

```python
2022 Feb 16, 11:18 (🦋) /stocks/qa/ $ var
          FB Value at Risk
┏━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃       ┃ VaR:    ┃ Historical VaR: ┃
┡━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 90.0% │ -0.0305 │ -0.0233         │
├───────┼─────────┼─────────────────┤
│ 95.0% │ -0.0389 │ -0.0364         │
├───────┼─────────┼─────────────────┤
│ 99.0% │ -0.0546 │ -0.0578         │
├───────┼─────────┼─────────────────┤
│ 99.9% │ -0.0719 │ -0.1719         │
└───────┴─────────┴─────────────────┘
```
---
