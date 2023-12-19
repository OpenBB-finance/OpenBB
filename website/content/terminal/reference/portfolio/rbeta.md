---
title: rbeta
description: This page provides a detailed guide on the use of the 'rbeta' function
  to show rolling beta of a portfolio versus a benchmark over different time periods.
  It covers the available periods and how to use them.
keywords:
- rbeta
- rolling beta
- portfolio vs benchmark
- portfolio period
- rolling window
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio/rbeta - Reference | OpenBB Terminal Docs" />

Show rolling beta portfolio vs benchmark

### Usage

```python
rbeta [-p PERIOD]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| period | Period to apply rolling window | 1y | True | mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all |

---
