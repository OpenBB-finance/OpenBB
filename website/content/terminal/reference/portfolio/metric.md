---
title: metric
description: This page provides detailed instructions on how to display a chosen metric
  for different periods. It discusses parameters such as volatility, sharpe, sortino,
  etc. and how to set the risk-free rate for calculations.
keywords:
- metric
- risk free rate
- volatility
- sharpe ratio
- sortino ratio
- max drawdown
- R square
- skew
- kurtosis
- gain to pain
- tracker
- information ratio
- tail ratio
- common sense ratio
- jensens alpha
- calmar ratio
- kelly criterion
- payoff ratio
- profit factor
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio/metric - Reference | OpenBB Terminal Docs" />

Display metric of choice for different periods

### Usage

```python
metric [-m METRIC] [-r RISK_FREE_RATE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| metric | Set metric of choice | True | True | volatility, sharpe, sortino, maxdrawdown, rsquare, skew, kurtosis, gaintopain, trackerr, information, tail, commonsense, jensens, calmar, kelly, payoff, profitfactor |
| risk_free_rate | Set risk free rate for calculations. | 0 | True | None |

---
