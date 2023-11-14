---
title: ema
description: Learn how to use the EMA strategy, where stock is bought when the price
  is equivalent to EMA(l). Parameters such as EMA period, spy hold comparison, and
  buy and hold comparison are covered extensively.
keywords:
- EMA Strategy
- Price EMA
- Stock Buying
- EMA Period
- Spy Hold Comparison
- Buy and Hold Comparison
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/backtesting/ema - Reference | OpenBB Terminal Docs" />

Strategy where stock is bought when Price  EMA(l)

### Usage

```python
ema [-l LENGTH] [--spy] [--no_bench]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| length | EMA period to consider | 20 | True | None |
| spy | Flag to add spy hold comparison | False | True | None |
| no_bench | Flag to not show buy and hold comparison | False | True | None |

---
