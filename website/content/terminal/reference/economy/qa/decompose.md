---
title: decompose
description: This product documentation page discusses the decompose function in time
  series analysis. It explains additive and multiplicative time series and provides
  specific usage examples and parameter details.
keywords:
- Decompose function
- Additive time series
- Multiplicative time series
- Time series analysis
- Stocks
- Parameter details
- Usage examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy/qa/decompose - Reference | OpenBB Terminal Docs" />

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
