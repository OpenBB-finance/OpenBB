---
title: rsharpe
description: The page provides comprehensive instructions on how to use the 'rsharpe'
  function, which is a tool for comparing a portfolio against a benchmark. The function
  allows for customization based on the desired period and risk free rate.
keywords:
- rsharpe
- rolling sharpe portfolio
- benchmarking
- risk free rate
- portfolio period
- portfolio calculation
- financial tools
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio/rsharpe - Reference | OpenBB Terminal Docs" />

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
