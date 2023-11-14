---
title: skew
description: The skew page describes skewness as a measure of asymmetry or distortion
  of a symmetric distribution, such as a normal distribution. Skewness measures the
  deviation of a random variable from a symmetric distribution. The page also details
  the usage and parameters of the 'skew' function.
keywords:
- skew
- asymmetry
- symmetric distribution
- normal distribution
- deviation
- n_window parameter
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/qa/skew - Reference | OpenBB Terminal Docs" />

Skewness is a measure of asymmetry or distortion of symmetric distribution. It measures the deviation of the given distribution of a random variable from a symmetric distribution, such as normal distribution. A normal distribution is without any skewness, as it is symmetrical on both sides. Hence, a curve is regarded as skewed if it is shifted towards the right or the left.

### Usage

```python
skew [-w N_WINDOW]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_window | window length | 14 | True | None |

![skew](https://user-images.githubusercontent.com/46355364/154308298-7528be2a-05f5-44b8-a479-d4716b2a6c6e.png)

---
