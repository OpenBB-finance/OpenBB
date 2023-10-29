---
title: normality
description: This page on the marketing website provides details on the 'normality'
  function including its usage, parameters, and examples. It is particularly centered
  around running normality tests in Python.
keywords:
- Normality command
- Normality Statistics
- Kurtosis
- Skewness
- Jarque-Bera
- Shapiro-Wilk
- Kolmogorov-Smirnov
- parameters
- examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy/qa/normality - Reference | OpenBB Terminal Docs" />

Normality tests

### Usage

```python
normality
```

---

## Parameters

This command has no parameters



---

## Examples

```python
2022 Feb 16, 11:11 (🦋) /stocks/qa/ $ normality
            Normality Statistics
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┓
┃                    ┃ Statistic ┃ p-value ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━┩
│ Kurtosis           │ 10.2422   │ 0.0000  │
├────────────────────┼───────────┼─────────┤
│ Skewness           │ -0.2238   │ 0.8229  │
├────────────────────┼───────────┼─────────┤
│ Jarque-Bera        │ 1155.1958 │ 0.0000  │
├────────────────────┼───────────┼─────────┤
│ Shapiro-Wilk       │ 0.9265    │ 0.0000  │
├────────────────────┼───────────┼─────────┤
│ Kolmogorov-Smirnov │ 0.4680    │ 0.0000  │
└────────────────────┴───────────┴─────────┘
```
---
