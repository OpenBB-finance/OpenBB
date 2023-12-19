---
title: decompose
description: Learn how to decompose time series using Additive and Multiplicative
  models on a marketing website. Includes usage instructions and parameters.
keywords:
- Decompose time series
- Additive Time Series
- Multiplicative Time Series
- Level
- CyclicTrend
- Residual
- Seasonality
- Parameters
- Usage
- Marketing
- Stocks
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/qa/decompose - Reference | OpenBB Terminal Docs" />

Decompose time series as: - Additive Time Series = Level + CyclicTrend + Residual + Seasonality - Multiplicative Time Series = Level * CyclicTrend * Residual * Seasonality

### Usage

```python
decompose [-m]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| multiplicative | decompose using multiplicative model instead of additive | False | True | None |


---

## Examples

```python
2022 Feb 16, 11:06 (🦋) /stocks/qa/ $ decompose

Time-Series Level is 2660.84
Strength of Trend: 0.0000
Strength of Seasonality: 0.0032
```
![decompose](https://user-images.githubusercontent.com/46355364/154306626-1c5ad11e-a2e9-4107-9aec-5cf18da5358e.png)

---
