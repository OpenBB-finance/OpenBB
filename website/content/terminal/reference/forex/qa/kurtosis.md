---
title: kurtosis
description: This page discusses the concept of kurtosis. It provides detailed insights
  on its functioning, importance, and usage with the help of Python code.
keywords:
- kurtosis
- probability distribution
- tailedness
- real-valued random variable
- shape
- theoretical distribution
- population sample
- Python code
- parameters
- n_window
- window length
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex/qa/kurtosis - Reference | OpenBB Terminal Docs" />

Kurtosis is a measure of the "tailedness" of the probability distribution of a real-valued random variable. Like skewness, kurtosis describes the shape of a probability distribution and there are different ways of quantifying it for a theoretical distribution and corresponding ways of estimating it from a sample from a population. Different measures of kurtosis may have different interpretations.

### Usage

```python
kurtosis [-w N_WINDOW]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_window | window length | 14 | True | range(5, 100) |

![kurtosis](https://user-images.githubusercontent.com/46355364/154307174-68671146-9551-4c2f-a179-db1d4b20b992.png)

---
