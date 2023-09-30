---
title: rsharpe
description: OpenBB Terminal Function
---

# rsharpe

Show rolling sharpe portfolio vs benchmark

### Usage

```python
rsharpe [-p PERIOD] [-r RISK_FREE_RATE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| period | Period to apply rolling window | 1y | True | mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all |
| risk_free_rate | Set risk free rate for calculations. | 0 | True | None |

---
