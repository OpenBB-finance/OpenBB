---
title: kurtosis
description: A deeper look into Kurtosis, a measure of probability distribution of
  a real-valued random variable. The page also demonstrates how to use it with python,
  especially setting the window length (n_window).
keywords:
- Kurtosis
- probability distribution
- real-valued random variable
- skewness
- theoretical distribution
- n_window
- window length
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/qa/kurtosis - Reference | OpenBB Terminal Docs" />

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
