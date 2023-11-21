---
title: normality
description: The page provides usage details for the command 'normality' which executes
  normality tests in python, includes parameters and examples showcasing normality
  statistics like Kurtosis, Skewness, Jarque-Bera, Shapiro-Wilk, and Kolmogorov-Smirnov.
keywords:
- normality tests
- kurtosis
- skewness
- Jarque-Bera
- Shapiro-Wilk
- Kolmogorov-Smirnov
- statistics
- p-value
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex/qa/normality - Reference | OpenBB Terminal Docs" />

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
