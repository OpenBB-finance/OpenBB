---
title: es
description: OpenBB Terminal Function
---

# es

Provides Expected Shortfall (short: ES) of the selected portfolio.

### Usage

```python
usage: es [-m] [-d DIST] [-p PERCENTILE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| use_mean | If one should use the mean of the portfolios return | True | True | None |
| distribution | Distribution used for the calculations | normal | True | laplace, student_t, logistic, normal |
| percentile | Percentile used for ES calculations, for example input 99.9 equals a 99.9 Percent Expected Shortfall | 99.9 | True | None |
---

