---
title: kurtosis
description: This page offers comprehensive information on kurtosis - a measure of
  the 'tailedness' of a probability distribution of a real-valued random variable.
  Learn about its different measures and how to estimate it from a sample. Try it
  out with our Python usage guide.
keywords:
- kurtosis
- probability distribution
- real-valued random variable
- shape of distribution
- theoretical distribution
- sample estimation
- python usage guide
- n_window parameter
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy/qa/kurtosis - Reference | OpenBB Terminal Docs" />

Kurtosis is a measure of the "tailedness" of the probability distribution of a real-valued random variable. Like skewness, kurtosis describes the shape of a probability distribution and there are different ways of quantifying it for a theoretical distribution and corresponding ways of estimating it from a sample from a population. Different measures of kurtosis may have different interpretations.

### Usage

```python
kurtosis [-w N_WINDOW]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_window | window length | 14 | True | None |

![kurtosis](https://user-images.githubusercontent.com/46355364/154307174-68671146-9551-4c2f-a179-db1d4b20b992.png)

---
