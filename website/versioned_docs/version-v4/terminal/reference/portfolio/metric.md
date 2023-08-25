---
title: metric
description: OpenBB Terminal Function
---

# metric

Display metric of choice for different periods

### Usage

```python
metric [-m METRIC] [-r RISK_FREE_RATE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| metric | Set metric of choice | True | True | volatility, sharpe, sortino, maxdrawdown, rsquare, skew, kurtosis, gaintopain, trackerr, information, tail, commonsense, jensens, calmar, kelly, payoff, profitfactor |
| risk_free_rate | Set risk free rate for calculations. | 0 | True | None |

---
