---
title: es
description: OpenBB Terminal Function
---

# es

Provides Expected Shortfall (short: ES) of the selected stock.

### Usage

```python
usage: es [-m] [-d {laplace,student_t,logistic,normal}] [-p PERCENTILE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| use_mean | If one should use the mean of the stocks return | False | True | None |
| distributions | Distribution used for the calculations | normal | True | laplace, student_t, logistic, normal |
| percentile | Percentile for calculations, i.e. input 99.9 equals a 99.9 Percent Expected Shortfall | 99.9 | True | None |
---

