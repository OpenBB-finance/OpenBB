---
title: quantile
description: This page provides insights into the concept of 'Quantile' and how it's
  used for dividing a distribution. It includes parameter details such as n_window
  and f_quantile and usage information with Python.
keywords:
- quantile
- distribution
- median
- n_window
- f_quantile
- observations
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/qa/quantile - Reference | OpenBB Terminal Docs" />

The quantiles are values which divide the distribution such that there is a given proportion of observations below the quantile. For example, the median is a quantile. The median is the central value of the distribution, such that half the points are less than or equal to it and half are greater than or equal to it. By default, q is set at 0.5, which effectively is median. Change q to get the desired quantile (0q1).

### Usage

```python
quantile [-w N_WINDOW] [-q F_QUANTILE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_window | window length | 14 | True | None |
| f_quantile | quantile | 0.5 | True | None |

![quantile](https://user-images.githubusercontent.com/46355364/154307976-868e98e1-5a30-43c7-92fc-f221d09c5bd2.png)

---
