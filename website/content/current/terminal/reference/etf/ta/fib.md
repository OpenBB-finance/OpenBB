---
title: fib
description: This page offers a comprehensive guide on how to calculate Fibonacci
  retracement levels, detailing its usage and the parameters required.
keywords:
- Fibonacci retracement levels
- Financial market analysis
- Trading tools
- Technical analysis
- period parameter
- start parameter
- end parameter
- calculation guide
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/ta/fib - Reference | OpenBB Terminal Docs" />

Calculates the fibonacci retracement levels

### Usage

```python
fib [-p PERIOD] [--start START] [--end END]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| period | Days to look back for retracement | 120 | True | None |
| start | Starting date to select | None | True | None |
| end | Ending date to select | None | True | None |

![fib](https://user-images.githubusercontent.com/46355364/154310727-81a1eab3-5565-42c7-8b47-4f80288dd700.png)

---
