---
title: rsort
description: The rsort page provides users with a guide on how to use the rsort function
  to compare their Sortino portfolio against a set benchmark. This function takes
  into consideration the rolling window period and the risk-free rate for calculations.
  Ideal for financial calculations relates to risk and portfolio management.
keywords:
- rsort
- Sortino portfolio
- benchmarking
- rolling window period
- risk free rate
- financial calculations
- portfolio management
- risk management
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="rsort - Portfolio - Reference | OpenBB Terminal Docs" />

# rsort

Show rolling sortino portfolio vs benchmark

### Usage

```python
rsort [-p PERIOD] [-r RISK_FREE_RATE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| period | Period to apply rolling window | 1y | True | mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all |
| risk_free_rate | Set risk free rate for calculations. | 0 | True | None |

---
