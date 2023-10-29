---
title: summary
description: The page provides a detailed guide on how to display a summary of portfolio
  vs benchmark. It explains the usage, parameters, and choices available.
keywords:
- summary
- portfolio
- benchmark
- Usage
- parameters
- period
- risk_free_rate
- calculations
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio/summary - Reference | OpenBB Terminal Docs" />

Display summary of portfolio vs benchmark

### Usage

```python
summary [-p PERIOD] [-r RISK_FREE_RATE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| period | The file to be loaded | all | True | mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all |
| risk_free_rate | Set risk free rate for calculations. | 0 | True | None |

---
