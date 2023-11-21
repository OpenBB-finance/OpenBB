---
title: fib
description: This page contains details on how to calculate the Fibonacci retracement
  levels using specified parameters. Learn about proper usage, accepted parameters,
  and view a visual representation.
keywords:
- Fibonacci retracement levels
- fib function
- parameters
- Fibonacci trading
- trading strategies
- stock analysis
- trading charts
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/ta/fib - Reference | OpenBB Terminal Docs" />

Calculates the fibonacci retracement levels

### Usage

```python
fib [-p PERIOD] [--start START] [--end END]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| period | Days to look back for retracement | 120 | True | range(1, 960) |
| start | Starting date to select | None | True | None |
| end | Ending date to select | None | True | None |

![fib](https://user-images.githubusercontent.com/46355364/154310727-81a1eab3-5565-42c7-8b47-4f80288dd700.png)

---
