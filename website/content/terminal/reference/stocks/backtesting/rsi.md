---
title: rsi
description: Understanding the rsi strategy, which buys stock when it's less than
  a threshold and shorts when it exceeds a threshold. Learn the usage, parameters,
  and options involved in this strategy.
keywords:
- rsi
- stock market strategy
- short sell
- rsi calculation
- buy and hold comparison
- spy hold comparison
- rsi level
- periods for calculation
- threshold for buying and shorting stock
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/backtesting/rsi - Reference | OpenBB Terminal Docs" />

Strategy that buys when the stock is less than a threshold and shorts when it exceeds a threshold.

### Usage

```python
rsi [-p PERIODS] [-u HIGH] [-l LOW] [--spy] [--no_bench] [--no_short]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| periods | Number of periods for RSI calculation | 14 | True | None |
| high | High (upper) RSI Level | 70 | True | None |
| low | Low RSI Level | 30 | True | None |
| spy | Flag to add spy hold comparison | False | True | None |
| no_bench | Flag to not show buy and hold comparison | False | True | None |
| shortable | Flag that disables the short sell | True | True | None |

---
