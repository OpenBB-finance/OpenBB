---
title: skew
description: Learn about the concept of skewness as a measure of asymmetry, its relevance
  in symmetric distribution and normal distribution, and the 'skew' command along
  with its parameters and usage.
keywords:
- skewness
- symmetric distribution
- asymmetry
- normal distribution
- distortion
- skew command
- command parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex/qa/skew - Reference | OpenBB Terminal Docs" />

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
