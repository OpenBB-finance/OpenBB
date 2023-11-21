---
title: rsort
description: Show rolling sortino portfolio vs benchmark
keywords:
- portfolio
- rsort
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio /rsort - Reference | OpenBB Terminal Docs" />

Show rolling sortino portfolio vs benchmark

### Usage

```python wordwrap
rsort [-p PERIOD] [-r RISK_FREE_RATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| period | -p  --period | Period to apply rolling window | 1y | True | mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all |
| risk_free_rate | -r  --rfr | Set risk free rate for calculations. | 0 | True | None |

---
