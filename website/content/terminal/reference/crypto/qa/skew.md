---
title: skew
description: The 'skew' documentation page explains how this concept can be utilized
  to measure asymmetry or distortion of a symmetric distribution, also describing
  usage and parameters in Python. It provides insights into how skewness measures
  deviation from a normal distribution, depicting either a right or left shift. Comprehensive
  visual aids are also given for clarification of the skewness concept.
keywords:
- skew
- asymmetry measurement
- distortion
- symmetric distribution
- normal distribution
- skewness
- random variable distribution
- distribution deviation
- right-skewed
- left-skew
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/qa/skew - Reference | OpenBB Terminal Docs" />

Skewness is a measure of asymmetry or distortion of symmetric distribution. It measures the deviation of the given distribution of a random variable from a symmetric distribution, such as normal distribution. A normal distribution is without any skewness, as it is symmetrical on both sides. Hence, a curve is regarded as skewed if it is shifted towards the right or the left.

### Usage

```python
skew [-w N_WINDOW]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_window | window length | 14 | True | range(5, 100) |

![skew](https://user-images.githubusercontent.com/46355364/154308298-7528be2a-05f5-44b8-a479-d4716b2a6c6e.png)

---
