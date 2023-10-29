---
title: rvol
description: Rvol page shows the rolling volatility portfolio versus benchmark. It
  is primarily used to analyse the market's volatility over different periods.
keywords:
- rvol
- rolling volatility
- portfolio
- benchmark
- market analysis
- volatility analysis
- time period
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio/rvol - Reference | OpenBB Terminal Docs" />

Show rolling volatility portfolio vs benchmark

### Usage

```python
rvol [-p PERIOD]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| period | Period to apply rolling window | 1y | True | mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all |

---
